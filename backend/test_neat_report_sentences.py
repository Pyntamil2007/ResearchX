import httpx
from pathlib import Path
from app.services.text_polisher import TextPolisher

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_text_polisher_unit():
    print("\n========================================================")
    print("TESTING TEXT POLISHER & SENTENCE REFINEMENT UNIT")
    print("========================================================\n")

    # Sample messy text with citations, broken hyphens, lowercase starts, and missing periods
    raw_snippet = "we propose an effi-\n cient trans- \nformer model [1, 2] for image classification [3-5] . the model outperforms prior baselines (Smith et al., 2021) with 98.5% accuracy"
    
    polished = TextPolisher.format_neat_paragraph(raw_snippet, max_sentences=3)
    print(f"Original: {raw_snippet}")
    print(f"Polished: {polished}\n")

    assert polished.startswith("We propose"), "Must capitalize first letter"
    assert "effi-" not in polished and "efficient" in polished, "Must heal hyphenated word breaks"
    assert "[1, 2]" not in polished and "[3-5]" not in polished, "Must remove citation brackets"
    assert polished.endswith("."), "Must end with terminal period"
    print("[PASS] TextPolisher unit tests passed cleanly.")

def test_full_analysis_report_neat_sentences():
    print("\n========================================================")
    print("TESTING FULL ANALYSIS REPORT NEAT SENTENCE INTEGRATION")
    print("========================================================\n")

    # 1. Login as admin
    login_res = client.post("/api/auth/login", json={
        "email": "admin@researchx.com",
        "password": "Admin@2026"
    })
    assert login_res.status_code == 200, f"Login failed: {login_res.text}"
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload valid PDF from demo_papers
    pdf_path = Path("demo_papers/ResNet_Deep_Residual_Learning.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    files = {"file": ("ResNet_Deep_Residual_Learning.pdf", pdf_bytes, "application/pdf")}
    data = {
        "title": "Deep Residual Learning for Image Recognition",
        "authors": "Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun",
        "publication_info": "IEEE Conference on Computer Vision and Pattern Recognition (CVPR) 2016"
    }
    up_res = client.post("/api/papers/upload", data=data, files=files, headers=headers)
    assert up_res.status_code == 200, f"Upload failed: {up_res.text}"
    paper_id = up_res.json()["data"]["id"]

    # 3. Trigger Analysis
    an_res = client.post(f"/api/analysis/paper/{paper_id}", headers=headers)
    assert an_res.status_code == 200, f"Analysis failed: {an_res.text}"
    analysis_id = an_res.json()["data"]["analysis_id"]

    # 4. Fetch full report
    rep_res = client.get(f"/api/analysis/{analysis_id}", headers=headers)
    assert rep_res.status_code == 200, f"Get analysis failed: {rep_res.text}"
    report = rep_res.json()["data"]

    # 5. Check all 14 structured text fields for neat sentence structure
    check_fields = [
        "research_problem", "motivation", "objective", "proposed_solution",
        "contribution", "methodology", "algorithms", "technologies",
        "dataset", "experimental_setup", "results", "key_findings",
        "limitations", "future_work"
    ]

    for field in check_fields:
        val = report.get(field)
        assert val is not None and len(val.strip()) > 0, f"Field '{field}' must not be empty"
        if val != "Information not available in the document.":
            assert val[0].isupper(), f"Field '{field}' must start with an uppercase letter: '{val[:30]}'"
            assert val.endswith(('.', '!', '?')), f"Field '{field}' must end with proper punctuation: '{val[-15:]}'"
        print(f"[PASS] Section '{field}' formatted cleanly: {val[:60]}...")

    # 6. Check Easy Summary (6 questions)
    easy_sum = report.get("easy_summary", {})
    for q_key, q_val in easy_sum.items():
        assert q_val is not None and len(q_val.strip()) > 0
        if q_val != "Information not available in the document.":
            assert q_val[0].isupper(), f"Easy summary '{q_key}' must start with uppercase"
            assert q_val.endswith(('.', '!', '?')), f"Easy summary '{q_key}' must end with punctuation"
        print(f"[PASS] Easy Summary '{q_key}' verified: {q_val[:50]}...")

    print("\n============================================================")
    print("SUCCESS: ALL REPORT SENTENCES ARE NEAT, POLISHED & VERIFIED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_text_polisher_unit()
    test_full_analysis_report_neat_sentences()
