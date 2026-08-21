from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.analysis import Analysis
from app.models.result import ExtractedResult
from app.schemas.result import ExtractedResultResponse, VisualizationData
from app.schemas.common import StandardResponse

router = APIRouter(prefix="/results", tags=["Extracted Results & Visualizations"])

@router.get("/{analysis_id}", response_model=StandardResponse[VisualizationData])
def get_results_for_analysis(
    analysis_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Retrieve extracted numerical metrics and visualization payload for an analysis."""
    analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis with ID {analysis_id} not found."
        )

    if current_user.role != "ADMIN" and analysis.paper.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied."
        )

    results = db.query(ExtractedResult).filter(ExtractedResult.analysis_id == analysis_id).all()
    if not results or not bool(analysis.has_visualizations):
        return StandardResponse(
            success=True,
            message="No suitable numerical or comparative data was identified in this paper. Visualization was not generated.",
            data=VisualizationData(
                has_visualizations=False,
                message="No suitable numerical or comparative data was identified in this paper. Visualization was not generated.",
                chart_type="none",
                metrics_summary=[],
                series=[],
                table_rows=[]
            )
        )

    metrics_set = list({r.metric_name for r in results})
    series = [
        {
            "name": r.model_name,
            "value": r.metric_value,
            "metric": r.metric_name,
            "group": r.comparison_group
        }
        for r in results
    ]
    table_rows = [
        {
            "model": r.model_name,
            "metric": r.metric_name,
            "value": f"{r.metric_value}%" if r.metric_value <= 100 else str(r.metric_value),
            "benchmark": r.comparison_group
        }
        for r in results
    ]

    return StandardResponse(
        success=True,
        message="Visualizations data retrieved.",
        data=VisualizationData(
            has_visualizations=True,
            message="Metrics and model comparisons extracted.",
            chart_type="bar" if len(results) <= 8 else "comparison",
            metrics_summary=metrics_set,
            series=series,
            table_rows=table_rows
        )
    )
