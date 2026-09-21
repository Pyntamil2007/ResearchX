import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def log_step(name):
    print(f"\n---> [TEST] {name}")

def log_ok(msg):
    print(f"     [PASS] {msg}")

def run_full_suite():
    print("=================================================================")
    print("      RESEARCHX - FULL SYSTEM & ARCHITECTURE VERIFICATION        ")
    print("=================================================================")

    # 1. Health & Status
    log_step("1. Checking Server Health")
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200 and res.json().get("status") == "healthy"
    log_ok("Backend health endpoint is operational")

    # 2. Authentication: Register New Researcher
    log_step("2. User Registration Workflow")
    test_user_email = f"curie_{int(time.time())}@research.org"
    res = requests.post(f"{BASE_URL}/auth/register", json={
        "name": "Dr. Marie Curie",
        "email": test_user_email,
        "password": "Password@123"
    })
    assert res.status_code == 200, f"Registration failed: {res.text}"
    curie_token = res.json()["data"]["access_token"]
    curie_headers = {"Authorization": f"Bearer {curie_token}"}
    log_ok(f"Registered new researcher '{test_user_email}' successfully")

    # 3. Authentication: Login Existing Researcher
    log_step("3. User Login Workflow")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": test_user_email,
        "password": "Password@123"
    })
    assert res.status_code == 200, f"Login failed: {res.text}"
    researcher_token = res.json()["data"]["access_token"]
    researcher_headers = {"Authorization": f"Bearer {researcher_token}"}
    log_ok("Registered researcher logged in successfully")

    # 4. Authentication: Login Admin
    log_step("4. Admin Login Workflow")
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@researchx.com",
        "password": "Admin@2026"
    })
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    log_ok("Default administrator logged in successfully")

    # 5. Role-Based Access Control (RBAC)
    log_step("5. Role-Based Access Control Security Checks")
    res = requests.get(f"{BASE_URL}/dashboard/admin", headers=researcher_headers)
    assert res.status_code == 403, f"Expected 403 Forbidden for researcher on admin route, got {res.status_code}"
    res = requests.get(f"{BASE_URL}/users", headers=researcher_headers)
    assert res.status_code == 403, f"Expected 403 Forbidden for researcher on users list, got {res.status_code}"
    log_ok("RBAC strictly enforced: Non-admins blocked from administrative routes")

    # 6. Admin User Management CRUD
    log_step("6. Admin User Management Operations (CRUD & Pagination)")
    # Create user
    res = requests.post(f"{BASE_URL}/users", headers=admin_headers, json={
        "name": "Dr. Ada Lovelace",
        "email": f"ada_{int(time.time())}@research.org",
        "password": "AdaPassword@123",
        "role": "USER",
        "status": "active"
    })
    assert res.status_code == 201, f"User creation failed: {res.text}"
    created_user_id = res.json()["data"]["id"]
    log_ok(f"Admin created user ID {created_user_id}")

    # Read user
    res = requests.get(f"{BASE_URL}/users/{created_user_id}", headers=admin_headers)
    assert res.status_code == 200
    log_ok("Admin retrieved user details")

    # Update user status (deactivate / activate)
    res = requests.patch(f"{BASE_URL}/users/{created_user_id}/status", headers=admin_headers, json={"status": "inactive"})
    assert res.status_code == 200 and res.json()["data"]["status"] == "inactive"
    log_ok("Admin deactivated user account")

    res = requests.patch(f"{BASE_URL}/users/{created_user_id}/status", headers=admin_headers, json={"status": "active"})
    assert res.status_code == 200 and res.json()["data"]["status"] == "active"
    log_ok("Admin reactivated user account")

    # Update user role
    res = requests.patch(f"{BASE_URL}/users/{created_user_id}/role", headers=admin_headers, json={"role": "ADMIN"})
    assert res.status_code == 200 and res.json()["data"]["role"] == "ADMIN"
    log_ok("Admin promoted user to ADMIN")

    # Delete user
    res = requests.delete(f"{BASE_URL}/users/{created_user_id}", headers=admin_headers)
    assert res.status_code == 200
    log_ok("Admin deleted user account")

    # 7. Research Paper Management & Listing
    log_step("7. Research Papers Search, Filter, Sort & Pagination")
    # Load demo papers for the new researcher
    for demo in ["ResNet_Deep_Residual_Learning.pdf", "Attention_Is_All_You_Need.pdf", "Qualitative_AI_Ethics_Governance.pdf"]:
        requests.post(f"{BASE_URL}/papers/demo/{demo}", headers=researcher_headers)

    res = requests.get(f"{BASE_URL}/papers?sort_by=newest&page=1&limit=5", headers=researcher_headers)
    assert res.status_code == 200
    papers_data = res.json()["data"]
    assert len(papers_data["items"]) >= 3
    assert papers_data["meta"]["total"] >= 3
    log_ok(f"Pagination verified: {papers_data['meta']['total']} total papers")

    # Test Search
    res = requests.get(f"{BASE_URL}/papers?search=ResNet", headers=researcher_headers)
    assert res.status_code == 200
    search_items = res.json()["data"]["items"]
    assert any("ResNet" in p["title"] or "ResNet" in p["file_name"] for p in search_items)
    log_ok("Search by title/keyword verified")

    # 8. AI/NLP Analysis on Quantitative Paper (ResNet)
    log_step("8. NLP Analysis & Metric Extraction on Quantitative Paper (ResNet)")
    resnet_paper = next((p for p in papers_data["items"] if "ResNet" in p["file_name"]), papers_data["items"][0])
    res = requests.post(f"{BASE_URL}/analysis/paper/{resnet_paper['id']}", headers=researcher_headers)
    assert res.status_code == 200
    analysis_id = res.json()["data"]["analysis_id"]
    log_ok(f"Analysis triggered successfully (ID: {analysis_id})")

    # 9. Verify 18-Section Structured Report & Easy Summary
    log_step("9. Verifying Complete 18-Section Academic Report & 6 Easy Summary Questions")
    res = requests.get(f"{BASE_URL}/analysis/{analysis_id}", headers=researcher_headers)
    assert res.status_code == 200
    report = res.json()["data"]

    # Check 18 structured sections:
    assert report["paper_title"] and report["paper_title"] != ""
    assert report["authors"] and report["authors"] != ""
    assert report["research_domain"] and report["research_domain"] != ""
    assert len(report["keywords"]) >= 1
    assert report["research_problem"] and report["research_problem"] != ""
    assert report["motivation"] and report["motivation"] != ""
    assert report["objective"] and report["objective"] != ""
    assert report["proposed_solution"] and report["proposed_solution"] != ""
    assert report["contribution"] and report["contribution"] != ""
    assert report["methodology"] and report["methodology"] != ""
    assert report["algorithms"] and report["algorithms"] != ""
    assert report["technologies"] and report["technologies"] != ""
    assert report["dataset"] and report["dataset"] != ""
    assert report["experimental_setup"] and report["experimental_setup"] != ""
    assert report["results"] and report["results"] != ""
    assert report["key_findings"] and report["key_findings"] != ""
    assert report["limitations"] and report["limitations"] != ""
    assert report["future_work"] and report["future_work"] != ""

    # Check 6 Easy Summary Questions:
    summary = report["easy_summary"]
    assert summary["what_is_this_paper_about"] and summary["what_is_this_paper_about"] != ""
    assert summary["what_problem_does_it_solve"] and summary["what_problem_does_it_solve"] != ""
    assert summary["why_was_the_research_conducted"] and summary["why_was_the_research_conducted"] != ""
    assert summary["how_was_it_performed"] and summary["how_was_it_performed"] != ""
    assert summary["what_was_the_result"] and summary["what_was_the_result"] != ""
    assert summary["what_is_the_main_contribution"] and summary["what_is_the_main_contribution"] != ""

    log_ok("All 18 structured report sections and 6 Easy Summary answers verified")

    # 10. Visualization Module & Strict Data Integrity
    log_step("10. Checking Visualization Data & Strict Data Integrity Rule")
    assert report["has_visualizations"] is True
    assert len(report["extracted_results"]) >= 2
    log_ok(f"Quantitative paper has {len(report['extracted_results'])} empirical metric comparisons and active chart data")

    # Analyze Qualitative Paper (AI Ethics)
    qual_paper = next((p for p in papers_data["items"] if "Qualitative" in p["file_name"]), None)
    if qual_paper:
        res = requests.post(f"{BASE_URL}/analysis/paper/{qual_paper['id']}", headers=researcher_headers)
        assert res.status_code == 200
        qual_analysis_id = res.json()["data"]["analysis_id"]

        res = requests.get(f"{BASE_URL}/analysis/{qual_analysis_id}", headers=researcher_headers)
        assert res.status_code == 200
        qual_report = res.json()["data"]

        # STRICT DATA INTEGRITY ASSERTION:
        assert qual_report["has_visualizations"] is False
        assert "No suitable numerical or comparative data" in qual_report["visualization_data"]["message"]
        log_ok("STRICT INTEGRITY ENFORCED: Qualitative paper produced ZERO fake charts and returned exact required message")

    # 11. Analysis History
    log_step("11. Verifying Analysis History Log")
    res = requests.get(f"{BASE_URL}/history", headers=researcher_headers)
    assert res.status_code == 200
    history_items = res.json()["data"]["items"]
    assert len(history_items) >= 1
    log_ok(f"Analysis history recorded {len(history_items)} entries")

    # 12. User & Admin Dashboards
    log_step("12. Verifying User and Admin Dashboards")
    res = requests.get(f"{BASE_URL}/dashboard/user", headers=researcher_headers)
    assert res.status_code == 200
    u_dash = res.json()["data"]
    assert u_dash["total_papers"] >= 3
    assert u_dash["total_analyzed"] >= 1
    log_ok("User dashboard statistics verified")

    res = requests.get(f"{BASE_URL}/dashboard/admin", headers=admin_headers)
    assert res.status_code == 200
    a_dash = res.json()["data"]
    assert a_dash["total_users"] >= 2
    assert a_dash["system_status"] == "Operational"
    log_ok("Admin dashboard statistics verified")

    print("\n=================================================================")
    print("SUCCESS: ALL FULL-STACK SYSTEM & INTEGRITY TESTS PASSED 100%!")
    print("=================================================================\n")

if __name__ == "__main__":
    run_full_suite()
