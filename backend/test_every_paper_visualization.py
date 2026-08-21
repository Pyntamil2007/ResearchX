import httpx
from pathlib import Path

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_every_paper_gets_visualization():
    print("\n========================================================")
    print("STARTING TEST SUITE: VISUALIZATIONS FOR EVERY PAPER UPLOAD")
    print("========================================================\n")

    # 1. Login
    login_res = client.post("/api/auth/login", json={
        "email": "admin@researchx.com",
        "password": "Admin@2026"
    })
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    test_papers = [
        ("demo_papers/ResNet_Deep_Residual_Learning.pdf", "Deep Residual Learning for Image Recognition", "Kaiming He et al.", "Computer Vision"),
        ("demo_papers/Attention_Is_All_You_Need.pdf", "Attention Is All You Need", "Ashish Vaswani et al.", "Natural Language Processing"),
        ("demo_papers/Qualitative_AI_Ethics_Governance.pdf", "AI Ethics and Algorithmic Governance in Healthcare", "Dr. Elena Rostova", "Healthcare")
    ]

    for pdf_rel_path, title, authors, domain in test_papers:
        pdf_path = Path(pdf_rel_path)
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        # Upload
        up_res = client.post(
            "/api/papers/upload",
            data={"title": title, "authors": authors, "publication_info": "Academic Conference 2026"},
            files={"file": (pdf_path.name, pdf_bytes, "application/pdf")},
            headers=headers
        )
        assert up_res.status_code == 200, f"Upload failed for {title}: {up_res.text}"
        paper_id = up_res.json()["data"]["id"]

        # Trigger Analysis
        an_res = client.post(f"/api/analysis/paper/{paper_id}", headers=headers)
        assert an_res.status_code == 200, f"Analysis failed for {title}: {an_res.text}"
        analysis_id = an_res.json()["data"]["analysis_id"]

        # Fetch Full Report
        rep_res = client.get(f"/api/analysis/{analysis_id}", headers=headers)
        assert rep_res.status_code == 200, f"Get analysis failed: {rep_res.text}"
        report = rep_res.json()["data"]

        # Verification
        assert report["has_visualizations"] is True, f"Paper '{title}' must have has_visualizations = True"
        v_data = report.get("visualization_data", {})
        assert v_data.get("has_visualizations") is True, f"Paper '{title}' visualization_data.has_visualizations must be True"
        
        series = v_data.get("series", [])
        table_rows = v_data.get("table_rows", [])
        metrics_summary = v_data.get("metrics_summary", [])

        assert len(series) >= 3, f"Paper '{title}' must have at least 3 visualization series items, got {len(series)}"
        assert len(table_rows) >= 3, f"Paper '{title}' must have at least 3 comparison table rows, got {len(table_rows)}"
        assert len(metrics_summary) >= 1, f"Paper '{title}' must have metrics summary"

        print(f"[PASS] Paper '{title}' ({report.get('research_domain')}):")
        print(f"       -> Generated {len(series)} benchmark series ({[s['name'] for s in series]})")
        print(f"       -> Metric dimensions: {metrics_summary}")
        print(f"       -> has_visualizations: {report['has_visualizations']}\n")

    print("============================================================")
    print("SUCCESS: EVERY PAPER UPLOAD HAS GUARANTEED VISUALIZATIONS!")
    print("============================================================\n")

if __name__ == "__main__":
    test_every_paper_gets_visualization()
