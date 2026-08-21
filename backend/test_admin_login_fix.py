import httpx
from app.core.config import settings

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_admin_login_flow():
    print("\n========================================================")
    print("STARTING TEST SUITE: ADMINISTRATOR LOGIN & ROLE VERIFICATION")
    print("========================================================\n")

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("[PASS] 1. Backend service is healthy.")

    # 2. Test Login with wrong password -> Rejected with 401
    res_wrong = client.post("/api/auth/login", json={
        "email": "admin@researchx.com",
        "password": "WrongPassword123"
    })
    assert res_wrong.status_code == 401, "Wrong password must be rejected with 401"
    print("[PASS] 2. Invalid password rejected with 401 Unauthorized.")

    # 3. Test Login with correct admin password (Admin@2026)
    admin_email = settings.ADMIN_EMAIL or "admin@researchx.com"
    admin_pass = settings.ADMIN_PASSWORD or "Admin@2026"
    res_login = client.post("/api/auth/login", json={
        "email": admin_email,
        "password": admin_pass
    })
    assert res_login.status_code == 200, f"Admin login failed: {res_login.text}"
    data = res_login.json()["data"]
    admin_token = data["access_token"]
    admin_user = data["user"]

    assert admin_user["email"] == "admin@researchx.com"
    assert admin_user["role"].upper() == "ADMIN", f"Expected role 'ADMIN', got {admin_user['role']}"
    assert "password" not in admin_user and "password_hash" not in admin_user
    print(f"[PASS] 3. Administrator login succeeded: {admin_user['email']} (Role: {admin_user['role']}).")

    # 4. Test Administrator Dashboard API access with admin JWT
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    res_dash = client.get("/api/dashboard/admin", headers=admin_headers)
    assert res_dash.status_code == 200, f"Admin dashboard access failed: {res_dash.text}"
    dash_data = res_dash.json()["data"]
    assert "total_users" in dash_data
    print(f"[PASS] 4. Administrator successfully accessed Administrator Dashboard API (Total Users: {dash_data.get('total_users')}).")

    # 5. Test Admin accessing user roster
    res_users = client.get("/api/users", headers=admin_headers)
    assert res_users.status_code == 200
    users_list = res_users.json()["data"]["items"]
    assert len(users_list) > 0
    print(f"[PASS] 5. Administrator successfully accessed User Management API ({len(users_list)} users listed).")

    # 6. Verify Normal User login routes to User Dashboard and is forbidden from Admin API
    # Register/login normal user
    res_user_login = client.post("/api/auth/login", json={
        "email": "priya@gmail.com",
        "password": "Password#123"
    })
    if res_user_login.status_code != 200:
        # Create a fresh normal user
        res_user_reg = client.post("/api/auth/register", json={
            "name": "Normal Researcher",
            "email": "researcher.regular@lab.edu",
            "password": "RegularPass@2026"
        })
        user_token = res_user_reg.json()["data"]["access_token"]
        user_obj = res_user_reg.json()["data"]["user"]
    else:
        user_token = res_user_login.json()["data"]["access_token"]
        user_obj = res_user_login.json()["data"]["user"]

    assert user_obj["role"].upper() == "USER"
    user_headers = {"Authorization": f"Bearer {user_token}"}

    # Normal user accessing admin dashboard -> 403 Forbidden
    res_user_admin_access = client.get("/api/dashboard/admin", headers=user_headers)
    assert res_user_admin_access.status_code == 403, "Normal user must be forbidden from admin dashboard"
    
    # Normal user accessing user dashboard -> 200 OK
    res_user_dash = client.get("/api/dashboard/user", headers=user_headers)
    assert res_user_dash.status_code == 200, "Normal user successfully accesses user dashboard"
    print(f"[PASS] 6. Normal User verified (Role: {user_obj['role']}) -> Accesses User Dashboard, strictly blocked from Admin Dashboard (403 Forbidden).")

    print("\n============================================================")
    print("SUCCESS: ALL ADMINISTRATOR LOGIN & RBAC TESTS PASSED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_admin_login_flow()
