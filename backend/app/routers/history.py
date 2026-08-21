import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from app.database.database import get_db
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.paper import ResearchPaper
from app.models.history import AnalysisHistory
from app.models.analysis import Analysis
from app.schemas.history import AnalysisHistoryResponse
from app.schemas.common import StandardResponse, PaginatedData, PaginationMeta

router = APIRouter(prefix="/history", tags=["Analysis History"])

@router.get("", response_model=StandardResponse[PaginatedData[AnalysisHistoryResponse]])
def list_user_history(
    search: Optional[str] = None,
    domain: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = "newest",  # newest, oldest, title, domain
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve the logged-in user's analysis history with pagination, search, filtering, and sorting."""
    query = db.query(AnalysisHistory).join(ResearchPaper, AnalysisHistory.paper_id == ResearchPaper.id).filter(
        AnalysisHistory.user_id == current_user.id
    )

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ResearchPaper.title.ilike(search_term),
                ResearchPaper.authors.ilike(search_term),
                ResearchPaper.domain.ilike(search_term)
            )
        )

    if domain and domain != "all":
        query = query.filter(ResearchPaper.domain == domain)

    if status and status != "all":
        query = query.filter(ResearchPaper.status == status)

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(AnalysisHistory.created_at.asc())
    elif sort_by == "title":
        query = query.order_by(ResearchPaper.title.asc())
    elif sort_by == "domain":
        query = query.order_by(ResearchPaper.domain.asc(), AnalysisHistory.created_at.desc())
    else:  # "newest"
        query = query.order_by(desc(AnalysisHistory.created_at))

    total = query.count()
    total_pages = max(1, math.ceil(total / limit))
    offset = (page - 1) * limit

    records = query.offset(offset).limit(limit).all()

    items = []
    for h in records:
        items.append(AnalysisHistoryResponse(
            id=h.id,
            user_id=h.user_id,
            paper_id=h.paper_id,
            analysis_id=h.analysis_id,
            paper_title=h.paper.title if h.paper else "Untitled Research Paper",
            authors=h.paper.authors if h.paper else "Information not available in the document.",
            domain=h.paper.domain if h.paper else "Computer Science",
            created_at=h.created_at,
            user_name=current_user.name,
            user_email=current_user.email
        ))

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
        message="Analysis history retrieved.",
        data=PaginatedData(items=items, meta=meta)
    )

@router.get("/admin", response_model=StandardResponse[PaginatedData[AnalysisHistoryResponse]])
def list_admin_history(
    search: Optional[str] = None,
    domain: Optional[str] = None,
    status: Optional[str] = None,
    sort_by: Optional[str] = "newest",  # newest, oldest, title, domain
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Retrieve system-wide analysis history (Admin only)."""
    query = db.query(AnalysisHistory).join(ResearchPaper, AnalysisHistory.paper_id == ResearchPaper.id).join(User, AnalysisHistory.user_id == User.id)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                ResearchPaper.title.ilike(search_term),
                ResearchPaper.authors.ilike(search_term),
                User.name.ilike(search_term),
                User.email.ilike(search_term),
                ResearchPaper.domain.ilike(search_term)
            )
        )

    if domain and domain != "all":
        query = query.filter(ResearchPaper.domain == domain)

    if status and status != "all":
        query = query.filter(ResearchPaper.status == status)

    # Sorting
    if sort_by == "oldest":
        query = query.order_by(AnalysisHistory.created_at.asc())
    elif sort_by == "title":
        query = query.order_by(ResearchPaper.title.asc())
    elif sort_by == "domain":
        query = query.order_by(ResearchPaper.domain.asc(), AnalysisHistory.created_at.desc())
    else:  # "newest"
        query = query.order_by(desc(AnalysisHistory.created_at))

    total = query.count()
    total_pages = max(1, math.ceil(total / limit))
    offset = (page - 1) * limit

    records = query.offset(offset).limit(limit).all()

    items = []
    for h in records:
        items.append(AnalysisHistoryResponse(
            id=h.id,
            user_id=h.user_id,
            paper_id=h.paper_id,
            analysis_id=h.analysis_id,
            paper_title=h.paper.title if h.paper else "Untitled Research Paper",
            authors=h.paper.authors if h.paper else "Information not available in the document.",
            domain=h.paper.domain if h.paper else "Computer Science",
            created_at=h.created_at,
            user_name=h.user.name if h.user else "Unknown User",
            user_email=h.user.email if h.user else ""
        ))

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
        message="System analysis history retrieved.",
        data=PaginatedData(items=items, meta=meta)
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_history_item(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an entry from analysis history."""
    history = db.query(AnalysisHistory).filter(AnalysisHistory.id == id).first()
    if not history:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"History record with ID {id} not found."
        )

    if current_user.role != "ADMIN" and history.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    db.delete(history)
    db.commit()

    return StandardResponse(
        success=True,
        message="History record deleted successfully.",
        data={"deleted_history_id": id}
    )
