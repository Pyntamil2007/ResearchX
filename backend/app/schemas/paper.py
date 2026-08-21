from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field

class ResearchPaperBase(BaseModel):
    title: str = "Untitled Research Paper"
    authors: Optional[str] = "Information not available in the paper."
    domain: Optional[str] = "Computer Science"
    document_type: Optional[str] = "Research Paper"

class ResearchPaperCreate(ResearchPaperBase):
    pass

class ResearchPaperUpdate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    domain: Optional[str] = None
    document_type: Optional[str] = None

class ResearchPaperResponse(ResearchPaperBase):
    id: int
    user_id: int
    file_name: str
    file_path: str
    status: str
    uploaded_at: datetime
    document_type: str = "Research Paper"
    has_analysis: bool = False
    latest_analysis_id: Optional[int] = None
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True

class PaperFilterParams(BaseModel):
    search: Optional[str] = None
    domain: Optional[str] = None
    status: Optional[str] = None
    sort_by: Optional[str] = "newest"  # "newest", "oldest", "alphabetical"
    page: int = 1
    limit: int = 10
