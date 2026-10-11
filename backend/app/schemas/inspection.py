from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class DefectItem(BaseModel):
    id: str
    type: str  # scratch, crack, tear, hole, dent, surface_irregularity, missing_component, dimension_anomaly
    severity: str  # low, medium, high, critical
    location: Optional[Dict[str, Any]] = None  # bounding box {x, y, width, height}
    confidence: float
    description: str

class CheckResult(BaseModel):
    check_name: str
    executed: bool
    status: str  # PASS, REVIEW, FAIL, SKIPPED
    score_or_value: Optional[float] = None
    threshold_or_tolerance: Optional[str] = None
    explanation: str
    limitations: Optional[str] = None

class InspectionRunRequest(BaseModel):
    product_id: Optional[str] = None
    mode: str = "combined"  # 'dimensional', 'defect', 'reference', 'combined'
    calibration_factor: Optional[float] = None  # override pixels_per_unit if supplied
    custom_expected_length: Optional[float] = None
    custom_expected_width: Optional[float] = None
    custom_tolerance: Optional[float] = None

class InspectionRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    mode: str
    inspection_image_path: str
    annotated_image_path: Optional[str] = None
    heatmap_image_path: Optional[str] = None
    reference_image_path: Optional[str] = None
    
    overall_status: str  # PASS, REVIEW, FAIL
    overall_explanation: str
    
    anomaly_score: Optional[float] = None
    anomaly_threshold: Optional[float] = None
    anomaly_status: Optional[str] = None
    
    measured_length: Optional[float] = None
    measured_width: Optional[float] = None
    expected_length: Optional[float] = None
    expected_width: Optional[float] = None
    length_deviation: Optional[float] = None
    width_deviation: Optional[float] = None
    unit: str
    dimensional_status: Optional[str] = None
    
    reference_similarity_score: Optional[float] = None
    reference_status: Optional[str] = None
    
    detected_defects: List[DefectItem] = []
    checks_executed: List[CheckResult] = []
    limitations: List[str] = []
    metadata: Dict[str, Any] = {}
    
    created_at: datetime
