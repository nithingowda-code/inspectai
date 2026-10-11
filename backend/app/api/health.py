from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def check_health():
    return {
        "status": "healthy",
        "service": "InspectAI Quality Inspection System",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
