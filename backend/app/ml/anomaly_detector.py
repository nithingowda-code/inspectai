import os
import cv2
import numpy as np
from typing import Dict, Any, List, Optional
from backend.app.ml.feature_extractor import ResNet18FeatureExtractor
from backend.app.ml.reference_bank import ProductReferenceBank

# Configurable defect thresholds
DEFAULT_ANOMALY_THRESHOLD = 0.32  # Anomaly score above this indicates defect/difference

def detect_surface_defects(img_bgr: np.ndarray) -> List[Dict[str, Any]]:
    """
    OpenCV surface defect analysis: identifies sharp scratches, cracks,
    tears, holes, and localized surface irregularities.
    """
    h, w = img_bgr.shape[:2]
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (3, 3), 0)

    defects = []

    # 1. High gradient scratches and sharp cracks using morphological gradient & Black-Hat / Top-Hat
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    blackhat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, kernel)
    tophat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, kernel)

    # Threshold dark anomalies (cracks, deep scratches, holes)
    _, dark_thresh = cv2.threshold(blackhat, 35, 255, cv2.THRESH_BINARY)
    _, bright_thresh = cv2.threshold(tophat, 45, 255, cv2.THRESH_BINARY)

    combined_flaws = cv2.bitwise_or(dark_thresh, bright_thresh)

    # Clean speckle noise
    clean_flaws = cv2.medianBlur(combined_flaws, 3)
    contours, _ = cv2.findContours(clean_flaws, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    flaw_id = 1
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if 25 < area < (h * w * 0.15):
            x, y, bw, bh = cv2.boundingRect(cnt)
            # Avoid extreme borders (often edge cutoffs)
            if x < 5 or y < 5 or (x + bw) > (w - 5) or (y + bh) > (h - 5):
                continue

            aspect_ratio = max(bw, bh) / max(min(bw, bh), 1)
            solidity = float(area) / max(bw * bh, 1)

            # Classify defect type based on shape morphology
            if aspect_ratio > 3.0:
                defect_type = "scratch"
                severity = "high" if area > 200 else "medium"
                desc = f"Elongated scratch/crack line detected ({bw}x{bh} px)"
            elif solidity > 0.65 and area > 100:
                defect_type = "dent_or_hole"
                severity = "high"
                desc = f"Pitted void or puncture hole detected ({bw}x{bh} px)"
            else:
                defect_type = "surface_irregularity"
                severity = "medium" if area > 150 else "low"
                desc = f"Localized surface defect/foreign matter ({bw}x{bh} px)"

            defects.append({
                "id": f"DEF-{flaw_id:03d}",
                "type": defect_type,
                "severity": severity,
                "location": {"x": int(x), "y": int(y), "width": int(bw), "height": int(bh)},
                "confidence": round(min(0.95, 0.65 + (area / 1000.0)), 2),
                "description": desc
            })
            flaw_id += 1

    return defects

def analyze_anomalies_and_defects(
    inspection_image_path: str,
    output_heatmap_path: str,
    product_id: Optional[str] = None,
    threshold: float = DEFAULT_ANOMALY_THRESHOLD
) -> Dict[str, Any]:
    """
    Combined deep-feature visual comparison & surface defect analysis.
    Produces:
      - Continuous anomaly score
      - Heatmap overlay image highlighting defect regions
      - Detected defect items list
      - Execution status & explanations
    """
    limitations = [
        "Unsupervised patch comparison relies on registered golden reference angles and lighting.",
        "Reflective specular highlights or shadow shifts can cause localized false-positive anomalies.",
        "Micro-defects smaller than 10 pixels may fall below feature map spatial resolution (8x8)."
    ]

    if not os.path.exists(inspection_image_path):
        return {
            "executed": False,
            "status": "REVIEW",
            "anomaly_score": None,
            "anomaly_threshold": threshold,
            "similarity_score": None,
            "defects": [],
            "heatmap_path": None,
            "explanation": f"Inspection image file {inspection_image_path} does not exist.",
            "limitations": limitations
        }

    img_bgr = cv2.imread(inspection_image_path)
    if img_bgr is None:
        return {
            "executed": False,
            "status": "REVIEW",
            "anomaly_score": None,
            "anomaly_threshold": threshold,
            "similarity_score": None,
            "defects": [],
            "heatmap_path": None,
            "explanation": "Unable to decode inspection image.",
            "limitations": limitations
        }

    h, w = img_bgr.shape[:2]
    extractor = ResNet18FeatureExtractor.get_instance()
    g_emb, s_feat = extractor.extract_features(inspection_image_path)

    if g_emb is None or s_feat is None:
        return {
            "executed": False,
            "status": "REVIEW",
            "anomaly_score": None,
            "anomaly_threshold": threshold,
            "similarity_score": None,
            "defects": [],
            "heatmap_path": None,
            "explanation": "Deep feature extraction failed for input image.",
            "limitations": limitations
        }

    # 1. Surface defect detection via OpenCV morphology
    detected_defects = detect_surface_defects(img_bgr)

    # 2. Reference comparison if product_id is provided and bank is ready
    has_ref_bank = False
    ref_anomaly_dist = 0.0
    similarity_score = None
    best_ref_path = None
    spatial_diff_map = None

    if product_id:
        bank = ProductReferenceBank(product_id)
        if bank.is_ready():
            has_ref_bank = True
            comp = bank.compute_anomaly_distance(g_emb, s_feat)
            ref_anomaly_dist = comp["min_global_distance"]
            similarity_score = comp["similarity_score"]
            best_ref_path = comp.get("best_ref_path")
            spatial_diff_map = comp.get("spatial_diff_map")

    # Composite continuous anomaly score
    # Baseline from surface defects:
    surface_flaw_count = len(detected_defects)
    high_sev_count = sum(1 for d in detected_defects if d["severity"] in ["high", "critical"])
    surface_score = min(0.95, (surface_flaw_count * 0.15) + (high_sev_count * 0.25))

    if has_ref_bank:
        # Weighted combination of deep distance and surface flaws
        combined_score = (ref_anomaly_dist * 0.55) + (surface_score * 0.45)
    else:
        # Only surface heuristics available
        combined_score = surface_score
        limitations.append("No registered reference images available for this product. Inspection based solely on general surface defect heuristics.")

    anomaly_score = round(float(combined_score), 3)

    # Generate Heatmap Overlay Image
    # Initialize base heatmap
    heatmap_raw = np.zeros((h, w), dtype=np.float32)

    if spatial_diff_map is not None:
        # Resize 8x8 spatial difference map to image dimensions
        resized_diff = cv2.resize(spatial_diff_map, (w, h), interpolation=cv2.INTER_CUBIC)
        # Normalize 0..1
        diff_min, diff_max = np.min(resized_diff), np.max(resized_diff)
        if diff_max > diff_min:
            resized_diff = (resized_diff - diff_min) / (diff_max - diff_min)
        heatmap_raw += resized_diff * 0.65

    # Add Gaussian blobs on detected surface defect regions
    for defect in detected_defects:
        loc = defect["location"]
        cx = loc["x"] + loc["width"] // 2
        cy = loc["y"] + loc["height"] // 2
        radius = max(loc["width"], loc["height"]) * 2
        # Draw soft white circle onto mask
        mask = np.zeros((h, w), dtype=np.float32)
        cv2.circle(mask, (cx, cy), radius, 1.0, -1)
        mask = cv2.GaussianBlur(mask, (31, 31), 0)
        heatmap_raw += mask * 0.75

    # Normalize heatmap_raw to 0..255 uint8
    heatmap_clamped = np.clip(heatmap_raw, 0.0, 1.0)
    heatmap_u8 = (heatmap_clamped * 255).astype(np.uint8)

    # Apply JET colormap
    color_heatmap = cv2.applyColorMap(heatmap_u8, cv2.COLORMAP_JET)

    # Blend with original image
    alpha = 0.40
    annotated_heatmap = cv2.addWeighted(color_heatmap, alpha, img_bgr, 1.0 - alpha, 0)

    # Draw bounding boxes and tags on defect regions
    for defect in detected_defects:
        loc = defect["location"]
        x, y, bw, bh = loc["x"], loc["y"], loc["width"], loc["height"]
        color = (0, 0, 255) if defect["severity"] in ["high", "critical"] else (0, 165, 255)
        cv2.rectangle(annotated_heatmap, (x, y), (x + bw, y + bh), color, 2)
        tag = f"{defect['type']} ({defect['confidence']:.2f})"
        cv2.putText(annotated_heatmap, tag, (x, max(15, y - 6)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

    # HUD info bar on bottom
    cv2.rectangle(annotated_heatmap, (10, h - 45), (min(500, w - 10), h - 10), (15, 20, 30), -1)
    status_label = "FAIL" if anomaly_score >= threshold else "PASS"
    text_color = (0, 0, 255) if status_label == "FAIL" else (0, 255, 128)
    cv2.putText(annotated_heatmap, f"ANOMALY SCORE: {anomaly_score:.3f} / THRESH: {threshold:.2f} [{status_label}]",
                (20, h - 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, text_color, 2)

    os.makedirs(os.path.dirname(output_heatmap_path), exist_ok=True)
    cv2.imwrite(output_heatmap_path, annotated_heatmap)

    # Final Decision for Defect Check
    if anomaly_score >= threshold:
        status = "FAIL"
        explanation = f"Anomaly score {anomaly_score:.3f} exceeded threshold {threshold:.2f}. "
        if detected_defects:
            explanation += f"Identified {len(detected_defects)} distinct defect region(s) (including {detected_defects[0]['type']})."
        else:
            explanation += "Significant visual pattern deviation from golden reference bank."
    elif not has_ref_bank and len(detected_defects) > 0:
        # Has some defects but no reference images for product
        status = "REVIEW"
        explanation = f"Defects detected ({len(detected_defects)}) but no approved reference images registered to verify baseline."
    else:
        status = "PASS"
        explanation = f"No significant anomalies or surface defects detected. Anomaly score {anomaly_score:.3f} is within permitted threshold {threshold:.2f}."

    return {
        "executed": True,
        "status": status,
        "anomaly_score": anomaly_score,
        "anomaly_threshold": threshold,
        "similarity_score": similarity_score,
        "best_ref_path": best_ref_path,
        "defects": detected_defects,
        "heatmap_path": output_heatmap_path,
        "explanation": explanation,
        "limitations": limitations
    }
