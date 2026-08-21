from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class AnalysisHistoryResponse(BaseModel):
    id: int
    user_id: int
    paper_id: int
    analysis_id: int
    paper_title: str
    authors: str
    domain: str
    created_at: datetime
    user_name: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        from_attributes = True
