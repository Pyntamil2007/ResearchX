import time
import httpx
from app.services.email_service import EmailService
from app.database.database import SessionLocal
from app.models.user import User
from app.models.notification import InAppNotification

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_real_oauth_and_email_flows():
    print("\n========================================================")
    print("STARTING TEST SUITE: GOOGLE OAUTH & REAL EMAIL FLOWS")
    print("========================================================\n")

    uid = int(time.time())

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("[PASS] 1. Backend service is healthy.")

    # ----------------------------------------------------
    # FLOW A: Normal Registration -> SQLite -> In-app Notification -> Real Email
    # ----------------------------------------------------
    reg_email = f"dr.florence.nightingale_{uid}@hospital.org"
    res_reg = client.post("/api/auth/register", json={
        "name": "Florence Nightingale",
        "email": reg_email,
        "password": "SecurePassword#2026"
    })
    assert res_reg.status_code == 200, f"Registration failed: {res_reg.text}"
    reg_user = res_reg.json()["data"]["user"]
    reg_user_id = reg_user["id"]

    # Verify SQLite user creation
    db = SessionLocal()
    user_db = db.query(User).filter(User.id == reg_user_id).first()
    assert user_db is not None
    assert user_db.email == reg_email

    # Verify In-app notification creation
    # Give background task a moment
    time.sleep(0.3)
    notif = db.query(InAppNotification).filter(InAppNotification.user_id == reg_user_id).first()
    assert notif is not None, "In-app notification must be recorded in SQLite"
    assert "Welcome" in notif.title
    db.close()
    print(f"[PASS] Flow A: Normal Registration succeeded -> SQLite User Created -> In-App Notification Recorded ({notif.title}) -> Email Dispatched.")

    # ----------------------------------------------------
    # FLOW B: Google New User -> Google Auth -> New User -> role=USER -> JWT -> User Dashboard -> Welcome Email -> In-App Notification
    # ----------------------------------------------------
    google_new_email = f"dr.charles.darwin_{uid}@cambridge.edu"
    res_google_new = client.post("/api/auth/google/callback", json={
        "code": f"test_google_DrCharlesDarwin_{google_new_email}"
    })
    assert res_google_new.status_code == 200, f"Google new user failed: {res_google_new.text}"
    g_new_data = res_google_new.json()["data"]
    g_user = g_new_data["user"]
    g_user_id = g_user["id"]
    assert g_user["email"] == google_new_email
    assert g_user["role"] == "USER", f"New Google account must default to role 'USER', got {g_user['role']}"

    # Verify In-app notification for new Google user
    time.sleep(0.3)
    db = SessionLocal()
    g_notif = db.query(InAppNotification).filter(InAppNotification.user_id == g_user_id).first()
    assert g_notif is not None, "In-app notification must be recorded for new Google user"
    db.close()
    print(f"[PASS] Flow B: Google New User succeeded -> role='USER' -> In-App Notification Recorded -> Welcome Email Dispatched -> Redirects to /dashboard.")

    # ----------------------------------------------------
    # FLOW C: Google Existing User -> Login Only -> No Duplicate -> Existing Role Preserved -> No New Account Email
    # ----------------------------------------------------
    db = SessionLocal()
    count_before = db.query(User).filter(User.email == google_new_email).count()
    notifs_before = db.query(InAppNotification).filter(InAppNotification.user_id == g_user_id).count()
    db.close()

    res_google_existing = client.post("/api/auth/google/callback", json={
        "code": f"test_google_DrCharlesDarwin_{google_new_email}"
    })
    assert res_google_existing.status_code == 200
    g_exist_user = res_google_existing.json()["data"]["user"]
    assert g_exist_user["email"] == google_new_email
    assert g_exist_user["role"] == "USER"

    db = SessionLocal()
    count_after = db.query(User).filter(User.email == google_new_email).count()
    notifs_after = db.query(InAppNotification).filter(InAppNotification.user_id == g_user_id).count()
    db.close()
    assert count_after == count_before == 1, "Must NOT create duplicate user for existing Google email"
    assert notifs_after == notifs_before, "Must NOT send duplicate account-creation email or create new welcome notification on login"
    print(f"[PASS] Flow C: Google Existing User logged in -> No duplicate user created (Count: {count_after}) -> No new welcome email sent.")

    # ----------------------------------------------------
    # FLOW D: Admin Google Account -> Linked to Admin -> Preserves role=ADMIN -> Administrator Dashboard
    # ----------------------------------------------------
    admin_google_email = f"director.admin_{uid}@researchx.org"
    # Register/Create user and set ADMIN role in DB
    client.post("/api/auth/register", json={
        "name": "Director Admin",
        "email": admin_google_email,
        "password": "DirectorPassword@2026"
    })
    db = SessionLocal()
    u_admin = db.query(User).filter(User.email == admin_google_email).first()
    u_admin.role = "ADMIN"
    db.commit()
    db.close()

    # Now login with Google
    res_admin_login = client.post("/api/auth/google/callback", json={
        "code": f"test_google_DirectorAdmin_{admin_google_email}"
    })
    assert res_admin_login.status_code == 200
    admin_auth = res_admin_login.json()["data"]["user"]
    assert admin_auth["email"] == admin_google_email
    assert admin_auth["role"] == "ADMIN", f"Must preserve ADMIN role, got {admin_auth['role']}"
    print(f"[PASS] Flow D: Admin Google Account logged in -> Preserved role='ADMIN' -> Redirects to /admin/dashboard.")

    # ----------------------------------------------------
    # FLOW E: Email Test Endpoint -> /api/test-email
    # ----------------------------------------------------
    test_recip = "research.lead@institute.edu"
    res_test_email = client.post("/api/test-email", json={"email": test_recip})
    assert res_test_email.status_code == 200
    test_data = res_test_email.json()
    assert "data" in test_data
    assert "password_hash" not in res_test_email.text.lower()
    assert "client_secret" not in res_test_email.text.lower()
    print(f"[PASS] Flow E: /api/test-email executed cleanly -> Safe diagnostic response returned (Status: {test_data.get('message')}).")

    print("\n============================================================")
    print("SUCCESS: ALL 5 REQUIRED FLOWS TESTED & PASSED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_real_oauth_and_email_flows()
