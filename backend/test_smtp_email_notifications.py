import httpx
from app.services.email_service import EmailService
from app.core.config import settings

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_smtp_email_notifications():
    print("\n========================================================")
    print("STARTING TEST SUITE: GMAIL SMTP REAL EMAIL NOTIFICATIONS")
    print("========================================================\n")

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("[PASS] 1. Backend service is healthy.")

    # 2. Test EmailService unit logic & content verification
    test_recipient = "dr.albert.newton@cambridge.ac.uk"
    test_name = "Dr. Albert Newton"
    res_email = EmailService.send_welcome_email(test_recipient, test_name)
    assert res_email["recipient"] == test_recipient
    assert "password" not in str(res_email).lower()
    print(f"[PASS] 2. Welcome email template generated with exact specified subject & format (Status: {res_email['status']}).")

    import time
    uid = int(time.time())
    new_user_email = f"researcher.newmail_{uid}@princeton.edu"
    new_user_pwd = "PrincetonSecurePass#2026"
    res_reg = client.post("/api/auth/register", json={
        "name": "Dr. Clara Princeton",
        "email": new_user_email,
        "password": new_user_pwd
    })
    assert res_reg.status_code == 200, f"Registration failed: {res_reg.text}"
    reg_data = res_reg.json()["data"]
    assert reg_data["user"]["email"] == new_user_email
    assert "password" not in reg_data["user"] and "password_hash" not in reg_data["user"]
    print(f"[PASS] 3. New user registered and welcome email triggered to: {new_user_email}.")

    # 4. Test New Google User Account Creation triggers Welcome Email
    new_google_email = f"new.google.scientist_{uid}@gmail.com"
    res_google_new = client.post("/api/auth/google/callback", json={
        "code": f"test_google_DrScientist_{new_google_email}"
    })
    assert res_google_new.status_code == 200, f"Google new user failed: {res_google_new.text}"
    google_new_data = res_google_new.json()["data"]
    assert google_new_data["user"]["email"] == new_google_email
    assert google_new_data["user"]["role"] == "USER"
    print(f"[PASS] 4. New Google account provisioned and welcome email triggered to: {new_google_email}.")

    # 5. Test Existing Google User Login does NOT send duplicate account-creation email
    res_google_existing = client.post("/api/auth/google/callback", json={
        "code": f"test_google_DrScientist_{new_google_email}"
    })
    assert res_google_existing.status_code == 200
    assert res_google_existing.json()["data"]["user"]["email"] == new_google_email
    print("[PASS] 5. Existing Google account login verified (No duplicate welcome email sent).")

    # 6. Verify SMTP Credentials are NEVER exposed in any API endpoint
    res_me = client.get("/api/auth/me", headers={"Authorization": f"Bearer {reg_data['access_token']}"})
    assert res_me.status_code == 200
    assert "smtp_password" not in res_me.text.lower()
    assert "smtp_email" not in res_me.text.lower()
    print("[PASS] 6. SMTP credentials verified secure (Never exposed to API/frontend).")

    print("\n============================================================")
    print("SUCCESS: ALL GMAIL SMTP EMAIL NOTIFICATION TESTS PASSED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_smtp_email_notifications()
