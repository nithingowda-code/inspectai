import os
import cv2
import numpy as np
from typing import Dict, Any, Tuple, Optional

def analyze_dimensions(
    image_path: str,
    output_annotated_path: str,
    expected_length: float,
    expected_width: float,
    pos_tolerance: float,
    neg_tolerance: float,
    calibration_factor: float = 10.0,
    unit: str = "mm"
) -> Dict[str, Any]:
    """
    Measures visible object dimensions from an image using OpenCV contour analysis.
    
    Formula:
      Measured = Pixels / calibration_factor
      Deviation = Measured - Expected
      Pass criteria: -neg_tolerance <= length_deviation <= pos_tolerance 
                     and -neg_tolerance <= width_deviation <= pos_tolerance
    """
    limitations = [
        "Planar 2D estimation assumes the object lies flat parallel to camera plane.",
        "Perspective distortion may affect boundary accuracy without multi-point camera calibration matrix.",
        "Shadows, high-glare lighting, or uneven background contrast can shift edge boundaries.",
        f"Calibration relies on {calibration_factor:.2f} pixels/{unit} scale factor."
    ]

    if not os.path.exists(image_path):
        return {
            "executed": False,
            "status": "REVIEW",
            "measured_length": None,
            "measured_width": None,
            "length_deviation": None,
            "width_deviation": None,
            "explanation": f"Input image path {image_path} not found.",
            "annotated_path": None,
            "limitations": limitations
        }

    img = cv2.imread(image_path)
    if img is None:
        return {
            "executed": False,
            "status": "REVIEW",
            "measured_length": None,
            "measured_width": None,
            "length_deviation": None,
            "width_deviation": None,
            "explanation": "Failed to decode inspection image file with OpenCV.",
            "annotated_path": None,
            "limitations": limitations
        }

    h, w = img.shape[:2]
    annotated = img.copy()

    # Preprocessing for contour extraction
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    # Multi-method thresholding: Otsu + adaptive to find solid object silhouette
    _, otsu_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    
    # Also evaluate regular Otsu in case object is brighter than background
    white_pixel_ratio = np.mean(otsu_thresh == 255)
    if white_pixel_ratio > 0.85 or white_pixel_ratio < 0.05:
        _, otsu_thresh = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Edge combination
    edges = cv2.Canny(blurred, 50, 150)
    combined = cv2.bitwise_or(otsu_thresh, edges)

    # Morphological close to bridge internal textures
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (7, 7))
    closed = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(closed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Filter out contours that are too small or span the entire image border
    valid_contours = []
    min_area = (h * w) * 0.01  # at least 1% of image
    max_area = (h * w) * 0.96  # not the entire frame

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if min_area < area < max_area:
            valid_contours.append((area, cnt))

    if not valid_contours:
        # Fallback to canny edge direct contour
        canny_contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in canny_contours:
            area = cv2.contourArea(cnt)
            if area > min_area * 0.5:
                valid_contours.append((area, cnt))

    if not valid_contours:
        cv2.putText(annotated, "STATUS: UNABLE TO ISOLATE CONTOUR", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
        os.makedirs(os.path.dirname(output_annotated_path), exist_ok=True)
        cv2.imwrite(output_annotated_path, annotated)
        return {
            "executed": True,
            "status": "REVIEW",
            "measured_length": None,
            "measured_width": None,
            "length_deviation": None,
            "width_deviation": None,
            "explanation": "No distinct object boundary could be isolated from background. Manual review required.",
            "annotated_path": output_annotated_path,
            "limitations": limitations
        }

    # Select the primary object contour (largest valid contour)
    valid_contours.sort(key=lambda x: x[0], reverse=True)
    primary_contour = valid_contours[0][1]

    # Calculate Rotated Minimum Area Bounding Box for orientation invariance
    rect = cv2.minAreaRect(primary_contour)
    (center_x, center_y), (dim_w, dim_h), angle = rect
    box = cv2.boxPoints(rect)
    box = np.int32(box)

    # Pixels to dimensions
    pixel_length = max(dim_w, dim_h)
    pixel_width = min(dim_w, dim_h)

    # Guard against invalid calibration factor
    calib = max(float(calibration_factor), 0.001)
    measured_length = round(pixel_length / calib, 2)
    measured_width = round(pixel_width / calib, 2)

    length_dev = round(measured_length - expected_length, 2)
    width_dev = round(measured_width - expected_width, 2)

    # Check tolerances
    length_within_tol = (-neg_tolerance <= length_dev <= pos_tolerance)
    width_within_tol = (-neg_tolerance <= width_dev <= pos_tolerance)

    if length_within_tol and width_within_tol:
        dim_status = "PASS"
        hud_color = (0, 230, 115)  # Tech Green (BGR)
        explanation = (
            f"All dimensions within tolerance. "
            f"Length: {measured_length:.2f}{unit} (Δ {length_dev:+.2f}{unit}, tol [-{neg_tolerance}, +{pos_tolerance}]). "
            f"Width: {measured_width:.2f}{unit} (Δ {width_dev:+.2f}{unit}, tol [-{neg_tolerance}, +{pos_tolerance}])."
        )
    else:
        dim_status = "FAIL"
        hud_color = (0, 0, 240)  # Tech Red (BGR)
        reasons = []
        if not length_within_tol:
            reasons.append(f"Length {measured_length:.2f}{unit} deviates by {length_dev:+.2f}{unit} (permitted: -{neg_tolerance} to +{pos_tolerance})")
        if not width_within_tol:
            reasons.append(f"Width {measured_width:.2f}{unit} deviates by {width_dev:+.2f}{unit} (permitted: -{neg_tolerance} to +{pos_tolerance})")
        explanation = "Dimensional out of tolerance: " + "; ".join(reasons)

    # Draw aesthetic industrial HUD overlay on image
    # 1. Semi-transparent boundary highlight
    overlay = annotated.copy()
    cv2.drawContours(overlay, [primary_contour], -1, (255, 200, 0), 2)  # Cyan/gold contour
    cv2.drawContours(overlay, [box], 0, hud_color, 2)  # Rotated box
    cv2.addWeighted(overlay, 0.75, annotated, 0.25, 0, annotated)

    # Draw corner markers
    for pt in box:
        cv2.circle(annotated, tuple(pt), 5, hud_color, -1)
        cv2.circle(annotated, tuple(pt), 8, (255, 255, 255), 1)

    # Draw center crosshair
    cx, cy = int(center_x), int(center_y)
    cv2.drawMarker(annotated, (cx, cy), hud_color, markerType=cv2.MARKER_CROSS, markerSize=18, thickness=2)

    # Draw dimension lines along the sides of the bounding box
    # Sort box vertices
    p1, p2, p3, p4 = box[0], box[1], box[2], box[3]
    mid_top = ((p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2)
    mid_side = ((p2[0] + p3[0]) // 2, (p2[1] + p3[1]) // 2)

    # HUD Data Panel on top-left of image
    panel_h = 135
    panel_w = min(480, w - 20)
    cv2.rectangle(annotated, (10, 10), (10 + panel_w, 10 + panel_h), (15, 20, 30), -1)
    cv2.rectangle(annotated, (10, 10), (10 + panel_w, 10 + panel_h), hud_color, 1)

    # Header line
    cv2.putText(annotated, f"INSPECT-AI OPTICAL METROLOGY [{dim_status}]", (20, 35),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, hud_color, 2)
    cv2.putText(annotated, f"Length: {measured_length:.2f} {unit}  (Target: {expected_length:.2f}, Dev: {length_dev:+.2f})",
                (20, 65), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)
    cv2.putText(annotated, f"Width:  {measured_width:.2f} {unit}  (Target: {expected_width:.2f}, Dev: {width_dev:+.2f})",
                (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (255, 255, 255), 1)
    cv2.putText(annotated, f"Tol: -{neg_tolerance:.2f}/+{pos_tolerance:.2f}{unit} | Scale: {calib:.1f}px/{unit} | Rot: {angle:.1f} deg",
                (20, 115), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (180, 200, 220), 1)

    # Dimension text alongside object box
    label_len = f"L: {measured_length:.1f}{unit}"
    label_wid = f"W: {measured_width:.1f}{unit}"
    cv2.putText(annotated, label_len, (mid_top[0] - 30, max(20, mid_top[1] - 10)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
    cv2.putText(annotated, label_wid, (mid_side[0] + 10, mid_side[1]),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    os.makedirs(os.path.dirname(output_annotated_path), exist_ok=True)
    cv2.imwrite(output_annotated_path, annotated)

    return {
        "executed": True,
        "status": dim_status,
        "measured_length": measured_length,
        "measured_width": measured_width,
        "expected_length": expected_length,
        "expected_width": expected_width,
        "length_deviation": length_dev,
        "width_deviation": width_dev,
        "unit": unit,
        "explanation": explanation,
        "annotated_path": output_annotated_path,
        "limitations": limitations,
        "bounding_box": {
            "center": [float(center_x), float(center_y)],
            "size": [float(dim_w), float(dim_h)],
            "angle": float(angle)
        }
    }
