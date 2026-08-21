import json
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.paper import ResearchPaper
from app.models.analysis import Analysis
from app.models.result import ExtractedResult
from app.services.analysis_service import AnalysisService, RESEARCH_DOMAINS_TAXONOMY
from app.schemas.analysis import AnalysisResponse, EasySummaryStructure, DomainExplanation, DomainUpdateRequest
from app.schemas.result import ExtractedResultResponse, VisualizationData
from app.schemas.common import StandardResponse

router = APIRouter(prefix="/analysis", tags=["AI & NLP Analysis"])

@router.get("/domains/taxonomy", response_model=StandardResponse[dict])
def get_domains_taxonomy():
    """Retrieve list of all 28 canonical research domains and descriptions."""
    return StandardResponse(
        success=True,
        message="Research domains taxonomy retrieved.",
        data={
            "domains": [
                {
                    "name": name,
                    "description": info["description"]
                }
                for name, info in RESEARCH_DOMAINS_TAXONOMY.items()
            ]
        }
    )

@router.post("/paper/{paper_id}", response_model=StandardResponse[dict])
def analyze_paper_endpoint(
    paper_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger AI/NLP analysis of an uploaded research paper."""
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Research paper with ID {paper_id} not found."
        )

    if current_user.role != "ADMIN" and paper.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to analyze this paper."
        )

    try:
        result = AnalysisService.analyze_paper(paper_id=paper_id, user_id=current_user.id, db=db)
        return StandardResponse(
            success=True,
            message="Paper analyzed successfully.",
            data=result
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to analyze the research paper: {str(e)}"
        )

@router.get("/{id}", response_model=StandardResponse[AnalysisResponse])
def get_analysis(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve full structured analysis report by Analysis ID."""
    analysis = db.query(Analysis).filter(Analysis.id == id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis report with ID {id} not found."
        )

    # Check permission
    if current_user.role != "ADMIN" and analysis.paper.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    # Parse keywords
    try:
        keywords = json.loads(analysis.keywords) if analysis.keywords else []
    except Exception:
        keywords = [k.strip() for k in analysis.keywords.split(",") if k.strip()] if analysis.keywords else []

    # Parse recommended domains
    try:
        recommended_domains = json.loads(analysis.recommended_domains) if analysis.recommended_domains else []
    except Exception:
        recommended_domains = ["Artificial Intelligence", "Machine Learning", "Data Science", "Computer Vision"]

    # Parse domain explanation
    try:
        raw_explanation = json.loads(analysis.domain_explanation) if analysis.domain_explanation else {}
        domain_explanation = DomainExplanation(**raw_explanation) if raw_explanation else None
    except Exception:
        domain_info = AnalysisService.get_domain_info(analysis.research_domain or "Computer Science")
        domain_explanation = DomainExplanation(**domain_info)

    if not domain_explanation:
        domain_info = AnalysisService.get_domain_info(analysis.research_domain or "Computer Science")
        domain_explanation = DomainExplanation(**domain_info)

    # Parse Easy Summary
    try:
        raw_summary = json.loads(analysis.easy_summary) if analysis.easy_summary else {}
        easy_summary = EasySummaryStructure(**raw_summary)
    except Exception:
        easy_summary = EasySummaryStructure(
            what_is_this_paper_about="Information not available in the paper.",
            what_problem_does_it_solve="Information not available in the paper.",
            why_was_the_research_conducted="Information not available in the paper.",
            how_was_it_performed="Information not available in the paper.",
            what_was_the_result="Information not available in the paper.",
            what_is_the_main_contribution="Information not available in the paper."
        )

    # Extracted results
    extracted_results = [
        ExtractedResultResponse.from_orm(r) for r in analysis.extracted_results
    ]

    # Build VisualizationData
    if bool(analysis.has_visualizations) and extracted_results:
        metrics_set = list({r.metric_name for r in extracted_results})
        series = [
            {
                "name": r.model_name,
                "value": r.metric_value,
                "metric": r.metric_name,
                "group": r.comparison_group
            }
            for r in extracted_results
        ]
        table_rows = [
            {
                "model": r.model_name,
                "metric": r.metric_name,
                "value": f"{r.metric_value}%" if r.metric_value <= 100 else str(r.metric_value),
                "benchmark": r.comparison_group
            }
            for r in extracted_results
        ]
        viz_data = VisualizationData(
            has_visualizations=True,
            message="Empirical metrics and model comparisons extracted from paper.",
            chart_type="bar" if len(extracted_results) <= 8 else "comparison",
            metrics_summary=metrics_set,
            series=series,
            table_rows=table_rows
        )
    else:
        viz_data = VisualizationData(
            has_visualizations=False,
            message="No suitable numerical or comparative data was identified in this paper. Visualization was not generated.",
            chart_type="none",
            metrics_summary=[],
            series=[],
            table_rows=[]
        )

    response_data = AnalysisResponse(
        id=analysis.id,
        paper_id=analysis.paper_id,
        paper_title=analysis.paper_title or "Untitled Research Paper",
        authors=analysis.authors or "Information not available in the paper.",
        publication_info=analysis.publication_info or "Information not available in the paper.",
        research_domain=analysis.research_domain or "Computer Science",
        document_type=analysis.document_type or "Research Paper",
        recommended_domains=recommended_domains,
        domain_explanation=domain_explanation,
        keywords=keywords,
        research_problem=analysis.research_problem or "Information not available in the paper.",
        motivation=analysis.motivation or "Information not available in the paper.",
        objective=analysis.objective or "Information not available in the paper.",
        proposed_solution=analysis.proposed_solution or "Information not available in the paper.",
        contribution=analysis.contribution or "Information not available in the paper.",
        methodology=analysis.methodology or "Methodology could not be reliably identified.",
        algorithms=analysis.algorithms or "Information not available in the paper.",
        technologies=analysis.technologies or "Information not available in the paper.",
        dataset=analysis.dataset or "Information not available in the paper.",
        experimental_setup=analysis.experimental_setup or "Information not available in the paper.",
        results=analysis.results or "Information not available in the paper.",
        key_findings=analysis.key_findings or "Information not available in the paper.",
        limitations=analysis.limitations or "Information not available in the paper.",
        future_work=analysis.future_work or "Information not available in the paper.",
        easy_summary=easy_summary,
        has_visualizations=bool(analysis.has_visualizations),
        extracted_results=extracted_results,
        visualization_data=viz_data,
        created_at=analysis.created_at
    )

    return StandardResponse(
        success=True,
        message="Analysis report retrieved successfully.",
        data=response_data
    )

@router.patch("/{id}/domain", response_model=StandardResponse[dict])
def update_analysis_domain(
    id: int,
    req: DomainUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Allow user to change or select a new research domain for the report."""
    analysis = db.query(Analysis).filter(Analysis.id == id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {id} not found."
        )

    if current_user.role != "ADMIN" and analysis.paper.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to modify this analysis."
        )

    new_domain = req.domain.strip()
    if not new_domain:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Domain name cannot be empty."
        )

    analysis.research_domain = new_domain
    if analysis.paper:
        analysis.paper.domain = new_domain

    # Update explanation
    domain_info = AnalysisService.get_domain_info(new_domain)
    analysis.domain_explanation = json.dumps(domain_info)

    db.commit()

    return StandardResponse(
        success=True,
        message=f"Research domain updated to '{new_domain}'.",
        data={
            "analysis_id": analysis.id,
            "research_domain": new_domain,
            "domain_explanation": domain_info
        }
    )

@router.delete("/{id}", response_model=StandardResponse[dict])
def delete_analysis(
    id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete an analysis report."""
    analysis = db.query(Analysis).filter(Analysis.id == id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {id} not found."
        )

    if current_user.role != "ADMIN" and analysis.paper.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this analysis."
        )

    paper_id = analysis.paper_id
    db.delete(analysis)
    db.commit()

    return StandardResponse(
        success=True,
        message="Analysis deleted successfully.",
        data={"deleted_analysis_id": id, "paper_id": paper_id}
    )
