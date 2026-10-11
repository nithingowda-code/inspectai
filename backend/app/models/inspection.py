import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    
    # Mode: 'dimensional', 'defect', 'reference', 'combined'
    mode = Column(String(50), nullable=False, default="combined")
    
    # Image file paths
    inspection_image_path = Column(String(512), nullable=False)
    annotated_image_path = Column(String(512), nullable=True)
    heatmap_image_path = Column(String(512), nullable=True)
    reference_image_path = Column(String(512), nullable=True)
    
    # Overall outcome: 'PASS', 'REVIEW', 'FAIL'
    overall_status = Column(String(20), nullable=False, index=True)
    overall_explanation = Column(Text, nullable=False)
    
    # Anomaly / Defect metrics
    anomaly_score = Column(Float, nullable=True)
    anomaly_threshold = Column(Float, nullable=True)
    anomaly_status = Column(String(20), nullable=True)  # PASS, REVIEW, FAIL, NOT_APPLICABLE
    
    # Dimensional metrics
    measured_length = Column(Float, nullable=True)
    measured_width = Column(Float, nullable=True)
    expected_length = Column(Float, nullable=True)
    expected_width = Column(Float, nullable=True)
    length_deviation = Column(Float, nullable=True)
    width_deviation = Column(Float, nullable=True)
    unit = Column(String(20), default="mm")
    dimensional_status = Column(String(20), nullable=True)
    
    # Reference Comparison metrics
    reference_similarity_score = Column(Float, nullable=True)
    reference_status = Column(String(20), nullable=True)
    
    # Detailed structured results (JSON strings)
    detected_defects_json = Column(Text, nullable=True, default="[]")
    checks_executed_json = Column(Text, nullable=True, default="[]")
    limitations_json = Column(Text, nullable=True, default="[]")
    metadata_json = Column(Text, nullable=True, default="{}")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    product = relationship("Product", back_populates="inspections")
