from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel
from app.schemas.result import ExtractedResultResponse, VisualizationData

class EasySummaryStructure(BaseModel):
    what_is_this_paper_about: str
    what_problem_does_it_solve: str
    why_was_the_research_conducted: str
    how_was_it_performed: str
    what_was_the_result: str
    what_is_the_main_contribution: str

class DomainExplanation(BaseModel):
    description: str
    why_this_domain: str

class DomainUpdateRequest(BaseModel):
    domain: str

class AnalysisBase(BaseModel):
    # 1. Paper Overview
    paper_title: Optional[str] = "Information not available in the paper."
    authors: Optional[str] = "Information not available in the paper."
    publication_info: Optional[str] = "Information not available in the paper."
    research_domain: Optional[str] = "Computer Science"
    document_type: Optional[str] = "Research Paper"
    recommended_domains: Optional[List[str]] = []
    domain_explanation: Optional[DomainExplanation] = None
    keywords: Optional[List[str]] = []
    
    # 2. Research Understanding
    research_problem: Optional[str] = "Information not available in the paper."
    motivation: Optional[str] = "Information not available in the paper."
    objective: Optional[str] = "Information not available in the paper."
    proposed_solution: Optional[str] = "Information not available in the paper."
    contribution: Optional[str] = "Information not available in the paper."
    
    # 3. Methodology
    methodology: Optional[str] = "Information not available in the paper."
    algorithms: Optional[str] = "Information not available in the paper."
    technologies: Optional[str] = "Information not available in the paper."
    dataset: Optional[str] = "Information not available in the paper."
    experimental_setup: Optional[str] = "Information not available in the paper."
    
    # 4. Results & Findings
    results: Optional[str] = "Information not available in the paper."
    key_findings: Optional[str] = "Information not available in the paper."
    
    # 5. Conclusion & Future
    limitations: Optional[str] = "Information not available in the paper."
    future_work: Optional[str] = "Information not available in the paper."
    
    # 6. Easy Summary
    easy_summary: Optional[EasySummaryStructure] = None
    has_visualizations: Optional[bool] = False

class AnalysisCreate(BaseModel):
    paper_id: int

class AnalysisResponse(BaseModel):
    id: int
    paper_id: int
    
    # 1. Paper Overview
    paper_title: str
    authors: str
    publication_info: str
    research_domain: str
    document_type: str = "Research Paper"
    recommended_domains: List[str] = []
    domain_explanation: Optional[DomainExplanation] = None
    keywords: List[str]
    
    # 2. Research Understanding
    research_problem: str
    motivation: str
    objective: str
    proposed_solution: str
    contribution: str
    
    # 3. Methodology
    methodology: str
    algorithms: str
    technologies: str
    dataset: str
    experimental_setup: str
    
    # 4. Results & Findings
    results: str
    key_findings: str
    
    # 5. Conclusion & Future
    limitations: str
    future_work: str
    
    # 6. Easy Summary
    easy_summary: EasySummaryStructure
    
    # 7. Results & Visualizations
    has_visualizations: bool
    extracted_results: List[ExtractedResultResponse] = []
    visualization_data: Optional[VisualizationData] = None
    
    created_at: datetime

    class Config:
        from_attributes = True
