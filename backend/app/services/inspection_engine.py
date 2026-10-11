import os
import uuid
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.app.models.product import Product
from backend.app.models.inspection import InspectionRecord
from backend.app.vision.measurement import analyze_dimensions
from backend.app.ml.anomaly_detector import analyze_anomalies_and_defects, DEFAULT_ANOMALY_THRESHOLD
from backend.app.database.session import BASE_DIR, DATA_DIR

class InspectionEngine:
    @staticmethod
    def run_inspection(
        db: Session,
        inspection_image_path: str,
        product_id: Optional[str] = None,
        mode: str = "combined",
        custom_calibration_factor: Optional[float] = None,
        custom_expected_length: Optional[float] = None,
        custom_expected_width: Optional[float] = None,
        custom_tolerance: Optional[float] = None
    ) -> InspectionRecord:
        """
        Coordinates optical metrology, defect detection, and reference comparison.
        Enforces deterministic decision rules:
          - FAIL: if any validated required check identifies an out-of-tolerance measurement or supported defect.
          - REVIEW: if a required check fails/cannot execute, confidence is insufficient, or the image is unsuitable.
          - PASS: ONLY if all required checks succeed and meet acceptance criteria.
        """
        inspection_id = str(uuid.uuid4())
        uploads_dir = os.path.join(DATA_DIR, "uploads")
        os.makedirs(uploads_dir, exist_ok=True)

        annotated_path = os.path.join(uploads_dir, f"annotated_{inspection_id}.jpg")
        heatmap_path = os.path.join(uploads_dir, f"heatmap_{inspection_id}.jpg")

        # Load product details if registered
        product = None
        if product_id:
            product = db.query(Product).filter(Product.id == product_id).first()

        # Dimension expectations
        unit = product.unit if product else "mm"
        exp_len = custom_expected_length or (product.expected_length if product else 100.0)
        exp_wid = custom_expected_width or (product.expected_width if product else 50.0)
        pos_tol = custom_tolerance or (product.pos_tolerance if product else 2.0)
        neg_tol = custom_tolerance or (product.neg_tolerance if product else 2.0)
        calib_factor = custom_calibration_factor or (product.calibration_factor if product else 10.0)

        checks_executed = []
        limitations = []
        detected_defects = []

        # Individual check results
        dim_res = None
        anomaly_res = None
        ref_image_path = None

        # Determine which checks run based on mode:
        # 'dimensional', 'defect', 'reference', 'combined'
        run_dim = mode in ["dimensional", "combined"]
        run_defect = mode in ["defect", "combined"]
        run_ref = mode in ["reference", "combined"]

        # 1. Optical Metrology (Dimensional Measurement)
        if run_dim:
            dim_res = analyze_dimensions(
                image_path=inspection_image_path,
                output_annotated_path=annotated_path,
                expected_length=exp_len,
                expected_width=exp_wid,
                pos_tolerance=pos_tol,
                neg_tolerance=neg_tol,
                calibration_factor=calib_factor,
                unit=unit
            )
            checks_executed.append({
                "check_name": "Dimensional Optical Metrology",
                "executed": dim_res["executed"],
                "status": dim_res["status"],
                "score_or_value": dim_res["measured_length"],
                "threshold_or_tolerance": f"L:{exp_len}±{pos_tol}{unit}, W:{exp_wid}±{pos_tol}{unit}",
                "explanation": dim_res["explanation"],
                "limitations": "; ".join(dim_res.get("limitations", []))
            })
            limitations.extend(dim_res.get("limitations", []))

        # 2. Defect & Anomaly Detection + Reference Comparison
        if run_defect or run_ref:
            anomaly_res = analyze_anomalies_and_defects(
                inspection_image_path=inspection_image_path,
                output_heatmap_path=heatmap_path,
                product_id=product_id if product else None,
                threshold=DEFAULT_ANOMALY_THRESHOLD
            )
            detected_defects = anomaly_res.get("defects", [])
            ref_image_path = anomaly_res.get("best_ref_path")

            checks_executed.append({
                "check_name": "Deep Feature & Surface Defect Analysis",
                "executed": anomaly_res["executed"],
                "status": anomaly_res["status"],
                "score_or_value": anomaly_res["anomaly_score"],
                "threshold_or_tolerance": f"Max Anomaly Threshold: {DEFAULT_ANOMALY_THRESHOLD:.2f}",
                "explanation": anomaly_res["explanation"],
                "limitations": "; ".join(anomaly_res.get("limitations", []))
            })
            limitations.extend(anomaly_res.get("limitations", []))

            if run_ref:
                sim_status = "PASS" if (anomaly_res.get("similarity_score") or 0) > 0.70 else ("REVIEW" if not product or not product.references else "FAIL")
                sim_val = anomaly_res.get("similarity_score")
                checks_executed.append({
                    "check_name": "Golden Reference Pattern Consistency",
                    "executed": bool(sim_val is not None),
                    "status": sim_status,
                    "score_or_value": sim_val,
                    "threshold_or_tolerance": "Min Similarity: 0.70",
                    "explanation": f"Visual cosine similarity score with registered golden reference: {sim_val if sim_val is not None else 'No Reference Registered'}",
                    "limitations": "Subject to illumination and orientation variation between sample and references."
                })

        # Deduplicate limitations
        limitations = list(dict.fromkeys(limitations))

        # 3. Overall Decision Synthesis (Strict Quality Control Logic)
        statuses = [check["status"] for check in checks_executed]
        all_executed = all(check["executed"] for check in checks_executed)

        if not all_executed or not checks_executed:
            overall_status = "REVIEW"
            overall_explanation = "One or more required inspection routines could not be executed reliably. Inspection requires operator review."
        elif "FAIL" in statuses:
            overall_status = "FAIL"
            failed_checks = [c["check_name"] for c in checks_executed if c["status"] == "FAIL"]
            overall_explanation = f"Critical inspection criteria failed in: {', '.join(failed_checks)}."
        elif "REVIEW" in statuses:
            overall_status = "REVIEW"
            review_checks = [c["check_name"] for c in checks_executed if c["status"] == "REVIEW"]
            overall_explanation = f"Uncertain inspection conditions or missing baseline in: {', '.join(review_checks)}. Manual inspection required."
        elif all(s == "PASS" for s in statuses):
            overall_status = "PASS"
            overall_explanation = "All quality parameters, dimensional tolerances, and defect thresholds met design specifications."
        else:
            overall_status = "REVIEW"
            overall_explanation = "Inconclusive results. Operator review mandated."

        # Create Persistent Inspection Record
        record = InspectionRecord(
            id=inspection_id,
            product_id=product_id,
            mode=mode,
            inspection_image_path=inspection_image_path,
            annotated_image_path=annotated_path if run_dim and os.path.exists(annotated_path) else None,
            heatmap_image_path=heatmap_path if (run_defect or run_ref) and os.path.exists(heatmap_path) else None,
            reference_image_path=ref_image_path,
            overall_status=overall_status,
            overall_explanation=overall_explanation,
            # Anomaly details
            anomaly_score=anomaly_res.get("anomaly_score") if anomaly_res else None,
            anomaly_threshold=DEFAULT_ANOMALY_THRESHOLD if anomaly_res else None,
            anomaly_status=anomaly_res.get("status") if anomaly_res else None,
            # Dimensional details
            measured_length=dim_res.get("measured_length") if dim_res else None,
            measured_width=dim_res.get("measured_width") if dim_res else None,
            expected_length=exp_len if run_dim else None,
            expected_width=exp_wid if run_dim else None,
            length_deviation=dim_res.get("length_deviation") if dim_res else None,
            width_deviation=dim_res.get("width_deviation") if dim_res else None,
            unit=unit,
            dimensional_status=dim_res.get("status") if dim_res else None,
            # Reference details
            reference_similarity_score=anomaly_res.get("similarity_score") if anomaly_res else None,
            reference_status=sim_status if run_ref and 'sim_status' in locals() else None,
            # Structured JSON
            detected_defects_json=json.dumps(detected_defects),
            checks_executed_json=json.dumps(checks_executed),
            limitations_json=json.dumps(limitations),
            metadata_json=json.dumps({
                "calibration_factor": calib_factor,
                "tolerance_pos": pos_tol,
                "tolerance_neg": neg_tol
            })
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record
