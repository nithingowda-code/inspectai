from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ModelStatusOut(BaseModel):
    is_ready: bool
    model_name: str
    architecture: str
    backbone: str
    embedding_dim: int
    device: str
    device_name: str
    weights_status: str
    total_reference_banks: int
    total_reference_embeddings: int
    supported_defect_types: list[str]
    last_evaluated_at: Optional[datetime] = None
    evaluation_metrics: Dict[str, Any] = {}
    training_instructions: str
