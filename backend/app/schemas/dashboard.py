from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from app.schemas.paper import ResearchPaperResponse
from app.schemas.history import AnalysisHistoryResponse

class DomainStat(BaseModel):
    domain: str
    count: int

class UserDashboardStats(BaseModel):
    total_papers: int
    total_analyzed: int
    total_processing: int
    total_failed: int
    recent_papers: List[ResearchPaperResponse]
    recent_analyses: List[AnalysisHistoryResponse]
    domain_distribution: List[DomainStat]
    metrics_summary: Dict[str, Any]

class AdminDashboardStats(BaseModel):
    total_users: int
    active_users: int
    inactive_users: int
    total_papers: int
    total_analyzed: int
    total_analyses: int
    completed_analyses: int
    failed_analyses: int
    system_status: str
    storage_used_mb: float
    domain_distribution: List[DomainStat]
    recent_users: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]
