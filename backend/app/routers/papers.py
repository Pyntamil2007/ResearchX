import os
import re
import math
import shutil
import uuid
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc
from app.database.database import get_db
from app.core.config import settings
from app.core.security import get_current_user
from app.models.user import User
from app.models.paper import ResearchPaper
from app.models.analysis import Analysis
from app.services.pdf_service import PDFService
from app.services.docx_service import DocxService
from app.services.ocr_service import OCRService
from app.services.notification_service import NotificationService
from app.schemas.paper import ResearchPaperResponse, ResearchPaperCreate, ResearchPaperUpdate
from app.schemas.common import StandardResponse, PaginatedData, PaginationMeta

router = APIRouter(prefix="/papers", tags=["Research Papers"])

ALLOWED_MIME_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "application/octet-stream"
}

@router.post("/upload", response_model=StandardResponse[ResearchPaperResponse])
async def upload_paper(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    domain: Optional[str] = Form("Computer Science"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Upload a new research paper in PDF, DOC, DOCX, or Image (JPG, JPEG, PNG, WEBP) format up to 100MB."""
    # 1. Validate file extension
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload PDF, DOC, DOCX, JPG, JPEG, or PNG."
        )

    # 2. Validate MIME type if provided
    content_type = (file.content_type or "").lower().strip()
    if content_type and content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Please upload PDF, DOC, DOCX, JPG, JPEG, or PNG."
        )

    # 3. Read and validate file size (100 MB max)
    contents = await file.read()
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(contents) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File exceeds the maximum allowed size of {settings.MAX_FILE_SIZE_MB}MB."
        )
    if len(contents) < 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty or corrupted."
        )

    # 4. Content signature verification (Magic Bytes)
    if file_ext == ".pdf" and not (contents.startswith(b'%PDF') or b'%PDF' in contents[:1024]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded PDF file is corrupted or not a valid PDF."
        )
    elif file_ext == ".docx" and not contents.startswith(b'PK\x03\x04'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded DOCX file is corrupted or not a valid Microsoft Word document."
        )
    elif file_ext in (".jpg", ".jpeg") and not (contents.startswith(b'\xff\xd8\xff') or contents.startswith(b'\xff\xd8')):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid JPEG image."
        )
    elif file_ext == ".png" and not contents.startswith(b'\x89PNG\r\n\x1a\n'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is not a valid PNG image."
        )

    # 5. Generate safe unique filename and save to storage
    unique_prefix = uuid.uuid4().hex[:8]
    safe_filename = f"{unique_prefix}_{file.filename.replace(' ', '_')}"
    saved_path = settings.UPLOAD_DIR / safe_filename

    with open(saved_path, "wb") as f:
        f.write(contents)

    # 6. Extract preliminary text, title, and authors
    extracted_text = ""
    inferred_title = title.strip() if title else ""
    inferred_authors = "Information not available in the document."
    inferred_doc_type = "Research Paper"
    
    try:
        if file_ext in (".jpg", ".jpeg", ".png", ".webp"):
            extracted_text = OCRService.extract_text_from_image(saved_path)
            inferred_doc_type = "Academic Document"
            if not inferred_title:
                clean_name = re.sub(r'\.(jpg|jpeg|png|webp)$', '', file.filename, flags=re.I).replace('_', ' ')
                inferred_title = clean_name
        elif file_ext == ".docx":
            extracted_text = DocxService.extract_text_from_docx(saved_path)
            sections = PDFService.segment_sections(extracted_text)
            inferred_doc_type = PDFService.detect_document_type(extracted_text)
            if not inferred_title:
                inferred_title = sections.get("title") or file.filename.replace(".docx", "").replace("_", " ")
            inferred_authors = sections.get("authors", inferred_authors)
        elif file_ext == ".doc":
            extracted_text = DocxService.extract_text_from_doc(saved_path)
            sections = PDFService.segment_sections(extracted_text)
            inferred_doc_type = PDFService.detect_document_type(extracted_text)
            if not inferred_title:
                inferred_title = sections.get("title") or file.filename.replace(".doc", "").replace("_", " ")
            inferred_authors = sections.get("authors", inferred_authors)
        else:
            extracted_text = PDFService.extract_text_from_pdf(saved_path)
            sections = PDFService.segment_sections(extracted_text)
            inferred_doc_type = PDFService.detect_document_type(extracted_text)
            if not inferred_title:
                inferred_title = sections.get("title") or file.filename.replace(".pdf", "").replace("_", " ")
            inferred_authors = sections.get("authors", inferred_authors)
    except HTTPException:
        raise
    except Exception as e:
        if not inferred_title:
            inferred_title = file.filename.replace(file_ext, "").replace("_", " ")

    # 7. Create database record
    paper = ResearchPaper(
        user_id=current_user.id,
        title=inferred_title[:250],
        authors=inferred_authors[:250],
        file_name=file.filename,
        file_path=str(saved_path),
        domain=domain or "Computer Science",
        document_type=inferred_doc_type,
        status="Uploaded",
        raw_text=extracted_text
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    # 1. User In-App Notification: Research paper uploaded
    NotificationService.create_user_notification(
        db=db,
        user_id=current_user.id,
        title="Research paper uploaded",
        message=f"Research document \"{paper.title}\" uploaded successfully and is ready for analysis.",
        notification_type="paper_uploaded"
    )

    # 2. Admin In-App Notification: New research paper uploaded
    NotificationService.notify_admins(
        db=db,
        title="New research paper uploaded",
        message=f"User {current_user.name} ({current_user.email}) uploaded a new research document: \"{paper.title}\".",
        notification_type="admin_paper_uploaded"
    )

    resp_data = ResearchPaperResponse.from_orm(paper)
    resp_data.user_name = current_user.name
    resp_data.user_email = current_user.email

    return StandardResponse(
        success=True,
        message=f"Research document '{paper.title}' uploaded successfully.",
        data=resp_data
    )

@router.post("/demo/{demo_file_name}", response_model=StandardResponse[ResearchPaperResponse])
def load_demo_paper(
    demo_file_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Load a pre-packaged sample academic research paper."""
    src_path = settings.DEMO_DIR / demo_file_name
    if not src_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Sample paper '{demo_file_name}' not found."
        )

    # Copy to uploads with unique name
    unique_prefix = uuid.uuid4().hex[:8]
    dest_file_name = f"demo_{unique_prefix}_{demo_file_name}"
    dest_path = settings.UPLOAD_DIR / dest_file_name
    shutil.copyfile(src_path, dest_path)

    # Extract text and metadata
    extracted_text = PDFService.extract_text_from_pdf(dest_path)
    sections = PDFService.segment_sections(extracted_text)
    
    paper_title = sections.get("title", demo_file_name.replace(".pdf", "").replace("_", " "))
    paper_authors = sections.get("authors", "Academic Researchers")
    
    domain_map = {
        "ResNet_Deep_Residual_Learning.pdf": "Computer Vision & Deep Learning",
        "Attention_Is_All_You_Need.pdf": "Natural Language Processing",
        "Qualitative_AI_Ethics_Governance.pdf": "AI Ethics & Governance"
    }
    domain = domain_map.get(demo_file_name, "Computer Science")

    paper = ResearchPaper(
        user_id=current_user.id,
        title=paper_title[:250],
        authors=paper_authors[:250],
        file_name=demo_file_name,
        file_path=str(dest_path),
        domain=domain,
        status="Uploaded",
        raw_text=extracted_text
    )
    db.add(paper)
    db.commit()
    db.refresh(paper)

    resp_data = ResearchPaperResponse.from_orm(paper)
    resp_data.user_name = current_user.name
    resp_data.user_email = current_user.email

    return StandardResponse(
        success=True,
        message=f"Sample paper '{paper.title}' loaded into your workspace.",
        data=resp_data
    )

@router.get("", response_model=StandardResponse[PaginatedData[ResearchPaperResponse]])
def list_papers(
    search: Optional[str] = None,
    domain: Optional[str] = None,
    document_type: Optional[str] = None,
    author: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = "newest",  # newest, oldest, alphabetical, domain, author
    all_users: bool = Query(False, description="Admin flag to view papers from all users"),
    user_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve list of research papers with search, filtering, and pagination."""
    query = db.query(ResearchPaper)

    # Permission check: Non-admin can only view their own papers
    if current_user.role != "ADMIN" or not all_users:
        if user_id and current_user.role == "ADMIN":
            query = query.filter(ResearchPaper.user_id == user_id)
        else:
            query = query.filter(ResearchPaper.user_id == current_user.id)

    # Search filter
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ResearchPaper.title.ilike(search_term),
                ResearchPaper.authors.ilike(search_term),
                ResearchPaper.domain.ilike(search_term),
                ResearchPaper.file_name.ilike(search_term)
            )
        )

    # Domain filter
    if domain and domain != "all":
        query = query.filter(ResearchPaper.domain == domain)

    # Document Type filter
    if document_type and document_type != "all":
        query = query.filter(ResearchPaper.document_type == document_type)

    # Author filter
    if author and author.strip():
        query = query.filter(ResearchPaper.authors.ilike(f"%{author.strip()}%"))

    # Status filter
    if status and status != "all":
        query = query.filter(ResearchPaper.status == status)

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(asc(ResearchPaper.uploaded_at))
    elif sort_by == "alphabetical":
        query = query.order_by(asc(ResearchPaper.title))
    elif sort_by == "domain":
        query = query.order_by(asc(ResearchPaper.domain), desc(ResearchPaper.uploaded_at))
    elif sort_by == "author":
        query = query.order_by(asc(ResearchPaper.authors), desc(ResearchPaper.uploaded_at))
    else:  # "newest"
        query = query.order_by(desc(ResearchPaper.uploaded_at))

    total = query.count()
    total_pages = max(1, math.ceil(total / limit))
    offset = (page - 1) * limit

    papers = query.offset(offset).limit(limit).all()

    # Enhance paper items with user and analysis info
    items = []
    for p in papers:
        resp = ResearchPaperResponse.from_orm(p)
        if p.user:
            resp.user_name = p.user.name
            resp.user_email = p.user.email
        
        # Check if analysis exists
        latest_analysis = db.query(Analysis).filter(Analysis.paper_id == p.id).order_by(Analysis.id.desc()).first()
        if latest_analysis:
            resp.has_analysis = True
            resp.latest_analysis_id = latest_analysis.id
            
        items.append(resp)

    meta = PaginationMeta(
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
        has_next=page < total_pages,
        has_prev=page > 1
    )

    return StandardResponse(
        success=True,
        message="Research papers retrieved successfully.",
        data=PaginatedData(items=items, meta=meta)
    )

@router.get("/{id}", response_model=StandardResponse[ResearchPaperResponse])
def get_paper(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve details of a specific research paper."""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research paper with ID {id} not found."
        )

    if current_user.role != "ADMIN" and paper.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access this research paper."
        )

    resp = ResearchPaperResponse.from_orm(paper)
    if paper.user:
        resp.user_name = paper.user.name
        resp.user_email = paper.user.email

    latest_analysis = db.query(Analysis).filter(Analysis.paper_id == paper.id).order_by(Analysis.id.desc()).first()
    if latest_analysis:
        resp.has_analysis = True
        resp.latest_analysis_id = latest_analysis.id

    return StandardResponse(
        success=True,
        message="Paper details retrieved.",
        data=resp
    )

@router.get("/{id}/download")
def download_paper(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download the original document file of the research paper."""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research paper with ID {id} not found."
        )

    if current_user.role != "ADMIN" and paper.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    file_path = Path(paper.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The requested file is missing from server storage."
        )

    ext = file_path.suffix.lower()
    media_types = {
        ".pdf": "application/pdf",
        ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ".doc": "application/msword",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp"
    }
    media_type = media_types.get(ext, "application/octet-stream")

    return FileResponse(
        path=str(file_path),
        filename=paper.file_name,
        media_type=media_type
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_paper(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a research paper and its associated analyses and storage file."""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research paper with ID {id} not found."
        )

    if current_user.role != "ADMIN" and paper.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this paper."
        )

    # Remove file from disk if present
    try:
        p = Path(paper.file_path)
        if p.exists() and "uploads" in str(p):
            p.unlink()
    except Exception:
        pass

    paper_title = paper.title
    db.delete(paper)
    db.commit()

    return StandardResponse(
        success=True,
        message=f"Research paper '{paper_title}' deleted successfully.",
        data={"deleted_paper_id": id}
    )
