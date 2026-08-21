import time
import httpx
from pathlib import Path

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_full_inapp_notifications_and_auth_cleanup():
    print("\n========================================================")
    print("STARTING TEST SUITE: IN-APP NOTIFICATIONS & AUTH CLEANUP")
    print("========================================================\n")

    uid = int(time.time() * 1000)

    # ----------------------------------------------------
    # 1. VERIFY GOOGLE OAUTH & TEST-EMAIL ENDPOINTS ARE REMOVED
    # ----------------------------------------------------
    res_g_url = client.get("/api/auth/google/url")
    assert res_g_url.status_code == 404, f"Google URL endpoint must be removed (404), got {res_g_url.status_code}"

    res_g_cb = client.post("/api/auth/google/callback", json={"code": "test"})
    assert res_g_cb.status_code == 404, f"Google callback endpoint must be removed (404), got {res_g_cb.status_code}"

    res_test_email = client.post("/api/auth/test-email", json={"recipient_email": "test@test.com"})
    assert res_test_email.status_code == 404, f"Test email endpoint must be removed (404), got {res_test_email.status_code}"

    print("[PASS] 1. Google OAuth endpoints & test-email endpoints are completely removed (404 Not Found).")

    # ----------------------------------------------------
    # 2. LOGIN AS ADMIN
    # ----------------------------------------------------
    admin_login = client.post("/api/auth/login", json={
        "email": "admin@researchx.com",
        "password": "Admin@2026"
    })
    assert admin_login.status_code == 200, f"Admin login failed: {admin_login.text}"
    admin_token = admin_login.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[PASS] 2. Administrator login successful.")

    # ----------------------------------------------------
    # 3. REGISTER NEW RESEARCHER USER
    # ----------------------------------------------------
    user_email = f"curie_{uid}@researchx.org"
    user_pwd = "CuriePassword@2026"
    user_name = f"Marie Curie {uid}"

    reg_res = client.post("/api/auth/register", json={
        "name": user_name,
        "email": user_email,
        "password": user_pwd
    })
    assert reg_res.status_code == 200, f"User registration failed: {reg_res.text}"
    user_token = reg_res.json()["data"]["access_token"]
    user_id = reg_res.json()["data"]["user"]["id"]
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Verify User In-App Notification: "Account created successfully"
    user_notifs_res = client.get("/api/notifications", headers=user_headers)
    assert user_notifs_res.status_code == 200
    user_notifs = user_notifs_res.json()["data"]
    assert user_notifs["unread_count"] >= 1
    assert any(n["title"] == "Account created successfully" for n in user_notifs["items"])
    print(f"[PASS] 3a. User received in-app notification: 'Account created successfully' (Unread count: {user_notifs['unread_count']}).")

    # Verify Admin In-App Notification: "New user registered"
    admin_notifs_res = client.get("/api/notifications", headers=admin_headers)
    assert admin_notifs_res.status_code == 200
    admin_notifs = admin_notifs_res.json()["data"]
    assert any(n["title"] == "New user registered" and user_name in n["message"] for n in admin_notifs["items"])
    print("[PASS] 3b. Admin received in-app notification: 'New user registered'.")

    # ----------------------------------------------------
    # 4. UPLOAD RESEARCH PAPER
    # ----------------------------------------------------
    pdf_path = Path("demo_papers/ResNet_Deep_Residual_Learning.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    up_res = client.post(
        "/api/papers/upload",
        data={"title": f"Residual Learning Study {uid}", "authors": "Marie Curie et al."},
        files={"file": (f"resnet_{uid}.pdf", pdf_bytes, "application/pdf")},
        headers=user_headers
    )
    assert up_res.status_code == 200, f"Paper upload failed: {up_res.text}"
    paper_id = up_res.json()["data"]["id"]

    # Verify User In-App Notification: "Research paper uploaded"
    user_notifs_2 = client.get("/api/notifications", headers=user_headers).json()["data"]
    assert any(n["title"] == "Research paper uploaded" for n in user_notifs_2["items"])
    print("[PASS] 4a. User received in-app notification: 'Research paper uploaded'.")

    # Verify Admin In-App Notification: "New research paper uploaded"
    admin_notifs_2 = client.get("/api/notifications", headers=admin_headers).json()["data"]
    assert any(n["title"] == "New research paper uploaded" for n in admin_notifs_2["items"])
    print("[PASS] 4b. Admin received in-app notification: 'New research paper uploaded'.")

    # ----------------------------------------------------
    # 5. TRIGGER AI/NLP ANALYSIS
    # ----------------------------------------------------
    an_res = client.post(f"/api/analysis/paper/{paper_id}", headers=user_headers)
    assert an_res.status_code == 200, f"Analysis failed: {an_res.text}"

    # Verify User In-App Notifications: "Analysis started", "Analysis completed", "Report generated"
    user_notifs_3 = client.get("/api/notifications", headers=user_headers).json()["data"]
    user_titles = [n["title"] for n in user_notifs_3["items"]]
    assert "Analysis started" in user_titles, "Must contain 'Analysis started'"
    assert "Analysis completed" in user_titles, "Must contain 'Analysis completed'"
    assert "Report generated" in user_titles, "Must contain 'Report generated'"
    print(f"[PASS] 5a. User received lifecycle notifications: 'Analysis started', 'Analysis completed', 'Report generated'.")

    # Verify Admin In-App Notification: "Analysis completed"
    admin_notifs_3 = client.get("/api/notifications", headers=admin_headers).json()["data"]
    assert any(n["title"] == "Analysis completed" for n in admin_notifs_3["items"])
    print("[PASS] 5b. Admin received in-app notification: 'Analysis completed'.")

    # ----------------------------------------------------
    # 6. TEST NOTIFICATION READ & CLEAR ACTIONS
    # ----------------------------------------------------
    first_notif = user_notifs_3["items"][0]
    first_notif_id = first_notif["id"]

    # Mark single notification as read
    patch_single = client.patch(f"/api/notifications/{first_notif_id}/read", headers=user_headers)
    assert patch_single.status_code == 200
    assert patch_single.json()["data"]["is_read"] is True
    print(f"[PASS] 6a. Single notification {first_notif_id} marked as read.")

    # Mark all notifications as read
    patch_all = client.patch("/api/notifications/read-all", headers=user_headers)
    assert patch_all.status_code == 200
    user_notifs_read = client.get("/api/notifications", headers=user_headers).json()["data"]
    assert user_notifs_read["unread_count"] == 0, f"All notifications must be read, unread={user_notifs_read['unread_count']}"
    print("[PASS] 6b. All notifications marked as read (Unread count = 0).")

    # Delete single notification
    del_single = client.delete(f"/api/notifications/{first_notif_id}", headers=user_headers)
    assert del_single.status_code == 200
    user_notifs_after_del = client.get("/api/notifications", headers=user_headers).json()["data"]
    assert not any(n["id"] == first_notif_id for n in user_notifs_after_del["items"])
    print(f"[PASS] 6c. Single notification {first_notif_id} successfully deleted.")

    # ----------------------------------------------------
    # 7. TEST PASSWORD CHANGE NOTIFICATION
    # ----------------------------------------------------
    # Reset password via forgot password flow
    forgot_res = client.post("/api/auth/forgot-password", json={"email": user_email})
    reset_tok = forgot_res.json()["data"]["reset_token"]
    reset_pwd_res = client.post("/api/auth/reset-password", json={"token": reset_tok, "new_password": "NewSecretPassword@2026"})
    assert reset_pwd_res.status_code == 200

    user_notifs_4 = client.get("/api/notifications", headers=user_headers).json()["data"]
    assert any(n["title"] == "Password changed" for n in user_notifs_4["items"])
    print("[PASS] 7. User received in-app notification: 'Password changed'.")

    # ----------------------------------------------------
    # 8. TEST USER ACCOUNT DELETION NOTIFICATION (ADMIN ALERT)
    # ----------------------------------------------------
    del_acc_res = client.post("/api/users/me/delete", json={"password": "NewSecretPassword@2026"}, headers=user_headers)
    assert del_acc_res.status_code == 200, f"Account deletion failed: {del_acc_res.text}"

    admin_notifs_4 = client.get("/api/notifications", headers=admin_headers).json()["data"]
    assert any(n["title"] == "User account deleted" and user_email in n["message"] for n in admin_notifs_4["items"])
    print("[PASS] 8. Admin received in-app notification: 'User account deleted'.")

    # ----------------------------------------------------
    # 9. USER PRIVACY & ROLE ISOLATION
    # ----------------------------------------------------
    # Verify that a user cannot see admin notifications or other users' notifications
    second_user_email = f"einstein_{uid}@researchx.org"
    reg_2 = client.post("/api/auth/register", json={
        "name": f"Albert Einstein {uid}",
        "email": second_user_email,
        "password": "AlbertPassword@2026"
    })
    token_2 = reg_2.json()["data"]["access_token"]
    user2_headers = {"Authorization": f"Bearer {token_2}"}

    user2_notifs = client.get("/api/notifications", headers=user2_headers).json()["data"]
    for n in user2_notifs["items"]:
        assert n["user_id"] == reg_2.json()["data"]["user"]["id"], "User must only see their own notifications!"

    print("[PASS] 9. Strict user privacy and role isolation verified.")

    print("\n============================================================")
    print("SUCCESS: IN-APP NOTIFICATIONS & AUTH CLEANUP 100% VERIFIED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_full_inapp_notifications_and_auth_cleanup()
