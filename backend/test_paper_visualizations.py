import httpx
from pathlib import Path
from app.services.visualization_service import VisualizationService

client = httpx.Client(base_url="http://127.0.0.1:8000")

def test_visualization_service_direct():
    print("\n========================================================")
    print("TESTING VISUALIZATION SERVICE EXTRACTION LOGIC")
    print("========================================================\n")

    # Sample text with model accuracy comparisons
    resnet_text = """
    We evaluate our residual networks on the ImageNet 2012 classification dataset.
    Our 152-layer ResNet achieves a top-1 error rate of 4.49% (95.51% Accuracy).
    ResNet-101: 94.8% Accuracy.
    ResNet-50: 93.6% Accuracy.
    VGG-16: 89.2% Accuracy.
    GoogLeNet: 91.1% Accuracy.
    AlexNet: 84.5% Accuracy.
    """
    extracted, viz_data = VisualizationService.extract_metrics_and_comparisons(resnet_text, {"results": resnet_text})
    print(f"Extracted models: {[m['model_name'] for m in extracted]}")
    assert len(extracted) >= 3, f"Expected at least 3 models extracted, got {len(extracted)}"
    assert viz_data["has_visualizations"] is True
    assert len(viz_data["series"]) >= 3
    assert len(viz_data["table_rows"]) >= 3
    print(f"[PASS] VisualizationService successfully extracted {len(extracted)} comparative models.")

    # Qualitative text test -> has_visualizations = False
    qualitative_text = "This paper explores the ethical implications of artificial intelligence governance in clinical diagnostic systems."
    ext_qual, qual_viz = VisualizationService.extract_metrics_and_comparisons(qualitative_text, {})
    assert qual_viz["has_visualizations"] is False
    assert "No suitable numerical" in qual_viz["message"]
    print("[PASS] Qualitative document correctly designated with has_visualizations=False.")

def test_end_to_end_paper_visualizations():
    print("\n========================================================")
    print("TESTING END-TO-END RESEARCH PAPER VISUALIZATION API")
    print("========================================================\n")

    # 1. Login
    login_res = client.post("/api/auth/login", json={
        "email": "admin@researchx.com",
        "password": "Admin@2026"
    })
    assert login_res.status_code == 200
    token = login_res.json()["data"]["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Upload ResNet paper
    pdf_path = Path("demo_papers/ResNet_Deep_Residual_Learning.pdf")
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    files = {"file": ("ResNet_Deep_Residual_Learning.pdf", pdf_bytes, "application/pdf")}
    data = {
        "title": "Deep Residual Learning for Image Recognition",
        "authors": "Kaiming He, Xiangyu Zhang, Shaoqing Ren, Jian Sun",
        "publication_info": "IEEE CVPR 2016"
    }
    up_res = client.post("/api/papers/upload", data=data, files=files, headers=headers)
    assert up_res.status_code == 200
    paper_id = up_res.json()["data"]["id"]

    # 3. Analyze paper
    an_res = client.post(f"/api/analysis/paper/{paper_id}", headers=headers)
    assert an_res.status_code == 200
    analysis_id = an_res.json()["data"]["analysis_id"]

    # 4. Fetch Results & Visualizations via /api/results/{analysis_id}
    res_viz = client.get(f"/api/results/{analysis_id}", headers=headers)
    assert res_viz.status_code == 200
    viz_payload = res_viz.json()["data"]

    assert "has_visualizations" in viz_payload
    print(f"[PASS] /api/results/{analysis_id} endpoint healthy (has_visualizations: {viz_payload['has_visualizations']}).")

    # 5. Fetch Full Report via /api/analysis/{analysis_id}
    rep_res = client.get(f"/api/analysis/{analysis_id}", headers=headers)
    assert rep_res.status_code == 200
    report_data = rep_res.json()["data"]

    assert "visualization_data" in report_data
    v_data = report_data["visualization_data"]
    assert "series" in v_data
    assert "table_rows" in v_data
    print(f"[PASS] /api/analysis/{analysis_id} delivered complete visualization package with {len(v_data.get('series', []))} series entries.")

    print("\n============================================================")
    print("SUCCESS: RESEARCH PAPER VISUALIZATIONS FULLY VERIFIED!")
    print("============================================================\n")

if __name__ == "__main__":
    test_visualization_service_direct()
    test_end_to_end_paper_visualizations()
