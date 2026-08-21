from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class ResearchPaper(Base):
    __tablename__ = "research_papers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False, default="Untitled Research Paper")
    authors = Column(String(255), nullable=True, default="Information not available in the paper.")
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    domain = Column(String(100), nullable=False, default="Computer Science")
    document_type = Column(String(100), nullable=False, default="Research Paper")  # Research Paper, Academic Book / Document, etc.
    status = Column(String(50), nullable=False, default="Uploaded")  # Uploaded, Processing, Analyzed, Failed
    raw_text = Column(Text, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="papers")
    analyses = relationship("Analysis", back_populates="paper", cascade="all, delete-orphan")
    history = relationship("AnalysisHistory", back_populates="paper", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ResearchPaper id={self.id} title='{self.title[:30]}' status='{self.status}'>"
