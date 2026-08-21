import httpx
from app.core.config import settings

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_google_oauth_flow():
    print("\n========================================================")
    print("STARTING TEST SUITE: GOOGLE OAUTH SPECIFIC BEHAVIOR & SECURITY")
    print("========================================================\n")

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("[PASS] 1. Backend service is healthy.")

    # 2. Test GET /api/auth/google/url endpoint
    res_url = client.get("/api/auth/google/url")
    assert res_url.status_code == 200, f"Failed to get Google auth URL: {res_url.text}"
    url_data = res_url.json()["data"]
    assert "url" in url_data
    assert "GOOGLE_CLIENT_SECRET=" not in res_url.text
    assert url_data.get("client_secret") is None
    print(f"[PASS] 2. Google auth URL endpoint verified (is_configured={url_data.get('is_configured')}).")

    # 3. Test: New Google Email -> Creates new account with role = "USER"
    new_google_email = "dr.maria.garcia@berkeley.edu"
    res_new_user = client.post("/api/auth/google/callback", json={
        "code": f"test_google_DrMariaGarcia_{new_google_email}"
    })
    assert res_new_user.status_code == 200, f"Google new user callback failed: {res_new_user.text}"
    new_auth = res_new_user.json()["data"]
    new_jwt = new_auth["access_token"]
    new_user_obj = new_auth["user"]

    assert new_user_obj["email"] == new_google_email
    assert new_user_obj["role"] == "USER", f"Expected new Google user role to be 'USER', got {new_user_obj['role']}"
    assert "password" not in new_user_obj and "password_hash" not in new_user_obj
    print(f"[PASS] 3. New Google email created account with role = 'USER': {new_user_obj['email']} -> Redirects to User Dashboard.")

    # 4. Test: New Google Email containing 'admin' (e.g. administrator.test@gmail.com) -> MUST still be 'USER' role
    admin_named_email = "administrator.smith@gmail.com"
    res_admin_named = client.post("/api/auth/google/callback", json={
        "code": f"test_google_AdminSmith_{admin_named_email}"
    })
    assert res_admin_named.status_code == 200
    admin_named_obj = res_admin_named.json()["data"]["user"]
    assert admin_named_obj["role"] == "USER", f"Expected 'USER' role even if email contains 'admin', got {admin_named_obj['role']}"
    print(f"[PASS] 4. Email containing 'admin' in name created as role = 'USER': {admin_named_obj['email']} (Security Check Passed).")

    # 5. Test: Existing Account with role = "ADMIN" -> Preserves "ADMIN" role
    # Create or ensure an existing ADMIN account
    existing_admin_email = "system.director@researchx.com"
    # Register/create admin
    res_reg_admin = client.post("/api/auth/register", json={
        "name": "System Director",
        "email": existing_admin_email,
        "password": "DirectorSecurePass@2026"
    })
    from app.database.database import SessionLocal
    from app.models import User
    db = SessionLocal()
    try:
        u = db.query(User).filter(User.email == existing_admin_email).first()
        if u:
            u.role = "ADMIN"
            db.commit()
    finally:
        db.close()

    # Now login with Google using this existing admin email
    res_google_admin = client.post("/api/auth/google/callback", json={
        "code": f"test_google_SystemDirector_{existing_admin_email}"
    })
    assert res_google_admin.status_code == 200
    google_admin_obj = res_google_admin.json()["data"]["user"]
    assert google_admin_obj["email"] == existing_admin_email
    assert google_admin_obj["role"] == "ADMIN", f"Expected existing ADMIN role to be preserved, got {google_admin_obj['role']}"
    print(f"[PASS] 5. Existing ADMIN account logged in via Google and preserved role = 'ADMIN': {google_admin_obj['email']} -> Redirects to Administrator Dashboard.")

    # 6. Test: Existing Account with role = "USER" -> Preserves "USER" role and no duplicate created
    # Login again with the user created in step 3
    db = SessionLocal()
    count_before = db.query(User).filter(User.email == new_google_email).count()
    db.close()
    assert count_before == 1

    res_login_again = client.post("/api/auth/google/callback", json={
        "code": f"test_google_DrMariaGarcia_{new_google_email}"
    })
    assert res_login_again.status_code == 200
    again_user_obj = res_login_again.json()["data"]["user"]
    assert again_user_obj["email"] == new_google_email
    assert again_user_obj["role"] == "USER"

    db = SessionLocal()
    count_after = db.query(User).filter(User.email == new_google_email).count()
    db.close()
    assert count_after == 1, "Duplicate account must NOT be created for existing Google email"
    print(f"[PASS] 6. Existing USER account logged in via Google without duplicate (Count: {count_after}) -> Redirects to User Dashboard.")

    # 7. Test: Authenticated JWT from Google User
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {res_login_again.json()['data']['access_token']}"})
    assert res_me.status_code == 200
    assert res_me.json()["data"]["email"] == new_google_email
    print("[PASS] 7. Google-issued JWT successfully authenticated with `/api/auth/me`.")

    print("\n============================================================")
    print("SUCCESS: ALL GOOGLE OAUTH FLOW & SECURITY TESTS PASSED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_google_oauth_flow()
