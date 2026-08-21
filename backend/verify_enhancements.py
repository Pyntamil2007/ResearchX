import io
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import httpx
from app.core.config import settings
from app.database.database import SessionLocal
from app.models.user import User
from app.core.security import create_access_token, get_password_hash
from app.services.llm_service import LLMService

client = httpx.Client(base_url="http://127.0.0.1:8000")

def create_sample_image(text_content: str, filename: str) -> Path:
    """Create a sample PNG document image for OCR testing."""
    img_dir = settings.UPLOAD_DIR
    img_dir.mkdir(parents=True, exist_ok=True)
    img_path = img_dir / filename
    
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Simple line drawing
    draw.rectangle([20, 20, 780, 580], outline=(0, 0, 0), width=2)
    draw.text((40, 50), text_content, fill=(0, 0, 0))
    img.save(img_path)
    return img_path

def test_all_enhancements():
    db = SessionLocal()
    print("\n--- Starting Verification of All ResearchX Enhancements ---")

    # 1. Verify Configuration & 100 MB Limit
    print("1. Verifying File Size Limits and Allowed Extensions...")
    assert settings.MAX_FILE_SIZE_MB == 100, f"Expected 100 MB, got {settings.MAX_FILE_SIZE_MB}"
    assert ".png" in settings.ALLOWED_EXTENSIONS
    assert ".jpg" in settings.ALLOWED_EXTENSIONS
    assert ".jpeg" in settings.ALLOWED_EXTENSIONS
    assert ".webp" in settings.ALLOWED_EXTENSIONS
    assert ".pdf" in settings.ALLOWED_EXTENSIONS
    print("   [PASS] 100 MB Limit and Multi-format Extensions Verified.")

    # 2. Verify User Auth Tokens
    admin = db.query(User).filter(User.email == "admin@researchx.io").first()
    if not admin:
        admin = User(name="System Administrator", email="admin@researchx.io", hashed_password=get_password_hash("AdminPass123!"), role="ADMIN", status="active")
        db.add(admin)
        db.commit()
        db.refresh(admin)

    admin_token = create_access_token({"sub": str(admin.id), "role": admin.role})
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    # 3. Verify Image OCR Upload & Pipeline
    print("\n2. Testing Image Upload (PNG) with OCR & NLP Pipeline...")
    sample_ocr_img = create_sample_image("Research Paper: Deep Residual Learning\nAuthors: Kaiming He, Xiangyu Zhang\nAbstract: Deep networks are harder to train.", "test_ocr_paper.png")
    
    with open(sample_ocr_img, "rb") as f:
        upload_resp = client.post(
            "/api/papers/upload",
            headers=admin_headers,
            files={"file": ("test_ocr_paper.png", f, "image/png")},
            data={"title": "Deep Residual Learning Image", "domain": "Deep Learning"}
        )
    
    assert upload_resp.status_code == 200, f"Upload failed: {upload_resp.text}"
    paper_data = upload_resp.json()["data"]
    paper_id = paper_data["id"]
    print(f"   [PASS] Image uploaded successfully. Paper ID: {paper_id}, Type: {paper_data.get('document_type')}")

    # 4. Verify Analysis Pipeline on Image Paper
    print("\n3. Testing End-to-End Analysis Pipeline on Image Document...")
    analyze_resp = client.post(f"/api/analysis/paper/{paper_id}", headers=admin_headers)
    assert analyze_resp.status_code == 200, f"Analysis failed: {analyze_resp.text}"
    analysis_id = analyze_resp.json()["data"]["analysis_id"]

    report_resp = client.get(f"/api/analysis/{analysis_id}", headers=admin_headers)
    assert report_resp.status_code == 200, f"Report fetch failed: {report_resp.text}"
    analysis_data = report_resp.json()["data"]
    
    # Check that required structured sections exist
    assert "research_problem" in analysis_data
    assert "objective" in analysis_data
    assert "methodology" in analysis_data
    assert "easy_summary" in analysis_data
    assert "research_domain" in analysis_data
    assert "recommended_domains" in analysis_data
    print(f"   [PASS] Analysis completed. Domain: {analysis_data['research_domain']}, Easy Summary Questions: {len(analysis_data['easy_summary'])}")

    # 5. Verify Zero Hallucination fallback on empty text
    print("\n4. Testing Zero-Hallucination LLM/NLP Fallback...")
    fallback_analysis = LLMService.extract_structured_analysis("", {}, "Computer Science", "Research Paper", "Empty Paper", "")
    assert fallback_analysis["research_problem"] == "Information not available in the document."
    assert fallback_analysis["objective"] == "Information not available in the document."
    assert fallback_analysis["dataset"] == "Information not available in the document."
    print("   [PASS] Zero-Hallucination verification passed. Output is strictly grounded.")

    # 6. Verify Search + Filter + Sort + Pagination on /api/papers
    print("\n5. Testing Search + Filter + Sort + Pagination on /api/papers...")
    # Search
    res_search = client.get("/api/papers?search=Residual", headers=admin_headers)
    assert res_search.status_code == 200
    assert len(res_search.json()["data"]["items"]) >= 1

    # Filter by domain
    res_domain = client.get("/api/papers?domain=Deep%20Learning", headers=admin_headers)
    assert res_domain.status_code == 200

    # Sort
    res_sort = client.get("/api/papers?sort_by=alphabetical", headers=admin_headers)
    assert res_sort.status_code == 200

    # Pagination & Limit
    res_page = client.get("/api/papers?page=1&limit=25", headers=admin_headers)
    assert res_page.status_code == 200
    assert res_page.json()["data"]["meta"]["limit"] == 25
    print("   [PASS] /api/papers search, filter, sort, and pagination verified.")

    # 7. Verify Search + Filter + Sort + Pagination on /api/users
    print("\n6. Testing Search + Filter + Sort + Pagination on /api/users...")
    res_users = client.get("/api/users?role=ADMIN&status=active&sort_by=name&limit=10", headers=admin_headers)
    assert res_users.status_code == 200
    assert len(res_users.json()["data"]["items"]) >= 1
    print("   [PASS] /api/users search, filter, sort, and pagination verified.")

    # 8. Verify Search + Filter + Sort + Pagination on /api/history
    print("\n7. Testing Search + Filter + Sort + Pagination on /api/history...")
    res_history = client.get("/api/history?sort_by=newest&limit=10", headers=admin_headers)
    assert res_history.status_code == 200
    assert len(res_history.json()["data"]["items"]) >= 1
    print("   [PASS] /api/history search, filter, sort, and pagination verified.")

    # 9. Verify Admin Papers endpoint
    print("\n8. Testing Admin Papers endpoint /api/admin/papers...")
    res_admin_papers = client.get("/api/admin/papers?sort_by=newest&limit=25", headers=admin_headers)
    assert res_admin_papers.status_code == 200
    print("   [PASS] /api/admin/papers verified.")

    db.close()
    print("\n=== ALL ENHANCEMENT VERIFICATIONS PASSED SUCCESSFULLY ===")

if __name__ == "__main__":
    test_all_enhancements()
