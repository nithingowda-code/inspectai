"""
Direct Image Comparator
Compares a reference (good) image against an inspection (potentially broken) image
without needing a pre-registered product, using:
 - Deep ResNet18 feature cosine distance (global + spatial)
 - Pixel-level structural difference map (SSIM + absolute diff)
 - OpenCV surface defect detection on inspection image
 - Diff heatmap overlay for visualization
"""
import os
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple

from backend.app.ml.feature_extractor import ResNet18FeatureExtractor

# Thresholds
SIMILARITY_PASS_THRESHOLD = 0.80   # cosine similarity above this → PASS
SIMILARITY_FAIL_THRESHOLD = 0.55   # below this → FAIL, else REVIEW
PIXEL_DIFF_SEVERE_THRESH  = 0.30   # fraction of pixels with high diff → FAIL trigger
ANOMALY_SCORE_THRESHOLD   = 0.35


def _compute_ssim_map(img1_gray: np.ndarray, img2_gray: np.ndarray) -> np.ndarray:
    """Returns per-pixel SSIM difference map (0=same, 1=max diff)."""
    # Resize both to same size for pixel comparison
    h, w = img1_gray.shape
    img2_r = cv2.resize(img2_gray, (w, h))

    # Local SSIM via sliding window variance/covariance
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu1 = cv2.GaussianBlur(img1_gray.astype(np.float32), (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(img2_r.astype(np.float32), (11, 11), 1.5)
    mu1_sq = mu1 * mu1
    mu2_sq = mu2 * mu2
    mu1_mu2 = mu1 * mu2

    sigma1_sq = cv2.GaussianBlur(img1_gray.astype(np.float32) ** 2, (11, 11), 1.5) - mu1_sq
    sigma2_sq = cv2.GaussianBlur(img2_r.astype(np.float32) ** 2, (11, 11), 1.5) - mu2_sq
    sigma12   = cv2.GaussianBlur(img1_gray.astype(np.float32) * img2_r.astype(np.float32), (11, 11), 1.5) - mu1_mu2

    ssim_map = ((2 * mu1_mu2 + C1) * (2 * sigma12 + C2)) / \
               ((mu1_sq + mu2_sq + C1) * (sigma1_sq + sigma2_sq + C2))

    diff_map = 1.0 - np.clip(ssim_map, 0.0, 1.0)   # 0=identical, 1=totally different
    return diff_map


def _detect_changed_regions(diff_map: np.ndarray, orig_shape: Tuple[int, int]) -> List[Dict[str, Any]]:
    """Find contiguous regions of high structural difference."""
    h, w = orig_shape
    diff_resized = cv2.resize(diff_map, (w, h))
    diff_u8 = (np.clip(diff_resized, 0, 1) * 255).astype(np.uint8)

    _, thresh = cv2.threshold(diff_u8, 60, 255, cv2.THRESH_BINARY)
    # Morphological closing to merge adjacent blobs
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (11, 11))
    closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    regions = []
    for i, cnt in enumerate(contours):
        area = cv2.contourArea(cnt)
        if area < 100:
            continue
        x, y, bw, bh = cv2.boundingRect(cnt)
        severity = "high" if area > 2000 else ("medium" if area > 500 else "low")
        regions.append({
            "id": f"CHG-{i+1:03d}",
            "type": "structural_change",
            "severity": severity,
            "location": {"x": int(x), "y": int(y), "width": int(bw), "height": int(bh)},
            "area_px": int(area),
            "confidence": round(min(0.97, 0.60 + area / 5000.0), 2),
            "description": f"Region shows structural/surface deviation from reference ({bw}×{bh} px, area={int(area)})"
        })

    return regions


def compare_images(
    reference_image_path: str,
    inspection_image_path: str,
    output_heatmap_path: str,
    output_sidebyside_path: str
) -> Dict[str, Any]:
    """
    Core comparison engine.
    Returns a rich result dict with:
      - similarity_score (0..1, higher = more similar)
      - anomaly_score (0..1, higher = more different / more broken)
      - detected_changes (list of changed region dicts)
      - overall status/explanation
    """
    limitations = [
        "Comparison is sensitive to image orientation, zoom, and lighting differences.",
        "Structural changes smaller than ~10 pixels may not be captured at the feature resolution.",
        "Colour or brightness shifts between reference and inspection can create false positives."
    ]

    # --- Load images ---
    if not os.path.exists(reference_image_path):
        return _error_result("Reference image file not found.", limitations)
    if not os.path.exists(inspection_image_path):
        return _error_result("Inspection image file not found.", limitations)

    ref_bgr  = cv2.imread(reference_image_path)
    insp_bgr = cv2.imread(inspection_image_path)
    if ref_bgr is None:
        return _error_result("Could not decode reference image.", limitations)
    if insp_bgr is None:
        return _error_result("Could not decode inspection image.", limitations)

    # Resize inspection to reference size for pixel comparison
    h_ref, w_ref = ref_bgr.shape[:2]
    insp_resized  = cv2.resize(insp_bgr, (w_ref, h_ref))

    ref_gray  = cv2.cvtColor(ref_bgr,      cv2.COLOR_BGR2GRAY)
    insp_gray = cv2.cvtColor(insp_resized, cv2.COLOR_BGR2GRAY)

    # --- Feature extraction ---
    extractor = ResNet18FeatureExtractor.get_instance()
    ref_gemb,  ref_sfeat  = extractor.extract_features(reference_image_path)
    insp_gemb, insp_sfeat = extractor.extract_features(inspection_image_path)

    if ref_gemb is None or insp_gemb is None:
        return _error_result("Deep feature extraction failed for one or both images.", limitations)

    # Global cosine similarity
    similarity_score = float(np.dot(ref_gemb, insp_gemb))   # both already L2-normalised
    similarity_score = max(0.0, min(1.0, similarity_score))

    # Spatial feature map difference (8×8 patch cosine distances)
    # Normalise spatial features per-channel
    ref_s_norm  = ref_sfeat  / (np.linalg.norm(ref_sfeat,  axis=0, keepdims=True) + 1e-6)
    insp_s_norm = insp_sfeat / (np.linalg.norm(insp_sfeat, axis=0, keepdims=True) + 1e-6)
    spatial_diff = np.mean(np.abs(ref_s_norm - insp_s_norm), axis=0)   # (8, 8)
    spatial_diff = (spatial_diff - spatial_diff.min()) / (spatial_diff.max() - spatial_diff.min() + 1e-6)

    # --- SSIM structural diff map ---
    ssim_diff = _compute_ssim_map(ref_gray, insp_gray)

    # Fraction of pixels with notable difference
    pixel_diff_fraction = float(np.mean(ssim_diff > 0.25))

    # Composite anomaly score
    feature_score = 1.0 - similarity_score   # 0=identical, 1=totally different
    pixel_score   = min(1.0, pixel_diff_fraction * 3.0)
    anomaly_score = round(float(feature_score * 0.55 + pixel_score * 0.45), 3)

    # --- Changed regions ---
    # Combined diff map: SSIM + spatial upscaled
    spatial_upscaled = cv2.resize(spatial_diff.astype(np.float32), (w_ref, h_ref))
    combined_diff = np.clip(ssim_diff * 0.6 + spatial_upscaled * 0.4, 0, 1)
    detected_changes = _detect_changed_regions(combined_diff, (h_ref, w_ref))

    # --- Build heatmap overlay on inspection image ---
    diff_u8 = (np.clip(combined_diff, 0, 1) * 255).astype(np.uint8)
    color_heatmap = cv2.applyColorMap(diff_u8, cv2.COLORMAP_JET)
    heatmap_blend = cv2.addWeighted(color_heatmap, 0.45, insp_resized, 0.55, 0)

    # Draw bounding boxes of changed regions
    for chg in detected_changes:
        loc = chg["location"]
        x, y, bw, bh = loc["x"], loc["y"], loc["width"], loc["height"]
        col = (0, 0, 255) if chg["severity"] == "high" else (0, 165, 255)
        cv2.rectangle(heatmap_blend, (x, y), (x + bw, y + bh), col, 2)
        cv2.putText(heatmap_blend, f"{chg['severity']} ({chg['confidence']:.2f})",
                    (x, max(14, y - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.42, col, 1)

    # HUD bar
    status_label = "FAIL" if anomaly_score >= ANOMALY_SCORE_THRESHOLD else "PASS"
    text_col = (0, 0, 255) if status_label == "FAIL" else (0, 255, 128)
    cv2.rectangle(heatmap_blend, (8, h_ref - 44), (min(520, w_ref - 8), h_ref - 8), (10, 15, 25), -1)
    cv2.putText(heatmap_blend,
                f"SIMILARITY: {similarity_score:.3f}  DIFF: {anomaly_score:.3f}  [{status_label}]",
                (18, h_ref - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.48, text_col, 2)

    os.makedirs(os.path.dirname(output_heatmap_path), exist_ok=True)
    cv2.imwrite(output_heatmap_path, heatmap_blend)

    # --- Side-by-side comparison image ---
    _build_sidebyside(ref_bgr, insp_resized, combined_diff, output_sidebyside_path)

    # --- Decision ---
    if anomaly_score >= ANOMALY_SCORE_THRESHOLD or len(detected_changes) >= 3:
        status = "FAIL"
        explanation = (
            f"Inspection image shows significant deviations from reference. "
            f"Similarity: {similarity_score:.1%}, Anomaly Score: {anomaly_score:.3f}. "
            f"{len(detected_changes)} distinct changed region(s) detected."
        )
    elif anomaly_score >= ANOMALY_SCORE_THRESHOLD * 0.6 or len(detected_changes) >= 1:
        status = "REVIEW"
        explanation = (
            f"Moderate differences found between reference and inspection image. "
            f"Similarity: {similarity_score:.1%}. "
            f"{len(detected_changes)} region(s) need operator review."
        )
    else:
        status = "PASS"
        explanation = (
            f"Inspection image is visually consistent with the reference. "
            f"Similarity: {similarity_score:.1%}, Anomaly Score: {anomaly_score:.3f}. "
            f"No significant defects or structural changes detected."
        )

    return {
        "executed": True,
        "status": status,
        "similarity_score": round(similarity_score, 4),
        "anomaly_score": anomaly_score,
        "anomaly_threshold": ANOMALY_SCORE_THRESHOLD,
        "pixel_diff_fraction": round(pixel_diff_fraction, 4),
        "detected_changes": detected_changes,
        "heatmap_path": output_heatmap_path,
        "sidebyside_path": output_sidebyside_path,
        "explanation": explanation,
        "limitations": limitations
    }


def _build_sidebyside(ref_bgr: np.ndarray, insp_bgr: np.ndarray,
                      diff_map: np.ndarray, out_path: str) -> None:
    """Creates a 3-panel side-by-side image: Reference | Inspection | Diff Heatmap."""
    h, w = ref_bgr.shape[:2]
    target_w, target_h = 480, 360

    ref_r  = cv2.resize(ref_bgr,  (target_w, target_h))
    insp_r = cv2.resize(insp_bgr, (target_w, target_h))

    diff_resized = cv2.resize(diff_map.astype(np.float32), (target_w, target_h))
    diff_u8 = (np.clip(diff_resized, 0, 1) * 255).astype(np.uint8)
    diff_color = cv2.applyColorMap(diff_u8, cv2.COLORMAP_INFERNO)

    # Add labels
    LABEL_H = 30
    canvas_w = target_w * 3 + 6
    canvas_h = target_h + LABEL_H
    canvas = np.full((canvas_h, canvas_w, 3), (18, 22, 32), dtype=np.uint8)

    # Paste panels
    canvas[LABEL_H:, 0:target_w]           = ref_r
    canvas[LABEL_H:, target_w+3:target_w*2+3] = insp_r
    canvas[LABEL_H:, target_w*2+6:]        = diff_color

    # Labels
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(canvas, "REFERENCE (Good)",    (10,             22), font, 0.52, (80, 255, 160), 1)
    cv2.putText(canvas, "INSPECTION (Broken)", (target_w + 13,  22), font, 0.52, (80, 160, 255), 1)
    cv2.putText(canvas, "DIFF MAP",            (target_w*2 + 16, 22), font, 0.52, (80, 200, 255), 1)

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    cv2.imwrite(out_path, canvas)


def _error_result(msg: str, limitations: list) -> Dict[str, Any]:
    return {
        "executed": False,
        "status": "REVIEW",
        "similarity_score": None,
        "anomaly_score": None,
        "anomaly_threshold": ANOMALY_SCORE_THRESHOLD,
        "pixel_diff_fraction": None,
        "detected_changes": [],
        "heatmap_path": None,
        "sidebyside_path": None,
        "explanation": msg,
        "limitations": limitations
    }
