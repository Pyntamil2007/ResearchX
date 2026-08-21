from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # 1. Paper Overview
    paper_title = Column(String(255), nullable=True)
    authors = Column(String(255), nullable=True)
    publication_info = Column(String(255), nullable=True)
    research_domain = Column(String(100), nullable=True)
    document_type = Column(String(100), nullable=True, default="Research Paper")
    recommended_domains = Column(Text, nullable=True)  # JSON list of recommended domain names
    domain_explanation = Column(Text, nullable=True)  # JSON dict with description & why_this_domain
    keywords = Column(Text, nullable=True)  # JSON list of strings or comma-separated
    
    # 2. Research Understanding
    research_problem = Column(Text, nullable=True)
    motivation = Column(Text, nullable=True)
    objective = Column(Text, nullable=True)
    proposed_solution = Column(Text, nullable=True)
    contribution = Column(Text, nullable=True)
    
    # 3. Methodology
    methodology = Column(Text, nullable=True)
    algorithms = Column(Text, nullable=True)
    technologies = Column(Text, nullable=True)
    dataset = Column(Text, nullable=True)
    experimental_setup = Column(Text, nullable=True)
    
    # 4. Results & Findings
    results = Column(Text, nullable=True)
    key_findings = Column(Text, nullable=True)
    
    # 5. Conclusion & Future
    limitations = Column(Text, nullable=True)
    future_work = Column(Text, nullable=True)
    
    # 6. Easy Summary (6 structured beginner Q&A stored as JSON string or text)
    easy_summary = Column(Text, nullable=True)
    
    # 7. Visualization flag and metadata
    has_visualizations = Column(Integer, default=0, nullable=False)  # 0 or 1
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    paper = relationship("ResearchPaper", back_populates="analyses")
    extracted_results = relationship("ExtractedResult", back_populates="analysis", cascade="all, delete-orphan")
    history = relationship("AnalysisHistory", back_populates="analysis", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Analysis id={self.id} paper_id={self.paper_id}>"
