from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class ExtractedResultBase(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    metric_name: str
    metric_value: float
    model_name: str
    comparison_group: Optional[str] = "Default Evaluation"

class ExtractedResultCreate(ExtractedResultBase):
    analysis_id: int

class ExtractedResultResponse(ExtractedResultBase):
    id: int
    analysis_id: int

    class Config:
        from_attributes = True

class VisualizationData(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    has_visualizations: bool
    message: Optional[str] = None
    chart_type: str = "bar"  # "bar", "comparison", "line", "table"
    metrics_summary: List[str] = []
    series: List[dict] = []
    table_rows: List[dict] = []
