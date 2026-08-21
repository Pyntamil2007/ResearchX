import os
from pathlib import Path
import httpx
from PIL import Image, ImageDraw

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_admin_and_delete_account():
    print("\n========================================================")
    print("STARTING TEST SUITE: ADMIN ACCOUNT SETUP & ACCOUNT DELETION")
    print("========================================================\n")

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("[PASS] 1. Backend service is healthy.")

    # 2. Administrator Account Initialization: admin@researchx.com
    admin_email = "admin@researchx.com"
    admin_pwd = "AdminSecurePassword@2026"

    # Register admin@researchx.com or sync password
    res_reg_admin = client.post("/api/auth/register", json={
        "name": "System Administrator",
        "email": admin_email,
        "password": admin_pwd
    })

    if res_reg_admin.status_code != 200:
        # If already exists with another password, update password hash & role in DB
        from app.database.database import SessionLocal
        from app.models import User, PasswordResetToken
        from app.core.security import get_password_hash
        db_s = SessionLocal()
        try:
            u = db_s.query(User).filter(User.email == admin_email).first()
            if u:
                u.password_hash = get_password_hash(admin_pwd)
                u.role = "ADMIN"
                db_s.commit()
        finally:
            db_s.close()

        res_login_admin = client.post("/api/auth/login", json={"email": admin_email, "password": admin_pwd})
        assert res_login_admin.status_code == 200, f"Admin login failed: {res_login_admin.text}"
        data_admin = res_login_admin.json()["data"]
    else:
        data_admin = res_reg_admin.json()["data"]

    admin_token = data_admin["access_token"]
    admin_user = data_admin["user"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # Verify role explicitly stored as ADMIN
    assert admin_user["role"] == "ADMIN", f"Expected admin@researchx.com to have role ADMIN, got {admin_user['role']}"
    assert "password" not in admin_user and "password_hash" not in admin_user, "Passwords must never be exposed"
    print(f"[PASS] 2. Administrator account verified: {admin_email} (Role: {admin_user['role']})")

    # 3. Verify Admin Access to Admin APIs
    res_admin_users = client.get("/api/users", headers=admin_headers)
    assert res_admin_users.status_code == 200
    print(f"[PASS] 3. Admin successfully retrieved user roster ({len(res_admin_users.json()['data']['items'])} accounts).")

    res_admin_papers = client.get("/api/admin/papers", headers=admin_headers)
    assert res_admin_papers.status_code == 200
    print("[PASS] 4. Admin successfully accessed paper management.")

    # 4. Register a Standard Researcher Account
    normal_email = "researcher.deletion.test@mit.edu"
    normal_pwd = "ResearcherPass#2026"
    res_reg_user = client.post("/api/auth/register", json={
        "name": "Dr. Deletion Test",
        "email": normal_email,
        "password": normal_pwd
    })
    if res_reg_user.status_code != 200:
        res_login_user = client.post("/api/auth/login", json={"email": normal_email, "password": normal_pwd})
        assert res_login_user.status_code == 200
        data_user = res_login_user.json()["data"]
    else:
        data_user = res_reg_user.json()["data"]

    user_token = data_user["access_token"]
    user_id = data_user["user"]["id"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    assert data_user["user"]["role"] == "USER"
    print(f"[PASS] 5. Standard Researcher account verified: {normal_email} (Role: USER)")

    # 5. Verify Standard Researcher is blocked from Admin APIs (403 Forbidden)
    res_forbidden_users = client.get("/api/users", headers=user_headers)
    assert res_forbidden_users.status_code == 403
    print("[PASS] 6. Standard user forbidden from `/api/users` (403 Forbidden).")

    res_forbidden_admin_dash = client.get("/api/dashboard/admin", headers=user_headers)
    assert res_forbidden_admin_dash.status_code == 403
    print("[PASS] 7. Standard user forbidden from `/api/dashboard/admin` (403 Forbidden).")

    # 6. Upload a test paper for the normal user
    img_dir = Path("uploads")
    img_dir.mkdir(parents=True, exist_ok=True)
    sample_file_path = img_dir / "user_deletion_test_doc.png"

    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((40, 50), "Sample Research Doc for Deletion Test\nAuthors: Jane Researcher\nAbstract: Testing deletion.", fill=(0, 0, 0))
    img.save(sample_file_path)

    with open(sample_file_path, "rb") as f:
        upload_resp = client.post(
            "/api/papers/upload",
            headers=user_headers,
            files={"file": ("user_deletion_test_doc.png", f, "image/png")},
            data={"title": "Sample Research Doc for Deletion Test", "domain": "Data Science"}
        )
    assert upload_resp.status_code == 200, f"Paper upload failed: {upload_resp.text}"
    uploaded_paper_id = upload_resp.json()["data"]["id"]
    saved_disk_path = Path(upload_resp.json()["data"]["file_path"])
    assert saved_disk_path.exists(), "Uploaded file must exist on disk"
    print(f"[PASS] 8. Uploaded paper created on disk: {saved_disk_path.name}")

    # 7. Attempt Account Deletion with WRONG password (Must return 401)
    res_wrong_pwd = client.post("/api/users/me/delete", headers=user_headers, json={"password": "WrongPassword123"})
    assert res_wrong_pwd.status_code == 401, "Wrong password must be rejected with 401"
    print("[PASS] 9. Deletion with wrong password correctly rejected (401 Unauthorized).")

    # 8. Attempt Self-Service Deletion on ADMIN Account (Must return 403 Forbidden)
    res_admin_self_delete = client.post("/api/users/me/delete", headers=admin_headers, json={"password": admin_pwd})
    assert res_admin_self_delete.status_code == 403, "Admin self-deletion must be blocked with 403"
    print("[PASS] 10. Admin account protection verified (Self-service deletion blocked with 403).")

    # 9. Perform Account Deletion with CORRECT password
    res_delete_success = client.post("/api/users/me/delete", headers=user_headers, json={"password": normal_pwd})
    assert res_delete_success.status_code == 200, f"Account deletion failed: {res_delete_success.text}"
    print(f"[PASS] 11. Account deletion succeeded: {res_delete_success.json()['message']}")

    # 10. Verify Data & Disk Purge:
    # A. Physical file removed
    assert not saved_disk_path.exists(), f"Uploaded file {saved_disk_path} should be deleted from disk"
    print("[PASS] 12. Uploaded research files purged from disk storage.")

    # B. User session invalidated
    res_me_deleted = client.get("/api/auth/me", headers=user_headers)
    assert res_me_deleted.status_code == 401, "Deleted user token must no longer be valid"
    print("[PASS] 13. Deleted user session successfully invalidated (401 Unauthorized).")

    # C. Login with deleted user fails
    res_login_deleted = client.post("/api/auth/login", json={"email": normal_email, "password": normal_pwd})
    assert res_login_deleted.status_code == 401, "Deleted user login must fail"
    print("[PASS] 14. Deleted user cannot log in (Account removed from SQLite).")

    print("\n============================================================")
    print("SUCCESS: ALL ADMIN & ACCOUNT DELETION TESTS PASSED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_admin_and_delete_account()
