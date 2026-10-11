from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.app.database.session import get_db
from backend.app.models.inspection import InspectionRecord
from backend.app.models.product import Product, ProductReference
from backend.app.schemas.dashboard import DashboardStats
from backend.app.api.inspections import format_inspection_out
from backend.app.ml.feature_extractor import ResNet18FeatureExtractor

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(InspectionRecord).count()
    passed = db.query(InspectionRecord).filter(InspectionRecord.overall_status == "PASS").count()
    failed = db.query(InspectionRecord).filter(InspectionRecord.overall_status == "FAIL").count()
    review = db.query(InspectionRecord).filter(InspectionRecord.overall_status == "REVIEW").count()
    
    pass_rate = round((passed / total * 100.0), 1) if total > 0 else 0.0

    products_count = db.query(Product).count()
    references_count = db.query(ProductReference).count()

    # Recent inspections (up to 6)
    recent = db.query(InspectionRecord).order_by(InspectionRecord.created_at.desc()).limit(6).all()
    recent_outs = [format_inspection_out(r) for r in recent]

    # Category distribution of products
    categories = db.query(Product.category, func.count(Product.id)).group_by(Product.category).all()
    cat_dist = {cat: count for cat, count in categories}

    # Daily trend (last 7 days from records)
    now = datetime.utcnow()
    trend = []
    for i in range(6, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())
        
        day_total = db.query(InspectionRecord).filter(
            InspectionRecord.created_at >= day_start,
            InspectionRecord.created_at <= day_end
        ).count()
        day_passed = db.query(InspectionRecord).filter(
            InspectionRecord.created_at >= day_start,
            InspectionRecord.created_at <= day_end,
            InspectionRecord.overall_status == "PASS"
        ).count()
        day_failed = db.query(InspectionRecord).filter(
            InspectionRecord.created_at >= day_start,
            InspectionRecord.created_at <= day_end,
            InspectionRecord.overall_status == "FAIL"
        ).count()
        day_review = db.query(InspectionRecord).filter(
            InspectionRecord.created_at >= day_start,
            InspectionRecord.created_at <= day_end,
            InspectionRecord.overall_status == "REVIEW"
        ).count()

        trend.append({
            "date": day_date.strftime("%b %d"),
            "total": day_total,
            "pass": day_passed,
            "fail": day_failed,
            "review": day_review
        })

    extractor = ResNet18FeatureExtractor.get_instance()

    return DashboardStats(
        total_inspections=total,
        passed_inspections=passed,
        failed_inspections=failed,
        review_inspections=review,
        pass_rate=pass_rate,
        registered_products_count=products_count,
        total_references_count=references_count,
        model_ready=True,
        model_device=extractor.device_name,
        recent_inspections=recent_outs,
        category_distribution=cat_dist,
        daily_trend=trend
    )
