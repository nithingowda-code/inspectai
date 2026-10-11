from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.schemas.inspection import InspectionRecordOut

class DashboardStats(BaseModel):
    total_inspections: int
    passed_inspections: int
    failed_inspections: int
    review_inspections: int
    pass_rate: float
    registered_products_count: int
    total_references_count: int
    model_ready: bool
    model_device: str
    recent_inspections: List[InspectionRecordOut]
    category_distribution: Dict[str, int]
    daily_trend: List[Dict[str, Any]]
