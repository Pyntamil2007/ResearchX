import os
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.database.database import get_db
from app.core.config import settings
from app.core.security import get_current_user, require_admin
from app.models.user import User
from app.models.paper import ResearchPaper
from app.models.analysis import Analysis
from app.models.history import AnalysisHistory
from app.schemas.paper import ResearchPaperResponse
from app.schemas.history import AnalysisHistoryResponse
from app.schemas.dashboard import UserDashboardStats, AdminDashboardStats, DomainStat
from app.schemas.common import StandardResponse

router = APIRouter(prefix="/dashboard", tags=["Dashboard Statistics"])

@router.get("/user", response_model=StandardResponse[UserDashboardStats])
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve personal dashboard statistics for the logged-in researcher."""
    total_papers = db.query(ResearchPaper).filter(ResearchPaper.user_id == current_user.id).count()
    total_analyzed = db.query(ResearchPaper).filter(ResearchPaper.user_id == current_user.id, ResearchPaper.status == "Analyzed").count()
    total_processing = db.query(ResearchPaper).filter(ResearchPaper.user_id == current_user.id, ResearchPaper.status == "Processing").count()
    total_failed = db.query(ResearchPaper).filter(ResearchPaper.user_id == current_user.id, ResearchPaper.status == "Failed").count()

    # Recent papers
    recent_papers_query = db.query(ResearchPaper).filter(ResearchPaper.user_id == current_user.id).order_by(desc(ResearchPaper.uploaded_at)).limit(5).all()
    recent_papers = []
    for p in recent_papers_query:
        resp = ResearchPaperResponse.from_orm(p)
        latest_analysis = db.query(Analysis).filter(Analysis.paper_id == p.id).order_by(Analysis.id.desc()).first()
        if latest_analysis:
            resp.has_analysis = True
            resp.latest_analysis_id = latest_analysis.id
        recent_papers.append(resp)

    # Recent analyses
    recent_history_query = db.query(AnalysisHistory).join(ResearchPaper, AnalysisHistory.paper_id == ResearchPaper.id).filter(AnalysisHistory.user_id == current_user.id).order_by(desc(AnalysisHistory.created_at)).limit(5).all()
    recent_analyses = []
    for h in recent_history_query:
        recent_analyses.append(AnalysisHistoryResponse(
            id=h.id,
            user_id=h.user_id,
            paper_id=h.paper_id,
            analysis_id=h.analysis_id,
            paper_title=h.paper.title if h.paper else "Untitled Research Paper",
            authors=h.paper.authors if h.paper else "Information not available in the paper.",
            domain=h.paper.domain if h.paper else "Computer Science",
            created_at=h.created_at,
            user_name=current_user.name,
            user_email=current_user.email
        ))

    # Domain distribution
    domain_counts = db.query(
        ResearchPaper.domain, func.count(ResearchPaper.id)
    ).filter(ResearchPaper.user_id == current_user.id).group_by(ResearchPaper.domain).all()

    domain_distribution = [
        DomainStat(domain=d or "Other", count=c) for d, c in domain_counts
    ]

    metrics_summary = {
        "analysis_rate_pct": round((total_analyzed / total_papers * 100), 1) if total_papers > 0 else 0,
        "active_papers": total_papers - total_failed,
        "unread_analyses": max(0, total_analyzed - len(recent_analyses))
    }

    stats = UserDashboardStats(
        total_papers=total_papers,
        total_analyzed=total_analyzed,
        total_processing=total_processing,
        total_failed=total_failed,
        recent_papers=recent_papers,
        recent_analyses=recent_analyses,
        domain_distribution=domain_distribution,
        metrics_summary=metrics_summary
    )

    return StandardResponse(
        success=True,
        message="User dashboard statistics retrieved.",
        data=stats
    )

@router.get("/admin", response_model=StandardResponse[AdminDashboardStats])
def get_admin_dashboard(
    db: Session = Depends(get_db),
    admin: User = Depends(require_admin)
):
    """Retrieve system-wide analytics for administrators."""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.status == "active").count()
    inactive_users = db.query(User).filter(User.status == "inactive").count()

    total_papers = db.query(ResearchPaper).count()
    total_analyzed = db.query(ResearchPaper).filter(ResearchPaper.status == "Analyzed").count()
    total_analyses = db.query(Analysis).count()
    completed_analyses = total_analyses
    failed_analyses = db.query(ResearchPaper).filter(ResearchPaper.status == "Failed").count()

    # Calculate upload storage directory size
    storage_bytes = 0
    if settings.UPLOAD_DIR.exists():
        for f in settings.UPLOAD_DIR.glob("**/*"):
            if f.is_file():
                storage_bytes += f.stat().st_size
    storage_used_mb = round(storage_bytes / (1024 * 1024), 2)

    # Domain distribution across all papers
    domain_counts = db.query(
        ResearchPaper.domain, func.count(ResearchPaper.id)
    ).group_by(ResearchPaper.domain).all()

    domain_distribution = [
        DomainStat(domain=d or "Other", count=c) for d, c in domain_counts
    ]

    # Recent users
    recent_users_query = db.query(User).order_by(desc(User.created_at)).limit(5).all()
    recent_users = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role,
            "status": u.status,
            "created_at": u.created_at.isoformat()
        }
        for u in recent_users_query
    ]

    # Recent activity
    recent_activity_query = db.query(AnalysisHistory).join(ResearchPaper, AnalysisHistory.paper_id == ResearchPaper.id).join(User, AnalysisHistory.user_id == User.id).order_by(desc(AnalysisHistory.created_at)).limit(8).all()
    recent_activity = [
        {
            "id": h.id,
            "action": "Analyzed Research Paper",
            "paper_title": h.paper.title if h.paper else "Untitled Paper",
            "user_name": h.user.name if h.user else "System",
            "created_at": h.created_at.isoformat()
        }
        for h in recent_activity_query
    ]

    stats = AdminDashboardStats(
        total_users=total_users,
        active_users=active_users,
        inactive_users=inactive_users,
        total_papers=total_papers,
        total_analyzed=total_analyzed,
        total_analyses=total_analyses,
        completed_analyses=completed_analyses,
        failed_analyses=failed_analyses,
        system_status="Operational",
        storage_used_mb=storage_used_mb,
        domain_distribution=domain_distribution,
        recent_users=recent_users,
        recent_activity=recent_activity
    )

    return StandardResponse(
        success=True,
        message="Admin dashboard statistics retrieved.",
        data=stats
    )
