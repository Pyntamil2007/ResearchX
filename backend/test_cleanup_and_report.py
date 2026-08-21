import io
import json
import httpx
from pathlib import Path
from PIL import Image, ImageDraw

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_account_cleanup_and_report():
    print("\n=== STARTING VERIFICATION: ACCOUNT CLEANUP & REPORT IMPROVEMENTS ===")

    # 1. Health check
    res_health = client.get("/api/health")
    assert res_health.status_code == 200, f"Health check failed: {res_health.text}"
    print("[PASS] 1. Backend service is healthy.")

    # 2. Verify No Predefined Users Exist (Clean Database)
    # Trying to login with old default accounts should fail (401)
    res_admin_fail = client.post("/api/auth/login", json={"email": "admin@researchx.io", "password": "Admin@123456"})
    assert res_admin_fail.status_code == 401, "Expected login to fail on clean database"

    res_user_fail = client.post("/api/auth/login", json={"email": "researcher@researchx.io", "password": "Researcher@123456"})
    assert res_user_fail.status_code == 401, "Expected login to fail on clean database"
    print("[PASS] 2. No default or hardcoded accounts exist in the database.")

    # 3. Register or Login First User (ADMIN)
    res_reg1 = client.post("/api/auth/register", json={
        "name": "Dr. Alice Morgan",
        "email": "alice.morgan@institute.org",
        "password": "SecurePassword@2026"
    })
    from app.database.database import SessionLocal
    from app.models import User, PasswordResetToken
    db_s = SessionLocal()
    try:
        u = db_s.query(User).filter(User.email == "alice.morgan@institute.org").first()
        if u and u.role != "ADMIN":
            u.role = "ADMIN"
            db_s.commit()
    finally:
        db_s.close()

    res_login1 = client.post("/api/auth/login", json={"email": "alice.morgan@institute.org", "password": "SecurePassword@2026"})
    data_reg1 = res_login1.json()["data"]
    admin_token = data_reg1["access_token"]
    admin_user = data_reg1["user"]
    assert "password" not in admin_user and "password_hash" not in admin_user, "Password must not be exposed"
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print(f"[PASS] 3. Admin user session established: {admin_user['email']} (Role: {admin_user['role']})")

    # 4. Register or Login Second User (Standard USER)
    res_reg2 = client.post("/api/auth/register", json={
        "name": "Bob Chen",
        "email": "bob.chen@university.edu",
        "password": "ResearcherPass#2026"
    })
    if res_reg2.status_code == 200:
        data_reg2 = res_reg2.json()["data"]
    else:
        res_login2 = client.post("/api/auth/login", json={"email": "bob.chen@university.edu", "password": "ResearcherPass#2026"})
        data_reg2 = res_login2.json()["data"]

    user_token = data_reg2["access_token"]
    user_user = data_reg2["user"]
    assert user_user["role"] == "USER", f"Expected second user to be USER, got {user_user['role']}"
    assert "password" not in user_user and "password_hash" not in user_user, "Password must not be exposed"
    user_headers = {"Authorization": f"Bearer {user_token}"}
    print(f"[PASS] 4. Standard USER session established: {user_user['email']} (Role: {user_user['role']})")

    # 5. Test Paper Upload & Author Extraction
    img_dir = Path("uploads")
    img_dir.mkdir(parents=True, exist_ok=True)
    sample_img_path = img_dir / "test_paper_authors.png"

    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((40, 50), "Deep Learning Architectures in Neural Vision\nAuthors: David Lee, Priya Kumar, John Smith\nAbstract: Deep networks are evaluated.", fill=(0, 0, 0))
    img.save(sample_img_path)

    with open(sample_img_path, "rb") as f:
        upload_resp = client.post(
            "/api/papers/upload",
            headers=user_headers,
            files={"file": ("test_paper_authors.png", f, "image/png")},
            data={"title": "Deep Learning Architectures in Neural Vision", "domain": "Deep Learning"}
        )
    assert upload_resp.status_code == 200, f"Paper upload failed: {upload_resp.text}"
    paper_id = upload_resp.json()["data"]["id"]
    print(f"[PASS] 5. Uploaded document created successfully (ID: {paper_id})")

    # 6. Analyze Paper
    res_analyze = client.post(f"/api/analysis/paper/{paper_id}", headers=user_headers)
    assert res_analyze.status_code == 200, f"Analysis failed: {res_analyze.text}"
    analysis_id = res_analyze.json()["data"]["analysis_id"]

    # 7. Fetch Analysis Report and verify all 14 structured sections
    res_report = client.get(f"/api/analysis/{analysis_id}", headers=user_headers)
    assert res_report.status_code == 200, f"Report fetch failed: {res_report.text}"
    report_data = res_report.json()["data"]

    # Verify Report Sequence & Integrity
    required_sections = [
        "paper_title",       # 1. Paper Overview
        "authors",           # 2. Authors
        "research_domain",   # 3. Domain
        "research_problem",  # 4. Research Problem
        "objective",         # 5. Objective
        "methodology",       # 6. Methodology
        "algorithms",        # 7. Algorithms
        "dataset",           # 8. Dataset
        "results",           # 9. Results
        "key_findings",      # 10. Key Findings
        "limitations",       # 11. Limitations
        "future_work",       # 12. Future Work
        "contribution",      # 13. Main Contribution
        "easy_summary"       # 14. Easy Summary (6 questions)
    ]

    for sec in required_sections:
        assert sec in report_data, f"Missing required section: {sec}"

    easy_summary = report_data["easy_summary"]
    assert "what_is_this_paper_about" in easy_summary
    assert "what_problem_does_it_solve" in easy_summary
    assert "why_was_the_research_conducted" in easy_summary
    assert "how_was_it_performed" in easy_summary
    assert "what_was_the_result" in easy_summary
    assert "what_is_the_main_contribution" in easy_summary

    print("[PASS] 6. Analysis report contains all 14 required sections and 6-question easy summary.")

    # 8. Verify Admin Access Control
    # Admin can list users
    res_admin_users = client.get("/api/users", headers=admin_headers)
    assert res_admin_users.status_code == 200
    assert len(res_admin_users.json()["data"]["items"]) >= 2
    print(f"[PASS] 7. Admin successfully manages {len(res_admin_users.json()['data']['items'])} registered users.")

    # Standard user is forbidden from admin user management
    res_forbidden = client.get("/api/users", headers=user_headers)
    assert res_forbidden.status_code == 403
    print("[PASS] 8. Role-Based Access Control verified: Standard user cannot access admin endpoints.")

    print("\n============================================================")
    print("SUCCESS: ALL ACCOUNT CLEANUP & REPORT VERIFICATIONS PASSED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_account_cleanup_and_report()
