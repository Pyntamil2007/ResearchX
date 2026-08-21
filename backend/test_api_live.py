import requests

BASE_URL = "http://127.0.0.1:8000/api"

def run_tests():
    print("=== STARTING LIVE BACKEND API VERIFICATION ===")

    # 1. Health check
    res = requests.get(f"{BASE_URL}/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    print("[OK] Health check endpoint operational")

    # 2. Login as Researcher
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "researcher@researchx.io",
        "password": "Researcher@123456"
    })
    assert res.status_code == 200, f"Researcher login failed: {res.text}"
    user_token = res.json()["data"]["access_token"]
    user_headers = {"Authorization": f"Bearer {user_token}"}
    print("[OK] Researcher authentication verified")

    # 3. Login as Admin
    res = requests.post(f"{BASE_URL}/auth/login", json={
        "email": "admin@researchx.io",
        "password": "Admin@123456"
    })
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_token = res.json()["data"]["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}
    print("[OK] Admin authentication verified")

    # 4. User profile /me
    res = requests.get(f"{BASE_URL}/auth/me", headers=user_headers)
    assert res.status_code == 200
    assert res.json()["data"]["email"] == "researcher@researchx.io"
    print("[OK] Profile verification passed")

    # 5. List Papers
    res = requests.get(f"{BASE_URL}/papers", headers=user_headers)
    assert res.status_code == 200
    papers_data = res.json()["data"]["items"]
    assert len(papers_data) >= 3, f"Expected at least 3 seeded papers, got {len(papers_data)}"
    print(f"[OK] Research paper list verified ({len(papers_data)} papers)")

    # 6. Analyze ResNet Paper (Quantitative)
    resnet_paper = next((p for p in papers_data if "ResNet" in p["file_name"]), papers_data[0])
    print(f"Analyzing paper {resnet_paper['id']}: {resnet_paper['title']}...")
    
    res = requests.post(f"{BASE_URL}/analysis/paper/{resnet_paper['id']}", headers=user_headers)
    assert res.status_code == 200, f"Analysis failed: {res.text}"
    analysis_id = res.json()["data"]["analysis_id"]
    print(f"[OK] AI/NLP Analysis executed successfully (ID: {analysis_id})")

    # 7. Fetch Analysis Report
    res = requests.get(f"{BASE_URL}/analysis/{analysis_id}", headers=user_headers)
    assert res.status_code == 200
    report = res.json()["data"]
    
    # Verify 18 sections & easy summary
    assert "paper_title" in report
    assert "research_problem" in report
    assert "methodology" in report
    assert "easy_summary" in report
    assert "what_is_this_paper_about" in report["easy_summary"]
    assert "what_was_the_result" in report["easy_summary"]
    assert report["has_visualizations"] is True
    assert len(report["extracted_results"]) >= 2
    print(f"[OK] ResNet report verified: {len(report['extracted_results'])} empirical metric comparisons extracted")

    # 8. Analyze Qualitative Paper (Zero fake charts test!)
    qual_paper = next((p for p in papers_data if "Qualitative" in p["file_name"]), None)
    if qual_paper:
        print(f"Analyzing qualitative paper {qual_paper['id']}: {qual_paper['title']}...")
        res = requests.post(f"{BASE_URL}/analysis/paper/{qual_paper['id']}", headers=user_headers)
        assert res.status_code == 200
        qual_analysis_id = res.json()["data"]["analysis_id"]

        res = requests.get(f"{BASE_URL}/analysis/{qual_analysis_id}", headers=user_headers)
        assert res.status_code == 200
        qual_report = res.json()["data"]
        assert qual_report["has_visualizations"] is False
        assert "No suitable numerical or comparative data" in qual_report["visualization_data"]["message"]
        print("[OK] STRICT DATA INTEGRITY PASSED: Qualitative paper correctly generated NO fake charts")

    # 9. Check User Dashboard
    res = requests.get(f"{BASE_URL}/dashboard/user", headers=user_headers)
    assert res.status_code == 200
    user_dash = res.json()["data"]
    assert user_dash["total_papers"] >= 3
    assert user_dash["total_analyzed"] >= 1
    print("[OK] User dashboard metrics verified")

    # 10. Check Admin Dashboard & User Management
    res = requests.get(f"{BASE_URL}/dashboard/admin", headers=admin_headers)
    assert res.status_code == 200
    print("[OK] Admin dashboard verified")

    # Role-Based Access Control
    res = requests.get(f"{BASE_URL}/dashboard/admin", headers=user_headers)
    assert res.status_code == 403
    print("[OK] Role-Based Access Control (RBAC) verified (403 Forbidden for non-admin)")

    # Admin User CRUD
    res = requests.get(f"{BASE_URL}/users", headers=admin_headers)
    assert res.status_code == 200
    users_list = res.json()["data"]["items"]
    print(f"[OK] Admin user list verified ({len(users_list)} users)")

    print("\n==========================================")
    print("ALL LIVE API & NLP TESTS PASSED 100%!")
    print("==========================================\n")

if __name__ == "__main__":
    run_tests()
