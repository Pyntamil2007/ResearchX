import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_rbac_and_security():
    print("\n========================================================")
    print("STARTING TEST SUITE: ROLE-BASED ACCESS CONTROL & SECURITY")
    print("========================================================\n")

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("[PASS] 1. Backend server healthy.")

    import time
    from app.database.database import SessionLocal
    from app.models import User, PasswordResetToken

    admin_email = "admin.system@researchx.io"
    admin_pwd = "AdminSecurityPass@2026"

    # Register admin if not exists, or elevate to ADMIN in database
    res_reg_admin = client.post("/api/auth/register", json={
        "name": "System Administrator",
        "email": admin_email,
        "password": admin_pwd
    })

    db_session = SessionLocal()
    try:
        admin_user = db_session.query(User).filter(User.email == admin_email).first()
        if admin_user:
            admin_user.role = "ADMIN"
            db_session.commit()
    finally:
        db_session.close()

    # Re-login to get updated JWT with ADMIN role
    res_login_admin = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd})
    assert res_login_admin.status_code == 200
    admin_token = res_login_admin.json()["data"]["access_token"]
    assert res_login_admin.json()["data"]["user"]["role"] == "ADMIN"
    print(f"[PASS] 2. Admin account verified with ADMIN role: {admin_email}")

    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Register second user (Standard Researcher)
    user_email = "researcher.jane@harvard.edu"
    user_pwd = "JaneResearcherPass#2026"
    res_reg_user = client.post("/api/auth/register", json={
        "name": "Dr. Jane Doe",
        "email": user_email,
        "password": user_pwd
    })
    
    if res_reg_user.status_code == 200:
        user_token = res_reg_user.json()["data"]["access_token"]
        user_id = res_reg_user.json()["data"]["user"]["id"]
        print(f"[PASS] 3. Standard Researcher account created: {user_email} (Role: USER)")
    else:
        res_login_user = client.post("/api/auth/login", json={"email": user_email, "password": user_pwd})
        assert res_login_user.status_code == 200
        user_token = res_login_user.json()["data"]["access_token"]
        user_id = res_login_user.json()["data"]["user"]["id"]
        print(f"[PASS] 3. Standard Researcher account logged in: {user_email} (Role: USER)")

    user_headers = {"Authorization": f"Bearer {user_token}"}

    # 4. Admin Access to Admin APIs (Should SUCCEED 200)
    res_admin_stats = client.get("/api/dashboard/admin", headers=admin_headers)
    assert res_admin_stats.status_code == 200, f"Admin stats failed: {res_admin_stats.text}"
    print(f"[PASS] 4. Admin successfully retrieved system statistics.")

    res_admin_users = client.get("/api/users", headers=admin_headers)
    assert res_admin_users.status_code == 200, f"Admin users failed: {res_admin_users.text}"
    print(f"[PASS] 5. Admin successfully retrieved user roster ({len(res_admin_users.json()['data']['items'])} users).")

    res_admin_papers = client.get("/api/admin/papers", headers=admin_headers)
    assert res_admin_papers.status_code == 200, f"Admin papers failed: {res_admin_papers.text}"
    print(f"[PASS] 6. Admin successfully retrieved repository papers.")

    # 5. Standard Researcher Access to Admin APIs (Must FAIL 403 Forbidden)
    res_user_stats = client.get("/api/dashboard/admin", headers=user_headers)
    assert res_user_stats.status_code == 403, "Researcher must be forbidden from admin stats"
    print("[PASS] 7. Standard Researcher blocked from `/api/dashboard/admin` with 403 Forbidden.")

    res_user_users = client.get("/api/users", headers=user_headers)
    assert res_user_users.status_code == 403, "Researcher must be forbidden from user management"
    print("[PASS] 8. Standard Researcher blocked from `/api/users` with 403 Forbidden.")

    res_user_admin_papers = client.get("/api/admin/papers", headers=user_headers)
    assert res_user_admin_papers.status_code == 403, "Researcher must be forbidden from admin papers"
    print("[PASS] 9. Standard Researcher blocked from `/api/admin/papers` with 403 Forbidden.")

    # 6. Standard Researcher Access to User APIs (Should SUCCEED 200)
    res_user_own_papers = client.get("/api/papers", headers=user_headers)
    assert res_user_own_papers.status_code == 200, f"User papers failed: {res_user_own_papers.text}"
    print("[PASS] 10. Standard Researcher successfully retrieved their own research workspace.")

    res_user_history = client.get("/api/history", headers=user_headers)
    assert res_user_history.status_code == 200, f"User history failed: {res_user_history.text}"
    print("[PASS] 11. Standard Researcher successfully retrieved their analysis history.")

    # 7. Admin User Role Update & Status Management
    # Deactivate and re-activate user
    res_status_update = client.patch(f"/api/users/{user_id}/status", headers=admin_headers, json={"status": "inactive"})
    assert res_status_update.status_code == 200, f"Status update failed: {res_status_update.text}"
    print("[PASS] 12. Admin successfully updated user status to inactive.")

    # Inactive user login should fail with 403
    res_inactive_login = client.post("/api/auth/login", json={"email": user_email, "password": user_pwd})
    assert res_inactive_login.status_code == 403, f"Inactive login should return 403, got {res_inactive_login.status_code}"
    print("[PASS] 13. Deactivated user login rejected with 403 Forbidden.")

    # Re-activate user
    res_reactivate = client.patch(f"/api/users/{user_id}/status", headers=admin_headers, json={"status": "active"})
    assert res_reactivate.status_code == 200, f"Reactivate failed: {res_reactivate.text}"
    print("[PASS] 14. Admin successfully reactivated user account.")

    print("\n============================================================")
    print("SUCCESS: ALL ROLE-BASED ACCESS & SECURITY TESTS PASSED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_rbac_and_security()
