import math
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from app.database.database import get_db
from app.core.security import require_admin
from app.models.user import User
from app.models.paper import ResearchPaper
from app.models.analysis import Analysis
from app.schemas.user import UserResponse
from app.schemas.paper import ResearchPaperResponse
from app.schemas.common import StandardResponse, PaginatedData, PaginationMeta

router = APIRouter(prefix="/admin", tags=["Admin System Management"])

@router.get("/users", response_model=StandardResponse[PaginatedData[UserResponse]])
def get_all_users_admin(
    search: Optional[str] = None,
    role: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin: Retrieve all users in the system."""
    query = db.query(User)

    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                User.name.ilike(search_term),
                User.email.ilike(search_term)
            )
        )

    if role:
        query = query.filter(User.role == role.upper())

    if status_filter:
        query = query.filter(User.status == status_filter.lower())

    total = query.count()
    total_pages = max(1, math.ceil(total / limit))
    offset = (page - 1) * limit

    users = query.order_by(desc(User.created_at)).offset(offset).limit(limit).all()
    user_responses = [UserResponse.from_orm(u) for u in users]

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
        message="Users list retrieved for admin.",
        data=PaginatedData(items=user_responses, meta=meta)
    )

@router.get("/papers", response_model=StandardResponse[PaginatedData[ResearchPaperResponse]])
def get_all_papers_admin(
    search: Optional[str] = None,
    domain: Optional[str] = None,
    document_type: Optional[str] = None,
    author: Optional[str] = None,
    status_filter: Optional[str] = Query(None, alias="status"),
    sort_by: Optional[str] = "newest",  # newest, oldest, alphabetical, domain, author
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin: Retrieve all research papers across all users."""
    query = db.query(ResearchPaper).join(User, ResearchPaper.user_id == User.id)

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

    if document_type and document_type != "all":
        query = query.filter(ResearchPaper.document_type == document_type)

    if author and author.strip():
        query = query.filter(ResearchPaper.authors.ilike(f"%{author.strip()}%"))

    if status_filter and status_filter != "all":
        query = query.filter(ResearchPaper.status == status_filter)

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

    items = []
    for p in papers:
        resp = ResearchPaperResponse.from_orm(p)
        if p.user:
            resp.user_name = p.user.name
            resp.user_email = p.user.email
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
        message="All research papers retrieved for admin.",
        data=PaginatedData(items=items, meta=meta)
    )

@router.delete("/papers/{id}", response_model=StandardResponse[dict])
def admin_delete_paper(
    id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin: Delete any research paper and cascade remove its analysis records."""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Paper with ID {id} not found."
        )

    title = paper.title
    db.delete(paper)
    db.commit()

    return StandardResponse(
        success=True,
        message=f"Paper '{title}' deleted by admin.",
        data={"deleted_paper_id": id}
    )

@router.get("/statistics", response_model=StandardResponse[dict])
def get_system_statistics(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Admin: Get deep system statistics and health metrics."""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.status == "active").count()
    inactive_users = db.query(User).filter(User.status == "inactive").count()
    admin_users = db.query(User).filter(User.role == "ADMIN").count()
    total_papers = db.query(ResearchPaper).count()
    total_analyzed = db.query(ResearchPaper).filter(ResearchPaper.status == "Analyzed").count()
    total_analyses = db.query(Analysis).count()
    completed_analyses = total_analyses
    failed_analyses = db.query(ResearchPaper).filter(ResearchPaper.status == "Failed").count()

    domains = db.query(ResearchPaper.domain, func.count(ResearchPaper.id)).group_by(ResearchPaper.domain).all()

    return StandardResponse(
        success=True,
        message="System statistics retrieved.",
        data={
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": inactive_users,
            "total_papers": total_papers,
            "total_analyses": total_analyses,
            "completed_analyses": completed_analyses,
            "failed_analyses": failed_analyses,
            "users": {
                "total": total_users,
                "active": active_users,
                "admins": admin_users,
                "researchers": total_users - admin_users
            },
            "papers": {
                "total": total_papers,
                "analyzed": total_analyzed,
                "pending": total_papers - total_analyzed
            },
            "analyses": {
                "total": total_analyses,
                "completed": completed_analyses,
                "failed": failed_analyses
            },
            "domain_breakdown": {d: c for d, c in domains},
            "server": {
                "status": "Operational",
                "framework": "FastAPI + SQLAlchemy + SQLite",
                "version": "1.0.0"
            }
        }
    )
