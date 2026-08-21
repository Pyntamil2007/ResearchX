from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database.database import Base

class ExtractedResult(Base):
    __tablename__ = "extracted_results"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    analysis_id = Column(Integer, ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)  # e.g. "Accuracy", "F1 Score", "BLEU", "Latency"
    metric_value = Column(Float, nullable=False)        # e.g. 94.5
    model_name = Column(String(150), nullable=False)    # e.g. "Proposed ResNet-50", "VGG-16 Baseline"
    comparison_group = Column(String(150), nullable=True) # e.g. "ImageNet Top-1 Accuracy", "GLUE Benchmark"

    # Relationships
    analysis = relationship("Analysis", back_populates="extracted_results")

    def __repr__(self):
        return f"<ExtractedResult model='{self.model_name}' metric='{self.metric_name}' value={self.metric_value}>"
