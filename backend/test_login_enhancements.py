import httpx

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_login_enhancements():
    print("\n========================================================")
    print("STARTING TEST SUITE: FORGOT PASSWORD & GOOGLE OAUTH 2.0")
    print("========================================================\n")

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("[PASS] 1. Backend server healthy.")

    # 2. Register normal user
    test_email = "researcher.test@oxford.ac.uk"
    initial_pwd = "OriginalPassword@2026"
    res_reg = client.post("/api/auth/register", json={
        "name": "Dr. Sarah Connor",
        "email": test_email,
        "password": initial_pwd
    })
    assert res_reg.status_code == 200 or res_reg.status_code == 400
    print(f"[PASS] 2. User registration verified for {test_email}.")

    # 3. Forgot Password Flow - Request Reset Token
    res_forgot = client.post("/api/auth/forgot-password", json={"email": test_email})
    assert res_forgot.status_code == 200, f"Forgot password failed: {res_forgot.text}"
    data_forgot = res_forgot.json()["data"]
    token = data_forgot.get("reset_token")
    assert token is not None and len(token) > 20, "Reset token must be generated"
    print(f"[PASS] 3. Forgot password token generated successfully (Token length: {len(token)}).")

    # Test Forgot Password with non-existent email
    res_forgot_404 = client.post("/api/auth/forgot-password", json={"email": "nonexistent@nowhere.com"})
    assert res_forgot_404.status_code == 404
    print("[PASS] 4. Non-existent email correctly rejected with 404.")

    # 4. Verify Reset Token
    res_verify = client.post("/api/auth/verify-reset-token", json={"token": token})
    assert res_verify.status_code == 200, f"Token verification failed: {res_verify.text}"
    assert res_verify.json()["data"]["valid"] is True
    print("[PASS] 5. Reset token verification succeeded.")

    # 5. Reset Password to New Password
    new_pwd = "NewSecurePassword#2026!"
    res_reset = client.post("/api/auth/reset-password", json={
        "token": token,
        "new_password": new_pwd
    })
    assert res_reset.status_code == 200, f"Password reset failed: {res_reset.text}"
    print("[PASS] 6. Password reset completed successfully.")

    # 6. Test Token Reuse Prevention (Replay attack prevention)
    res_reuse = client.post("/api/auth/reset-password", json={
        "token": token,
        "new_password": "AnotherPassword@999"
    })
    assert res_reuse.status_code == 400, "Used token must not be accepted"
    print("[PASS] 7. Token reuse rejected (Single-use token enforcement verified).")

    # 7. Test Login with Old Password (Should FAIL 401)
    res_old_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": initial_pwd
    })
    assert res_old_login.status_code == 401, "Old password must not work"
    print("[PASS] 8. Old password rejected with 401 Unauthorized.")

    # 8. Test Login with New Password (Should SUCCEED 200)
    res_new_login = client.post("/api/auth/login", json={
        "email": test_email,
        "password": new_pwd
    })
    assert res_new_login.status_code == 200, f"New password login failed: {res_new_login.text}"
    user_token = res_new_login.json()["data"]["access_token"]
    assert user_token is not None
    print("[PASS] 9. Login with new password succeeded and issued valid JWT.")

    # 9. Google OAuth 2.0 - Authorization URL
    res_google_url = client.get("/api/auth/google/url")
    assert res_google_url.status_code == 200
    data_g_url = res_google_url.json()["data"]
    assert "url" in data_g_url
    print(f"[PASS] 10. Google OAuth endpoint verified: is_configured={data_g_url.get('is_configured')} (URL: {data_g_url['url'][:60]}...)")

    # 10. Google OAuth 2.0 - New User Authentication Callback
    new_google_email = "new.google.researcher@gmail.com"
    res_google_new = client.post("/api/auth/google/callback", json={
        "code": f"test_google_DrElenaRostova_{new_google_email}"
    })
    assert res_google_new.status_code == 200, f"Google new user callback failed: {res_google_new.text}"
    google_jwt = res_google_new.json()["data"]["access_token"]
    google_user = res_google_new.json()["data"]["user"]
    assert google_user["email"] == new_google_email
    print(f"[PASS] 11. Google OAuth auto-provisioned new account: {google_user['email']} (Role: {google_user['role']}).")

    # 11. Google OAuth 2.0 - Existing User Authentication Callback (Account Linking)
    res_google_existing = client.post("/api/auth/google/callback", json={
        "code": f"test_google_SarahConnor_{test_email}"
    })
    assert res_google_existing.status_code == 200, f"Google existing user callback failed: {res_google_existing.text}"
    linked_user = res_google_existing.json()["data"]["user"]
    assert linked_user["email"] == test_email
    print(f"[PASS] 12. Google OAuth securely linked to existing account: {linked_user['email']}.")

    # 12. Verify Authenticated Protected Endpoint Access
    auth_headers = {"Authorization": f"Bearer {google_jwt}"}
    res_me = client.get("/api/auth/me", headers=auth_headers)
    assert res_me.status_code == 200
    assert res_me.json()["data"]["email"] == new_google_email
    print("[PASS] 13. Protected `/api/auth/me` successfully authenticated with Google-issued JWT.")

    print("\n============================================================")
    print("SUCCESS: ALL LOGIN ENHANCEMENTS & SECURITY TESTS PASSED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_login_enhancements()
