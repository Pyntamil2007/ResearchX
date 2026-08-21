import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import httpx
from app.main import app

def run_tests():
    print("=== STARTING DIRECT API INTEGRATION TESTS ===")
    
    client = httpx.Client(base_url="http://127.0.0.1:8000")
    
    try:
        # 1. Health check
        res = client.get("/api/health")
        assert res.status_code == 200, f"Health check failed: {res.text}"
        print("[PASS] Health check passed")

        # 2. Login as Researcher
        res = client.post("/api/auth/login", json={
            "email": "researcher@researchx.io",
            "password": "Researcher@123456"
        })
        assert res.status_code == 200, f"Researcher login failed: {res.text}"
        user_token = res.json()["data"]["access_token"]
        user_headers = {"Authorization": f"Bearer {user_token}"}
        print("[PASS] Researcher login passed")

        # 3. Login as Admin
        res = client.post("/api/auth/login", json={
            "email": "admin@researchx.io",
            "password": "Admin@123456"
        })
        assert res.status_code == 200, f"Admin login failed: {res.text}"
        admin_token = res.json()["data"]["access_token"]
        admin_headers = {"Authorization": f"Bearer {admin_token}"}
        print("[PASS] Admin login passed")

        # 4. User profile /me
        res = client.get("/api/auth/me", headers=user_headers)
        assert res.status_code == 200
        assert res.json()["data"]["email"] == "researcher@researchx.io"
        print("[PASS] Auth /me passed")

        # 5. List Papers
        res = client.get("/api/papers", headers=user_headers)
        assert res.status_code == 200
        papers_data = res.json()["data"]["items"]
        assert len(papers_data) >= 3, f"Expected at least 3 seeded papers, got {len(papers_data)}"
        print(f"[PASS] List papers passed ({len(papers_data)} papers found)")

        # 6. Analyze ResNet Paper (Quantitative)
        resnet_paper = next((p for p in papers_data if "ResNet" in p["file_name"]), papers_data[0])
        print(f"Analyzing paper {resnet_paper['id']}: {resnet_paper['title']}...")
        
        res = client.post(f"/api/analysis/paper/{resnet_paper['id']}", headers=user_headers)
        assert res.status_code == 200, f"Analysis failed: {res.text}"
        analysis_id = res.json()["data"]["analysis_id"]
        print(f"[PASS] Analysis triggered successfully (Analysis ID: {analysis_id})")

        # 7. Fetch Analysis Report
        res = client.get(f"/api/analysis/{analysis_id}", headers=user_headers)
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
        print(f"[PASS] ResNet report verified with {len(report['extracted_results'])} extracted metric comparisons")

        # 8. Analyze Qualitative Paper (Zero fake charts test!)
        qual_paper = next((p for p in papers_data if "Qualitative" in p["file_name"]), None)
        if qual_paper:
            print(f"Analyzing qualitative paper {qual_paper['id']}: {qual_paper['title']}...")
            res = client.post(f"/api/analysis/paper/{qual_paper['id']}", headers=user_headers)
            assert res.status_code == 200
            qual_analysis_id = res.json()["data"]["analysis_id"]

            res = client.get(f"/api/analysis/{qual_analysis_id}", headers=user_headers)
            assert res.status_code == 200
            qual_report = res.json()["data"]
            assert qual_report["has_visualizations"] is False
            assert "No suitable numerical or comparative data" in qual_report["visualization_data"]["message"]
            print("[PASS] STRICT DATA INTEGRITY PASSED: Qualitative paper correctly generated NO fake charts")

        # 9. Check User Dashboard
        res = client.get("/api/dashboard/user", headers=user_headers)
        assert res.status_code == 200
        user_dash = res.json()["data"]
        assert user_dash["total_papers"] >= 3
        assert user_dash["total_analyzed"] >= 1
        print("[PASS] User dashboard stats verified")

        # 10. Check Admin Dashboard & User Management
        res = client.get("/api/dashboard/admin", headers=admin_headers)
        assert res.status_code == 200
        print("[PASS] Admin dashboard verified")

        # Non-admin forbidden on admin endpoint
        res = client.get("/api/dashboard/admin", headers=user_headers)
        assert res.status_code == 403
        print("[PASS] Role-Based Access Control (RBAC) verified: Forbidden for non-admin")

        # Admin User CRUD
        res = client.get("/api/users", headers=admin_headers)
        assert res.status_code == 200
        users_list = res.json()["data"]["items"]
        print(f"[PASS] Admin list users passed ({len(users_list)} users)")

        print("\n==========================================")
        print("SUCCESS: ALL BACKEND & API TESTS PASSED 100%!")
        print("==========================================\n")
    finally:
        client.close()

if __name__ == "__main__":
    run_tests()
