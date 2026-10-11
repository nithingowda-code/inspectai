import os
import uuid
import json
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.orm import Session

from backend.app.database.session import get_db, DATA_DIR
from backend.app.models.inspection import InspectionRecord
from backend.app.models.product import Product
from backend.app.schemas.inspection import InspectionRecordOut, DefectItem, CheckResult
from backend.app.services.inspection_engine import InspectionEngine
from backend.app.services.report_generator import generate_pdf_report

router = APIRouter(prefix="/inspections", tags=["Inspections"])

def format_inspection_out(rec: InspectionRecord) -> InspectionRecordOut:
    defects = [DefectItem(**d) for d in json.loads(rec.detected_defects_json or "[]")]
    checks = [CheckResult(**c) for c in json.loads(rec.checks_executed_json or "[]")]
    limitations = json.loads(rec.limitations_json or "[]")
    meta = json.loads(rec.metadata_json or "{}")

    product_name = rec.product.name if rec.product else "Standalone Inspection"

    return InspectionRecordOut(
        id=rec.id,
        product_id=rec.product_id,
        product_name=product_name,
        mode=rec.mode,
        inspection_image_path=rec.inspection_image_path,
        annotated_image_path=rec.annotated_image_path,
        heatmap_image_path=rec.heatmap_image_path,
        reference_image_path=rec.reference_image_path,
        overall_status=rec.overall_status,
        overall_explanation=rec.overall_explanation,
        anomaly_score=rec.anomaly_score,
        anomaly_threshold=rec.anomaly_threshold,
        anomaly_status=rec.anomaly_status,
        measured_length=rec.measured_length,
        measured_width=rec.measured_width,
        expected_length=rec.expected_length,
        expected_width=rec.expected_width,
        length_deviation=rec.length_deviation,
        width_deviation=rec.width_deviation,
        unit=rec.unit,
        dimensional_status=rec.dimensional_status,
        reference_similarity_score=rec.reference_similarity_score,
        reference_status=rec.reference_status,
        detected_defects=defects,
        checks_executed=checks,
        limitations=limitations,
        metadata=meta,
        created_at=rec.created_at
    )

@router.post("/run", response_model=InspectionRecordOut, status_code=status.HTTP_201_CREATED)
async def run_inspection(
    file: UploadFile = File(...),
    product_id: Optional[str] = Form(None),
    mode: str = Form("combined"),
    calibration_factor: Optional[float] = Form(None),
    custom_expected_length: Optional[float] = Form(None),
    custom_expected_width: Optional[float] = Form(None),
    custom_tolerance: Optional[float] = Form(None),
    db: Session = Depends(get_db)
):
    # Validate image upload
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/bmp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid image file format. Supported: JPEG, PNG, WEBP, BMP")

    if mode not in ["dimensional", "defect", "reference", "combined"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Choose dimensional, defect, reference, or combined")

    # If product_id supplied, check existence
    if product_id:
        p = db.query(Product).filter(Product.id == product_id).first()
        if not p:
            raise HTTPException(status_code=404, detail="Selected product does not exist")

    uploads_dir = os.path.join(DATA_DIR, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    safe_filename = f"insp_{uuid.uuid4().hex[:12]}{ext}"
    dest_path = os.path.join(uploads_dir, safe_filename)

    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    # Execute inspection engine
    record = InspectionEngine.run_inspection(
        db=db,
        inspection_image_path=dest_path,
        product_id=product_id if product_id and product_id.strip() else None,
        mode=mode,
        custom_calibration_factor=calibration_factor,
        custom_expected_length=custom_expected_length,
        custom_expected_width=custom_expected_width,
        custom_tolerance=custom_tolerance
    )

    return format_inspection_out(record)

@router.get("", response_model=List[InspectionRecordOut])
def list_inspections(
    product_id: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    mode_filter: Optional[str] = Query(None, alias="mode"),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    query = db.query(InspectionRecord)

    if product_id:
        query = query.filter(InspectionRecord.product_id == product_id)
    if status_filter:
        query = query.filter(InspectionRecord.overall_status == status_filter.upper())
    if mode_filter:
        query = query.filter(InspectionRecord.mode == mode_filter.lower())
    if search:
        # Search in ID, explanation, or linked product name
        query = query.outerjoin(Product).filter(
            (InspectionRecord.id.ilike(f"%{search}%")) |
            (InspectionRecord.overall_explanation.ilike(f"%{search}%")) |
            (Product.name.ilike(f"%{search}%"))
        )

    records = query.order_by(InspectionRecord.created_at.desc()).offset(offset).limit(limit).all()
    return [format_inspection_out(r) for r in records]

@router.get("/{inspection_id}", response_model=InspectionRecordOut)
def get_inspection(inspection_id: str, db: Session = Depends(get_db)):
    rec = db.query(InspectionRecord).filter(InspectionRecord.id == inspection_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Inspection record not found")
    return format_inspection_out(rec)

@router.get("/{inspection_id}/report")
def download_inspection_report_pdf(inspection_id: str, db: Session = Depends(get_db)):
    rec = db.query(InspectionRecord).filter(InspectionRecord.id == inspection_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Inspection record not found")

    p_name = rec.product.name if rec.product else "Standalone Inspection"
    pdf_path = generate_pdf_report(rec, product_name=p_name)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=500, detail="Failed to locate generated PDF report file")

    return FileResponse(
        pdf_path,
        media_type="application/pdf",
        filename=f"InspectAI_Report_{rec.id[:8]}.pdf"
    )

@router.get("/{inspection_id}/report/json")
def download_inspection_report_json(inspection_id: str, db: Session = Depends(get_db)):
    rec = db.query(InspectionRecord).filter(InspectionRecord.id == inspection_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Inspection record not found")

    formatted = format_inspection_out(rec)
    return JSONResponse(content=formatted.model_dump(mode="json"))
