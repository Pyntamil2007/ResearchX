from datetime import datetime
from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id", ondelete="CASCADE"), nullable=False, index=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="history")
    paper = relationship("ResearchPaper", back_populates="history")
    analysis = relationship("Analysis", back_populates="history")

    def __repr__(self):
        return f"<AnalysisHistory id={self.id} user_id={self.user_id} paper_id={self.paper_id}>"
