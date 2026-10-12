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
from backend.app.ml.direct_comparator import compare_images
from backend.app.vision.compare import run_two_image_comparison
from backend.app.models.product import ProductReference

router = APIRouter(prefix="/inspections", tags=["Inspections"])

def format_inspection_out(rec: InspectionRecord) -> InspectionRecordOut:
    raw_defects = json.loads(rec.detected_defects_json or "[]")
    defects = []
    for idx, d in enumerate(raw_defects):
        if "id" not in d:
            d["id"] = f"DEF-{idx+1:03d}"
        defects.append(DefectItem(**d))
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


@router.post("/compare")
async def run_comparison(
    reference_file: UploadFile = File(..., description="Good / golden reference image"),
    inspection_file: UploadFile = File(..., description="Inspection / possibly broken image"),
    expected_length: Optional[float] = Form(None),
    expected_width: Optional[float] = Form(None),
    pos_tolerance: Optional[float] = Form(None),
    neg_tolerance: Optional[float] = Form(None),
    unit: str = Form("mm"),
    scale_method: str = Form("same_setup"),
    db: Session = Depends(get_db)
):
    """
    Directly compares a reference image (ideal product) against an inspection image
    (test / defective product) through the 6-stage universal CV comparison engine:
    validation -> segmentation -> SIFT/contour alignment -> difference signals -> scoring -> output.
    Persists the inspection record in SQLite database so it appears in history and reports.
    """
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/bmp"]
    for up_file, label in [(reference_file, "reference"), (inspection_file, "inspection")]:
        if up_file.content_type not in allowed_types:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid {label} image format. Supported: JPEG, PNG, WEBP, BMP"
            )

    uploads_dir = os.path.join(DATA_DIR, "uploads")
    os.makedirs(uploads_dir, exist_ok=True)

    comparison_id = uuid.uuid4().hex[:12]

    # Save reference image
    ref_ext = os.path.splitext(reference_file.filename or "")[1] or ".jpg"
    ref_path = os.path.join(uploads_dir, f"ref_{comparison_id}{ref_ext}")
    ref_contents = await reference_file.read()
    with open(ref_path, "wb") as f:
        f.write(ref_contents)

    # Save inspection image
    insp_ext = os.path.splitext(inspection_file.filename or "")[1] or ".jpg"
    insp_path = os.path.join(uploads_dir, f"insp_{comparison_id}{insp_ext}")
    insp_contents = await inspection_file.read()
    with open(insp_path, "wb") as f:
        f.write(insp_contents)

    # Run the 6-stage comparison pipeline
    result = run_two_image_comparison(
        ideal_image_path=ref_path,
        test_image_path=insp_path,
        output_dir=uploads_dir,
        comparison_id=comparison_id,
        scale_method=scale_method,
        expected_length=expected_length,
        expected_width=expected_width,
        pos_tolerance=pos_tolerance,
        neg_tolerance=neg_tolerance,
        unit=unit
    )

    img_paths = result.get("image_paths", {})
    heatmap_path = img_paths.get("heatmap_path")
    sidebyside_path = img_paths.get("sidebyside_path")
    overlay_path = img_paths.get("overlay_path")
    annotated_path = img_paths.get("annotated_path")

    # Map defects format for persistent record
    defects_for_db = []
    for reg in result.get("detected_regions", []):
        defects_for_db.append({
            "id": reg.get("id", f"DIFF-{len(defects_for_db)+1:03d}"),
            "type": reg.get("category", "structural_change"),
            "severity": reg.get("severity", "medium"),
            "location": reg.get("location", {}),
            "area_px": reg.get("area_px", 0),
            "confidence": reg.get("confidence", 0.8),
            "description": f"{reg.get('id')}: {reg.get('classification')}"
        })

    dims = result.get("dimensions", {})
    record = InspectionRecord(
        id=str(uuid.uuid4()),
        product_id=None,
        mode="quick_compare",
        inspection_image_path=insp_path,
        reference_image_path=ref_path,
        heatmap_image_path=heatmap_path,
        annotated_image_path=annotated_path or sidebyside_path,
        overall_status=result["overall_status"],
        overall_explanation=result["overall_explanation"],
        anomaly_score=float(result.get("difference_index", 0.0)) / 100.0,
        anomaly_threshold=0.35,
        anomaly_status="PASS" if result["overall_status"] == "PASS" else ("FAIL" if result["overall_status"] == "FAIL" else "REVIEW"),
        measured_length=dims.get("measured_length"),
        measured_width=dims.get("measured_width"),
        expected_length=dims.get("expected_length"),
        expected_width=dims.get("expected_width"),
        length_deviation=dims.get("length_deviation"),
        width_deviation=dims.get("width_deviation"),
        unit=unit,
        dimensional_status=dims.get("tolerance_status"),
        reference_similarity_score=float(result.get("similarity_index", 0.0)) / 100.0,
        reference_status="PASS" if result.get("similarity_index", 0.0) >= 80.0 else "REVIEW",
        detected_defects_json=json.dumps(defects_for_db),
        checks_executed_json=json.dumps(result.get("checks_executed", [])),
        limitations_json=json.dumps(result.get("limitations", [])),
        metadata_json=json.dumps({
            "comparison_id": comparison_id,
            "difference_index": result.get("difference_index"),
            "similarity_index": result.get("similarity_index"),
            "sub_scores": result.get("sub_scores"),
            "alignment_quality": result.get("alignment_quality"),
            "scale_method": scale_method,
            "sidebyside_path": sidebyside_path,
            "overlay_path": overlay_path
        })
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    def _to_url(path: str | None) -> str | None:
        if not path:
            return None
        idx = path.find("/data/")
        return path[idx:] if idx != -1 else None

    return {
        "comparison_id": comparison_id,
        "inspection_id": record.id,
        "reference_image_url": _to_url(ref_path),
        "inspection_image_url": _to_url(insp_path),
        "heatmap_image_url": _to_url(heatmap_path) if heatmap_path and os.path.exists(heatmap_path) else None,
        "sidebyside_image_url": _to_url(sidebyside_path) if sidebyside_path and os.path.exists(sidebyside_path) else None,
        "overlay_image_url": _to_url(overlay_path) if overlay_path and os.path.exists(overlay_path) else None,
        "annotated_image_url": _to_url(annotated_path) if annotated_path and os.path.exists(annotated_path) else None,
        "overall_status": result["overall_status"],
        "overall_explanation": result["overall_explanation"],
        "difference_index": result["difference_index"],
        "similarity_index": result["similarity_index"],
        "sub_scores": result["sub_scores"],
        "score_disclaimer": result["score_disclaimer"],
        "dimensions": result["dimensions"],
        "detected_regions": result["detected_regions"],
        "checks_executed": result["checks_executed"],
        "limitations": result["limitations"],
        "alignment_quality": result["alignment_quality"]
    }


@router.post("/save-product-from-comparison")
def save_product_from_comparison(
    comparison_id: str = Form(...),
    name: str = Form(...),
    category: str = Form("General"),
    description: str = Form(""),
    expected_length: Optional[float] = Form(None),
    expected_width: Optional[float] = Form(None),
    pos_tolerance: Optional[float] = Form(2.0),
    neg_tolerance: Optional[float] = Form(2.0),
    unit: str = Form("mm"),
    db: Session = Depends(get_db)
):
    """
    Saves the ideal/reference image from a Quick Compare run as a permanent registered product.
    """
    uploads_dir = os.path.join(DATA_DIR, "uploads")
    ref_files = [f for f in os.listdir(uploads_dir) if f.startswith(f"ref_{comparison_id}")]
    if not ref_files:
        raise HTTPException(status_code=404, detail="Reference image for comparison not found")

    ref_src = os.path.join(uploads_dir, ref_files[0])
    prod_id = str(uuid.uuid4())

    new_prod = Product(
        id=prod_id,
        name=name,
        category=category,
        description=description,
        expected_length=expected_length or 100.0,
        expected_width=expected_width or 50.0,
        pos_tolerance=pos_tolerance or 2.0,
        neg_tolerance=neg_tolerance or 2.0,
        unit=unit,
        calibration_factor=10.0
    )
    db.add(new_prod)

    ref_dir = os.path.join(DATA_DIR, "references")
    os.makedirs(ref_dir, exist_ok=True)
    dest_filename = f"prod_{prod_id}_{ref_files[0]}"
    dest_path = os.path.join(ref_dir, dest_filename)

    with open(ref_src, "rb") as sf, open(dest_path, "wb") as df:
        df.write(sf.read())

    ref_record = ProductReference(
        product_id=prod_id,
        filename=dest_filename,
        file_path=dest_path,
        is_primary=True
    )
    db.add(ref_record)
    db.commit()
    db.refresh(new_prod)

    return {"status": "success", "product_id": new_prod.id, "name": new_prod.name}



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
