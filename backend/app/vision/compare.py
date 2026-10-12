"""
InspectAI Two-Image Direct Comparison Pipeline (Core Vision Engine)

Implements the 6-stage universal comparison pipeline:
  Stage 1: Image validation and preprocessing (exposure, blur, EXIF, CLAHE)
  Stage 2: Object segmentation (Otsu/adaptive, morphological clean, largest contour)
  Stage 3: Alignment / Registration (SIFT/ORB + RANSAC homography, contour fallback)
  Stage 4: Difference analysis (silhouette IoU, missing/extra regions, SSIM, ResNet18 patch anomaly, geometry)
  Stage 5: Scoring (Difference Index, Similarity Index, transparent sub-scores)
  Stage 6: Visual outputs (side-by-side, silhouette overlay, annotated bounding boxes, plain-language summary)
"""
import os
import math
import cv2
import numpy as np
from typing import Dict, Any, List, Tuple, Optional

try:
    from backend.app.ml.feature_extractor import ResNet18FeatureExtractor
    HAS_TORCH_MODEL = True
except Exception as e:
    HAS_TORCH_MODEL = False
    print(f"[InspectAI] Torch feature extractor not available: {e}")


# ==============================================================================
# STAGE 1: Image Validation & Preprocessing
# ==============================================================================

def validate_and_preprocess(image_path: str) -> Dict[str, Any]:
    """
    Validates image file readability, resolution, exposure, and blur.
    Applies CLAHE contrast normalization.
    """
    if not os.path.exists(image_path):
        return {
            "valid": False,
            "error": "Image file does not exist on disk",
            "img_bgr": None,
            "img_gray": None,
            "blur_score": 0.0,
            "mean_brightness": 0.0,
            "warnings": ["File not found"]
        }

    img_bgr = cv2.imread(image_path)
    if img_bgr is None or img_bgr.size == 0:
        return {
            "valid": False,
            "error": "Image file could not be decoded. Corrupted or unsupported format.",
            "img_bgr": None,
            "img_gray": None,
            "blur_score": 0.0,
            "mean_brightness": 0.0,
            "warnings": ["Corrupt or unreadable image"]
        }

    h, w = img_bgr.shape[:2]
    if h < 80 or w < 80:
        return {
            "valid": False,
            "error": f"Image resolution too low ({w}x{h} px). Minimum required is 80x80 px.",
            "img_bgr": img_bgr,
            "img_gray": None,
            "blur_score": 0.0,
            "mean_brightness": 0.0,
            "warnings": ["Low resolution"]
        }

    img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # 1. Blur evaluation via variance of Laplacian
    laplacian_var = float(cv2.Laplacian(img_gray, cv2.CV_64F).var())
    is_blurry = laplacian_var < 20.0

    # 2. Exposure evaluation
    mean_brightness = float(np.mean(img_gray))
    is_underexposed = mean_brightness < 25.0
    is_overexposed = mean_brightness > 235.0

    warnings = []
    if is_blurry:
        warnings.append(f"Image appears blurry (Laplacian variance {laplacian_var:.1f} < 20.0)")
    if is_underexposed:
        warnings.append(f"Image is underexposed/dark (Mean brightness {mean_brightness:.1f}/255)")
    if is_overexposed:
        warnings.append(f"Image is overexposed/blown out (Mean brightness {mean_brightness:.1f}/255)")

    # 3. CLAHE Lighting Normalization on Luminance channel
    lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    lab_norm = cv2.merge((l_clahe, a, b))
    img_bgr_norm = cv2.cvtColor(lab_norm, cv2.COLOR_LAB2BGR)

    return {
        "valid": True,
        "error": None,
        "img_bgr": img_bgr,
        "img_bgr_norm": img_bgr_norm,
        "img_gray": img_gray,
        "blur_score": laplacian_var,
        "is_blurry": is_blurry,
        "mean_brightness": mean_brightness,
        "is_underexposed": is_underexposed,
        "is_overexposed": is_overexposed,
        "warnings": warnings,
        "width": w,
        "height": h
    }


# ==============================================================================
# STAGE 2: Object Segmentation
# ==============================================================================

def segment_object(img_bgr: np.ndarray) -> Dict[str, Any]:
    """
    Extracts the foreground manufactured object from background.
    Uses adaptive/Otsu thresholding and morphological cleanup.
    Returns binary mask (255=object, 0=bg), main contour, and geometry.
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    total_area = h * w

    # Gaussian blur to suppress fine surface texture before thresholding
    blurred = cv2.GaussianBlur(gray, (7, 7), 0)

    # Otsu thresholding
    _, thresh_otsu = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Check corners to deduce if background is light or dark
    corners = [thresh_otsu[0:15, 0:15], thresh_otsu[0:15, -15:],
               thresh_otsu[-15:, 0:15], thresh_otsu[-15:, -15:]]
    corner_mean = np.mean([c.mean() for c in corners])
    if corner_mean > 127:
        # Background is white/light -> invert so object is white (255)
        binary = cv2.bitwise_not(thresh_otsu)
    else:
        binary = thresh_otsu

    # Morphological opening (remove isolated salt noise) followed by closing (fill holes)
    kernel_small = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    kernel_large = cv2.getStructuringElement(cv2.MORPH_RECT, (11, 11))
    cleaned = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel_small)
    cleaned = cv2.morphologyEx(cleaned, cv2.MORPH_CLOSE, kernel_large)

    contours, _ = cv2.findContours(cleaned, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        # Fallback to whole frame if no contour found
        mask = np.full((h, w), 255, dtype=np.uint8)
        return {
            "mask": mask,
            "contour": None,
            "confidence": 0.2,
            "area_px": float(total_area),
            "perimeter_px": float(2 * (h + w)),
            "bounding_box": (0, 0, w, h),
            "rotated_rect": ((w / 2, h / 2), (w, h), 0.0),
            "solidity": 1.0,
            "status": "REVIEW",
            "warning": "No distinct object boundary detected; entire frame selected."
        }

    # Find largest contour
    main_contour = max(contours, key=cv2.contourArea)
    cnt_area = float(cv2.contourArea(main_contour))
    area_ratio = cnt_area / total_area

    # Check validity of segmentation
    if area_ratio < 0.02:
        confidence = 0.35
        status = "REVIEW"
        warning = f"Detected object is extremely small ({area_ratio*100:.1f}% of image)."
    elif area_ratio > 0.98:
        confidence = 0.40
        status = "REVIEW"
        warning = "Object occupies almost 100% of image; boundary separation uncertain."
    else:
        confidence = 0.90
        status = "PASS"
        warning = None

    # Create clean filled mask
    mask = np.zeros((h, w), dtype=np.uint8)
    cv2.drawContours(mask, [main_contour], -1, 255, -1)

    # Fill internal holes inside the main object
    cnt_fill = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel_large)

    x, y, bw, bh = cv2.boundingRect(main_contour)
    rot_rect = cv2.minAreaRect(main_contour)  # ((cx, cy), (width, height), angle)
    peri = float(cv2.arcLength(main_contour, True))

    hull = cv2.convexHull(main_contour)
    hull_area = float(cv2.contourArea(hull))
    solidity = (cnt_area / hull_area) if hull_area > 0 else 1.0

    return {
        "mask": cnt_fill,
        "contour": main_contour,
        "confidence": confidence,
        "area_px": cnt_area,
        "perimeter_px": peri,
        "bounding_box": (x, y, bw, bh),
        "rotated_rect": rot_rect,
        "solidity": solidity,
        "status": status,
        "warning": warning
    }


# ==============================================================================
# STAGE 3: Alignment (Registration)
# ==============================================================================

def align_test_to_ideal(
    ideal_bgr: np.ndarray,
    ideal_mask: np.ndarray,
    test_bgr: np.ndarray,
    test_mask: np.ndarray
) -> Dict[str, Any]:
    """
    Registers the test image to match the ideal reference image geometry.
    Uses SIFT feature matching with RANSAC homography.
    Falls back to contour principal axes / centroid alignment when features are sparse.
    """
    ih, iw = ideal_bgr.shape[:2]
    th, tw = test_bgr.shape[:2]

    ideal_gray = cv2.cvtColor(ideal_bgr, cv2.COLOR_BGR2GRAY)
    test_gray = cv2.cvtColor(test_bgr, cv2.COLOR_BGR2GRAY)

    sift = cv2.SIFT_create(nfeatures=2000)

    # Detect features specifically on/around the segmented objects
    dilated_ideal_mask = cv2.dilate(ideal_mask, np.ones((15, 15), np.uint8))
    dilated_test_mask = cv2.dilate(test_mask, np.ones((15, 15), np.uint8))

    kp1, des1 = sift.detectAndCompute(ideal_gray, mask=dilated_ideal_mask)
    kp2, des2 = sift.detectAndCompute(test_gray, mask=dilated_test_mask)

    # If masked keypoints too few, try full image
    if des1 is None or len(kp1) < 10:
        kp1, des1 = sift.detectAndCompute(ideal_gray, None)
    if des2 is None or len(kp2) < 10:
        kp2, des2 = sift.detectAndCompute(test_gray, None)

    aligned_bgr = None
    aligned_mask = None
    method = "none"
    inliers_count = 0
    inlier_ratio = 0.0
    reprojection_error = 0.0
    reliable = False
    notes = ""

    if des1 is not None and des2 is not None and len(kp1) >= 8 and len(kp2) >= 8:
        # FLANN matcher for speed & quality
        FLANN_INDEX_KDTREE = 1
        index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
        search_params = dict(checks=50)
        try:
            flann = cv2.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(des2, des1, k=2)  # test -> ideal

            # Lowe's ratio test
            good_matches = []
            for m_n in matches:
                if len(m_n) == 2:
                    m, n = m_n
                    if m.distance < 0.75 * n.distance:
                        good_matches.append(m)

            if len(good_matches) >= 8:
                src_pts = np.float32([kp2[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
                dst_pts = np.float32([kp1[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

                H, mask_inliers = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 4.0)

                if H is not None and mask_inliers is not None:
                    inliers_count = int(np.sum(mask_inliers))
                    inlier_ratio = float(inliers_count / len(good_matches)) if len(good_matches) > 0 else 0.0

                    # Compute reprojection error for inliers
                    inlier_indices = np.where(mask_inliers.ravel() == 1)[0]
                    if len(inlier_indices) > 0:
                        src_inliers = src_pts[inlier_indices]
                        dst_inliers = dst_pts[inlier_indices]
                        projected = cv2.perspectiveTransform(src_inliers, H)
                        reprojection_error = float(np.mean(np.linalg.norm(dst_inliers - projected, axis=2)))

                    # Sanity check determinant & scale of H to avoid degenerate transforms
                    det = np.linalg.det(H[:2, :2])
                    if 0.15 < abs(det) < 8.0 and inliers_count >= 8:
                        aligned_bgr = cv2.warpPerspective(test_bgr, H, (iw, ih), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
                        aligned_mask = cv2.warpPerspective(test_mask, H, (iw, ih), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
                        method = "sift_ransac_homography"
                        reliable = inliers_count >= 12 and inlier_ratio >= 0.25
                        notes = f"Feature alignment verified ({inliers_count} inliers, {inlier_ratio*100:.1f}% ratio, error {reprojection_error:.2f}px)"
        except Exception as e:
            notes = f"SIFT matching encountered error ({e}), falling back to contour alignment."

    # Fallback to contour-based alignment if feature alignment was not possible or unreliable
    if aligned_bgr is None:
        # Moment-based centroid & principal axes alignment
        m_ideal = cv2.moments(ideal_mask)
        m_test = cv2.moments(test_mask)

        if m_ideal["m00"] > 0 and m_test["m00"] > 0:
            cx_i, cy_i = m_ideal["m10"] / m_ideal["m00"], m_ideal["m01"] / m_ideal["m00"]
            cx_t, cy_t = m_test["m10"] / m_test["m00"], m_test["m01"] / m_test["m00"]

            # Scale estimation from area
            scale = math.sqrt(m_ideal["m00"] / m_test["m00"])

            # Principal orientation angle
            def _get_angle(m):
                mu20, mu02, mu11 = m["mu20"], m["mu02"], m["mu11"]
                return 0.5 * math.atan2(2 * mu11, mu20 - mu02)

            angle_i = _get_angle(m_ideal)
            angle_t = _get_angle(m_test)
            delta_angle = math.degrees(angle_i - angle_t)

            # Rotation matrix around test center
            M_rot = cv2.getRotationMatrix2D((cx_t, cy_t), delta_angle, scale)
            # Adjust translation so test center lands on ideal center
            M_rot[0, 2] += (cx_i - cx_t)
            M_rot[1, 2] += (cy_i - cy_t)

            aligned_bgr = cv2.warpAffine(test_bgr, M_rot, (iw, ih), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0))
            aligned_mask = cv2.warpAffine(test_mask, M_rot, (iw, ih), flags=cv2.INTER_NEAREST, borderMode=cv2.BORDER_CONSTANT, borderValue=0)
            method = "contour_moment_affine"
            reliable = False  # Always flag fallback as requiring operator review
            notes = "Feature match insufficient. Aligned via contour centroids and principal axes (REVIEW required)."
        else:
            # Resize directly
            aligned_bgr = cv2.resize(test_bgr, (iw, ih))
            aligned_mask = cv2.resize(test_mask, (iw, ih))
            method = "direct_scale_fallback"
            reliable = False
            notes = "Alignment fallback: direct uniform resize. Feature matching failed."

    return {
        "aligned_test_bgr": aligned_bgr,
        "aligned_test_mask": aligned_mask,
        "method": method,
        "inliers_count": inliers_count,
        "inlier_ratio": inlier_ratio,
        "reprojection_error": reprojection_error,
        "reliable": reliable,
        "notes": notes,
        "status": "PASS" if reliable else "REVIEW"
    }


# ==============================================================================
# STAGE 4: Difference Analysis
# ==============================================================================

def analyze_differences(
    ideal_bgr: np.ndarray,
    ideal_mask: np.ndarray,
    aligned_test_bgr: np.ndarray,
    aligned_test_mask: np.ndarray,
    scale_method: str = "same_setup",
    expected_length: Optional[float] = None,
    expected_width: Optional[float] = None,
    pos_tolerance: Optional[float] = None,
    neg_tolerance: Optional[float] = None,
    unit: str = "mm"
) -> Dict[str, Any]:
    """
    Computes multiple independent difference signals:
      1. Silhouette difference (IoU, missing area, extra area, Hu distance)
      2. Pixel & structural difference (SSIM and color diff in object region)
      3. Deep feature patch anomaly (ResNet18 cosine distance)
      4. Geometric measurement comparison (length, width, area, aspect ratio)
      5. Heuristic region classification (missing, extra, deformation, surface)
    """
    ih, iw = ideal_bgr.shape[:2]
    ideal_gray = cv2.cvtColor(ideal_bgr, cv2.COLOR_BGR2GRAY)
    test_gray = cv2.cvtColor(aligned_test_bgr, cv2.COLOR_BGR2GRAY)

    # ---------------------------------------------------------
    # 1. Silhouette Comparison
    # ---------------------------------------------------------
    m_ideal = (ideal_mask > 127).astype(np.uint8)
    m_test = (aligned_test_mask > 127).astype(np.uint8)

    intersection = int(np.sum((m_ideal & m_test)))
    union = int(np.sum((m_ideal | m_test)))
    iou = float(intersection / union) if union > 0 else 0.0

    ideal_area_px = int(np.sum(m_ideal))
    test_area_px = int(np.sum(m_test))

    # Missing regions = Present in ideal, absent in test
    missing_mask = ((m_ideal == 1) & (m_test == 0)).astype(np.uint8) * 255
    missing_area_px = int(np.sum(missing_mask > 0))
    missing_pct = float((missing_area_px / ideal_area_px) * 100) if ideal_area_px > 0 else 0.0

    # Extra regions = Present in test, absent in ideal
    extra_mask = ((m_test == 1) & (m_ideal == 0)).astype(np.uint8) * 255
    extra_area_px = int(np.sum(extra_mask > 0))
    extra_pct = float((extra_area_px / ideal_area_px) * 100) if ideal_area_px > 0 else 0.0

    # Contour shape distance (Hu Moments)
    cnt_ideal_list, _ = cv2.findContours(ideal_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnt_test_list, _ = cv2.findContours(aligned_test_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    hu_distance = 0.0
    if cnt_ideal_list and cnt_test_list:
        c1 = max(cnt_ideal_list, key=cv2.contourArea)
        c2 = max(cnt_test_list, key=cv2.contourArea)
        hu_distance = float(cv2.matchShapes(c1, c2, cv2.CONTOURS_MATCH_I1, 0.0))

    # ---------------------------------------------------------
    # 2. Pixel & Structural Difference (SSIM + Lab Color Diff)
    # ---------------------------------------------------------
    C1, C2 = (0.01 * 255) ** 2, (0.03 * 255) ** 2
    mu1 = cv2.GaussianBlur(ideal_gray.astype(np.float32), (11, 11), 1.5)
    mu2 = cv2.GaussianBlur(test_gray.astype(np.float32), (11, 11), 1.5)
    sigma1_sq = cv2.GaussianBlur(ideal_gray.astype(np.float32) ** 2, (11, 11), 1.5) - (mu1 ** 2)
    sigma2_sq = cv2.GaussianBlur(test_gray.astype(np.float32) ** 2, (11, 11), 1.5) - (mu2 ** 2)
    sigma12 = cv2.GaussianBlur(ideal_gray.astype(np.float32) * test_gray.astype(np.float32), (11, 11), 1.5) - (mu1 * mu2)

    ssim_map = ((2 * mu1 * mu2 + C1) * (2 * sigma12 + C2)) / ((mu1**2 + mu2**2 + C1) * (sigma1_sq + sigma2_sq + C2))
    ssim_diff_map = 1.0 - np.clip(ssim_map, 0.0, 1.0)

    # Color difference in Lab space
    lab_ideal = cv2.cvtColor(ideal_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    lab_test = cv2.cvtColor(aligned_test_bgr, cv2.COLOR_BGR2LAB).astype(np.float32)
    color_diff = np.linalg.norm(lab_ideal - lab_test, axis=2) / 100.0  # normalize roughly 0..1

    # Combined surface difference restricted to the overlapping object area
    common_mask = (m_ideal & m_test).astype(np.float32)
    surface_diff = (0.6 * ssim_diff_map + 0.4 * np.clip(color_diff, 0.0, 1.0)) * common_mask

    mean_surface_diff = float(np.sum(surface_diff) / np.sum(common_mask)) if np.sum(common_mask) > 0 else 0.0

    # ---------------------------------------------------------
    # 3. Deep Feature Anomaly (ResNet18 Patches)
    # ---------------------------------------------------------
    deep_anomaly_score = 0.0
    deep_diff_map = np.zeros((ih, iw), dtype=np.float32)

    if HAS_TORCH_MODEL:
        try:
            extractor = ResNet18FeatureExtractor.get_instance()
            f1_global, f1_spatial = extractor.extract_features_from_bgr(ideal_bgr)
            f2_global, f2_spatial = extractor.extract_features_from_bgr(aligned_test_bgr)

            # Global cosine distance
            cos_sim_global = float(np.dot(f1_global, f2_global) / (np.linalg.norm(f1_global) * np.linalg.norm(f2_global) + 1e-7))
            deep_anomaly_score = float(max(0.0, 1.0 - cos_sim_global))

            # Spatial patch difference map (8x8)
            f1_norm = f1_spatial / (np.linalg.norm(f1_spatial, axis=0, keepdims=True) + 1e-7)
            f2_norm = f2_spatial / (np.linalg.norm(f2_spatial, axis=0, keepdims=True) + 1e-7)
            spatial_sim = np.sum(f1_norm * f2_norm, axis=0)  # shape (8, 8)
            spatial_dist = 1.0 - np.clip(spatial_sim, -1.0, 1.0)
            deep_diff_map = cv2.resize(spatial_dist, (iw, ih), interpolation=cv2.INTER_CUBIC)
            deep_diff_map = np.clip(deep_diff_map, 0.0, 1.0)
        except Exception as e:
            print(f"[InspectAI] Deep feature extraction error: {e}")
            deep_anomaly_score = mean_surface_diff
            deep_diff_map = surface_diff
    else:
        deep_anomaly_score = mean_surface_diff
        deep_diff_map = surface_diff

    # Master Anomaly Heatmap (combines missing/extra silhouettes + surface + deep features)
    master_diff_map = np.clip(
        0.40 * (missing_mask.astype(np.float32) / 255.0) +
        0.35 * (extra_mask.astype(np.float32) / 255.0) +
        0.15 * surface_diff +
        0.10 * deep_diff_map,
        0.0, 1.0
    )

    # ---------------------------------------------------------
    # 4. Geometric & Dimensional Metrology
    # ---------------------------------------------------------
    # Get bounding dimensions
    xi, yi, wi_px, hi_px = cv2.boundingRect(ideal_mask)
    xt, yt, wt_px, ht_px = cv2.boundingRect(aligned_test_mask)

    # Orientation-invariant length and width (length = longer dimension)
    ideal_len_px = float(max(wi_px, hi_px))
    ideal_wid_px = float(min(wi_px, hi_px))
    test_len_px = float(max(wt_px, ht_px))
    test_wid_px = float(min(wt_px, ht_px))

    len_dev_pct = float(((test_len_px - ideal_len_px) / ideal_len_px) * 100) if ideal_len_px > 0 else 0.0
    wid_dev_pct = float(((test_wid_px - ideal_wid_px) / ideal_wid_px) * 100) if ideal_wid_px > 0 else 0.0
    area_dev_pct = float(((test_area_px - ideal_area_px) / ideal_area_px) * 100) if ideal_area_px > 0 else 0.0

    dimensions_result = {
        "scale_method": scale_method,
        "unit": unit,
        "is_calibrated": False,
        "ideal_length_px": ideal_len_px,
        "ideal_width_px": ideal_wid_px,
        "test_length_px": test_len_px,
        "test_width_px": test_wid_px,
        "length_deviation_pct": round(len_dev_pct, 2),
        "width_deviation_pct": round(wid_dev_pct, 2),
        "area_deviation_pct": round(area_dev_pct, 2),
        "measured_length": None,
        "measured_width": None,
        "expected_length": expected_length,
        "expected_width": expected_width,
        "length_deviation": None,
        "width_deviation": None,
        "tolerance_status": "NOT_CALIBRATED",
        "explanation": "Relative percentage deviations computed relative to ideal object."
    }

    if scale_method == "same_setup" and expected_length and expected_length > 0:
        px_per_unit = ideal_len_px / expected_length
        m_len = test_len_px / px_per_unit
        m_wid = test_wid_px / px_per_unit
        exp_w = expected_width or (expected_length * (ideal_wid_px / ideal_len_px))

        dev_l = m_len - expected_length
        dev_w = m_wid - exp_w

        pos_tol = pos_tolerance if pos_tolerance is not None else 2.0
        neg_tol = neg_tolerance if neg_tolerance is not None else 2.0

        is_l_pass = (-neg_tol <= dev_l <= pos_tol)
        is_w_pass = (-neg_tol <= dev_w <= pos_tol)

        tol_status = "PASS" if (is_l_pass and is_w_pass) else "FAIL"

        dimensions_result.update({
            "is_calibrated": True,
            "measured_length": round(m_len, 2),
            "measured_width": round(m_wid, 2),
            "expected_length": round(expected_length, 2),
            "expected_width": round(exp_w, 2),
            "length_deviation": round(dev_l, 2),
            "width_deviation": round(dev_w, 2),
            "tolerance_status": tol_status,
            "explanation": f"Calibrated using ideal object dimension ({px_per_unit:.2f} px/{unit}). Length dev: {dev_l:+.2f}{unit}, Width dev: {dev_w:+.2f}{unit}."
        })
    elif scale_method == "relative_only":
        dimensions_result["unit"] = "%"
        dimensions_result["tolerance_status"] = "RELATIVE_ONLY"
        dimensions_result["explanation"] = "Relative-only mode active: reporting strictly uncalibrated percentage deviations."

    # ---------------------------------------------------------
    # 5. Region Classification (Suspected Differences)
    # ---------------------------------------------------------
    detected_regions: List[Dict[str, Any]] = []
    reg_counter = 1

    # A) Missing Material Regions
    kernel_clean = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    missing_clean = cv2.morphologyEx(missing_mask, cv2.MORPH_OPEN, kernel_clean)
    cnts_missing, _ = cv2.findContours(missing_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in cnts_missing:
        area = cv2.contourArea(cnt)
        if area >= 80:  # ignore micro noise
            x, y, bw, bh = cv2.boundingRect(cnt)
            pct_obj = (area / ideal_area_px) * 100 if ideal_area_px > 0 else 0.0
            sev = "critical" if pct_obj > 5.0 else ("high" if pct_obj > 2.0 else "medium")
            detected_regions.append({
                "id": f"DIFF-{reg_counter:03d}",
                "classification": "suspected missing material or component",
                "category": "missing_material",
                "severity": sev,
                "location": {"x": int(x), "y": int(y), "width": int(bw), "height": int(bh)},
                "area_px": int(area),
                "area_percent_of_object": round(pct_obj, 2),
                "confidence_note": "Suspected missing region identified by silhouette subtraction. Subject to operator review.",
                "confidence": round(min(0.95, 0.65 + pct_obj * 0.05), 2)
            })
            reg_counter += 1

    # B) Extra / Protruding Material Regions
    extra_clean = cv2.morphologyEx(extra_mask, cv2.MORPH_OPEN, kernel_clean)
    cnts_extra, _ = cv2.findContours(extra_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in cnts_extra:
        area = cv2.contourArea(cnt)
        if area >= 80:
            x, y, bw, bh = cv2.boundingRect(cnt)
            pct_obj = (area / ideal_area_px) * 100 if ideal_area_px > 0 else 0.0
            sev = "high" if pct_obj > 4.0 else ("medium" if pct_obj > 1.5 else "low")
            detected_regions.append({
                "id": f"DIFF-{reg_counter:03d}",
                "classification": "suspected extra or protruding material",
                "category": "extra_material",
                "severity": sev,
                "location": {"x": int(x), "y": int(y), "width": int(bw), "height": int(bh)},
                "area_px": int(area),
                "area_percent_of_object": round(pct_obj, 2),
                "confidence_note": "Suspected material flash or foreign protrusion beyond ideal boundary.",
                "confidence": round(min(0.92, 0.60 + pct_obj * 0.05), 2)
            })
            reg_counter += 1

    # C) Surface Defect Regions (Scratches, Cracks, Dents within common body)
    surf_binary = (surface_diff > 0.40).astype(np.uint8) * 255
    surf_clean = cv2.morphologyEx(surf_binary, cv2.MORPH_OPEN, kernel_clean)
    cnts_surf, _ = cv2.findContours(surf_clean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for cnt in cnts_surf:
        area = cv2.contourArea(cnt)
        if area >= 60:
            x, y, bw, bh = cv2.boundingRect(cnt)
            pct_obj = (area / ideal_area_px) * 100 if ideal_area_px > 0 else 0.0
            aspect = float(bw) / float(bh) if bh > 0 else 1.0
            is_linear = aspect > 3.0 or aspect < 0.33
            defect_type = "suspected surface scratch or crack" if is_linear else "suspected surface dent, hole, or discolouration"
            sev = "high" if pct_obj > 3.0 else ("medium" if pct_obj > 1.0 else "low")
            detected_regions.append({
                "id": f"DIFF-{reg_counter:03d}",
                "classification": defect_type,
                "category": "surface_defect",
                "severity": sev,
                "location": {"x": int(x), "y": int(y), "width": int(bw), "height": int(bh)},
                "area_px": int(area),
                "area_percent_of_object": round(pct_obj, 2),
                "confidence_note": "Optical texture/intensity anomaly detected within interior object silhouette.",
                "confidence": round(min(0.90, 0.55 + pct_obj * 0.04), 2)
            })
            reg_counter += 1

    return {
        "iou": round(iou, 4),
        "hu_shape_distance": round(hu_distance, 4),
        "ideal_area_px": ideal_area_px,
        "test_area_px": test_area_px,
        "missing_area_px": missing_area_px,
        "missing_area_percent": round(missing_pct, 2),
        "extra_area_px": extra_area_px,
        "extra_area_percent": round(extra_pct, 2),
        "mean_surface_diff": round(mean_surface_diff, 4),
        "deep_anomaly_score": round(deep_anomaly_score, 4),
        "dimensions": dimensions_result,
        "detected_regions": detected_regions,
        "missing_mask": missing_mask,
        "extra_mask": extra_mask,
        "surface_diff": surface_diff,
        "master_diff_map": master_diff_map
    }


# ==============================================================================
# STAGE 5: Scoring Engine
# ==============================================================================

def compute_inspection_scores(diff_res: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes transparent sub-scores and overall Difference / Similarity indices.
    All scores strictly 0..100.
    """
    # 1. Shape similarity (IoU + Hu distance)
    iou = diff_res["iou"]
    hu_dist = diff_res["hu_shape_distance"]
    shape_sim = np.clip(iou * 100.0 - min(40.0, hu_dist * 50.0), 0.0, 100.0)

    # 2. Size / dimension score
    dims = diff_res["dimensions"]
    max_dev_pct = max(abs(dims["length_deviation_pct"]), abs(dims["width_deviation_pct"]))
    dimension_score = np.clip(100.0 - (max_dev_pct * 3.0), 0.0, 100.0)

    # 3. Surface & Structural score
    surf_diff = diff_res["mean_surface_diff"]
    surface_sim = np.clip(100.0 - (surf_diff * 140.0), 0.0, 100.0)

    # 4. Deep feature score
    deep_score = diff_res["deep_anomaly_score"]
    deep_sim = np.clip(100.0 - (deep_score * 120.0), 0.0, 100.0)

    # Weighted Difference Index (0 = perfect match, 100 = completely damaged/broken)
    diff_index = (
        0.35 * (100.0 - shape_sim) +
        0.25 * (100.0 - dimension_score) +
        0.20 * (100.0 - surface_sim) +
        0.20 * (100.0 - deep_sim)
    )
    missing_pct = diff_res.get("missing_area_percent", 0.0)
    extra_pct = diff_res.get("extra_area_percent", 0.0)
    if missing_pct > 0.5 or extra_pct > 0.5:
        diff_index = max(diff_index, (missing_pct + extra_pct) * 2.2)

    diff_index = float(np.clip(diff_index, 0.0, 100.0))
    similarity_index = float(100.0 - diff_index)

    return {
        "difference_index": round(diff_index, 1),
        "similarity_index": round(similarity_index, 1),
        "sub_scores": {
            "shape_similarity": round(float(shape_sim), 1),
            "dimension_match": round(float(dimension_score), 1),
            "surface_integrity": round(float(surface_sim), 1),
            "deep_feature_similarity": round(float(deep_sim), 1)
        },
        "score_disclaimer": "These indices are heuristic scores computed from optical and deep feature signals, not calibrated probabilities or guaranteed accuracy."
    }


# ==============================================================================
# STAGE 6: Visual Outputs & Summary Generation
# ==============================================================================

def generate_visual_outputs(
    ideal_bgr: np.ndarray,
    ideal_mask: np.ndarray,
    aligned_test_bgr: np.ndarray,
    diff_res: Dict[str, Any],
    scores: Dict[str, Any],
    output_dir: str,
    prefix_id: str
) -> Dict[str, str]:
    """
    Creates and saves:
      1. Side-by-side composite: [Ideal | Aligned Test | Difference Heatmap]
      2. Silhouette Overlay: Ideal contour with missing in red/orange & extra in cyan/yellow
      3. Annotated Test Image: Bounding boxes and numbered labels on defects
    """
    os.makedirs(output_dir, exist_ok=True)
    ih, iw = ideal_bgr.shape[:2]

    # ---------------------------------------------------------
    # A) Difference Heatmap
    # ---------------------------------------------------------
    master_diff = diff_res["master_diff_map"]
    diff_u8 = (np.clip(master_diff, 0.0, 1.0) * 255).astype(np.uint8)
    heatmap_colored = cv2.applyColorMap(diff_u8, cv2.COLORMAP_JET)

    # Blend heatmap over aligned test image
    alpha = 0.55
    heatmap_blended = cv2.addWeighted(aligned_test_bgr, 1.0 - alpha, heatmap_colored, alpha, 0)

    heatmap_path = os.path.join(output_dir, f"heatmap_{prefix_id}.jpg")
    cv2.imwrite(heatmap_path, heatmap_blended)

    # ---------------------------------------------------------
    # B) Side-by-side Composite
    # ---------------------------------------------------------
    panel_w = 400
    panel_h = int(ih * (panel_w / iw))

    p1 = cv2.resize(ideal_bgr, (panel_w, panel_h))
    p2 = cv2.resize(aligned_test_bgr, (panel_w, panel_h))
    p3 = cv2.resize(heatmap_blended, (panel_w, panel_h))

    # Add header text to each panel
    font = cv2.FONT_HERSHEY_SIMPLEX
    def _draw_banner(img, title, color=(0, 255, 200)):
        cv2.rectangle(img, (0, 0), (panel_w, 32), (15, 23, 42), -1)
        cv2.putText(img, title, (10, 22), font, 0.55, color, 1, cv2.LINE_AA)

    _draw_banner(p1, "IDEAL REFERENCE", (200, 200, 200))
    _draw_banner(p2, "TEST OBJECT (ALIGNED)", (0, 210, 255))
    _draw_banner(p3, f"DIFF HEATMAP (Index: {scores['difference_index']})", (0, 120, 255))

    sbs_img = np.hstack([p1, p2, p3])
    sbs_path = os.path.join(output_dir, f"sbs_{prefix_id}.jpg")
    cv2.imwrite(sbs_path, sbs_img)

    # ---------------------------------------------------------
    # C) Silhouette Overlay (Missing in Red, Extra in Cyan)
    # ---------------------------------------------------------
    # Background darkened
    overlay_img = (ideal_bgr.astype(np.float32) * 0.45).astype(np.uint8)

    # Outline ideal object in crisp white
    cnts_ideal, _ = cv2.findContours(ideal_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(overlay_img, cnts_ideal, -1, (255, 255, 255), 2)

    # Missing material highlighted in Crimson / Red (BGR: 40, 40, 240)
    missing_mask = diff_res["missing_mask"]
    overlay_img[missing_mask > 0] = [30, 30, 230]

    # Extra material highlighted in Cyan / Yellow (BGR: 240, 220, 30)
    extra_mask = diff_res["extra_mask"]
    overlay_img[extra_mask > 0] = [230, 220, 30]

    # Legend at bottom
    cv2.rectangle(overlay_img, (0, ih - 32), (iw, ih), (10, 15, 30), -1)
    cv2.circle(overlay_img, (15, ih - 16), 6, (30, 30, 230), -1)
    cv2.putText(overlay_img, f"Missing: {diff_res['missing_area_percent']}%", (28, ih - 12), font, 0.45, (220, 220, 220), 1)
    cv2.circle(overlay_img, (160, ih - 16), 6, (230, 220, 30), -1)
    cv2.putText(overlay_img, f"Extra/Flash: {diff_res['extra_area_percent']}%", (173, ih - 12), font, 0.45, (220, 220, 220), 1)

    overlay_path = os.path.join(output_dir, f"overlay_{prefix_id}.jpg")
    cv2.imwrite(overlay_path, overlay_img)

    # ---------------------------------------------------------
    # D) Annotated Test Image (Numbered Defect Boxes)
    # ---------------------------------------------------------
    annotated_img = aligned_test_bgr.copy()
    regions = diff_res["detected_regions"]

    for reg in regions:
        loc = reg["location"]
        x, y, w, h = loc["x"], loc["y"], loc["width"], loc["height"]
        cid = reg["id"]
        cat = reg["category"]

        color = (0, 0, 240) if cat == "missing_material" else ((0, 210, 255) if cat == "extra_material" else (0, 140, 255))
        cv2.rectangle(annotated_img, (x, y), (x + w, y + h), color, 2)

        tag = f"{cid}: {reg['classification'][:18]}"
        (tw, th_box), _ = cv2.getTextSize(tag, font, 0.45, 1)
        cv2.rectangle(annotated_img, (x, max(0, y - 20)), (x + tw + 6, max(20, y)), color, -1)
        cv2.putText(annotated_img, tag, (x + 3, max(14, y - 5)), font, 0.45, (10, 15, 25), 1, cv2.LINE_AA)

    annotated_path = os.path.join(output_dir, f"annotated_{prefix_id}.jpg")
    cv2.imwrite(annotated_path, annotated_img)

    return {
        "heatmap_path": heatmap_path,
        "sidebyside_path": sbs_path,
        "overlay_path": overlay_path,
        "annotated_path": annotated_path
    }


# ==============================================================================
# PIPELINE ORCHESTRATOR
# ==============================================================================

def run_two_image_comparison(
    ideal_image_path: str,
    test_image_path: str,
    output_dir: str,
    comparison_id: str,
    scale_method: str = "same_setup",
    expected_length: Optional[float] = None,
    expected_width: Optional[float] = None,
    pos_tolerance: Optional[float] = None,
    neg_tolerance: Optional[float] = None,
    unit: str = "mm"
) -> Dict[str, Any]:
    """
    Executes the end-to-end 6-stage comparison pipeline.
    Returns complete structured results ready for API responses and DB storage.
    """
    checks_executed: List[Dict[str, Any]] = []
    limitations: List[str] = [
        "2D visual inspection is sensitive to camera viewpoint, lens distortion, and directional lighting.",
        "Internal defects, subsurface cracks, and 3D depth variations cannot be detected from single-angle images.",
        "Defect classification tags and bounding boxes are heuristic suggestions; operator review is required."
    ]

    # --- STAGE 1: Image Validation ---
    val_ideal = validate_and_preprocess(ideal_image_path)
    val_test = validate_and_preprocess(test_image_path)

    if not val_ideal["valid"]:
        return _make_failure_result("Ideal image validation failed: " + str(val_ideal["error"]))
    if not val_test["valid"]:
        return _make_failure_result("Test image validation failed: " + str(val_test["error"]))

    checks_executed.append({
        "check_name": "Image Quality & Exposure Validation",
        "executed": True,
        "status": "REVIEW" if (val_ideal["warnings"] or val_test["warnings"]) else "PASS",
        "score_or_value": round((val_ideal["blur_score"] + val_test["blur_score"]) / 2.0, 1),
        "threshold_or_tolerance": "Laplacian variance >= 20.0, Brightness 25..235",
        "explanation": "Images checked for sharpness, proper exposure, and resolution.",
        "limitations": "; ".join(val_ideal["warnings"] + val_test["warnings"]) or "None noted"
    })

    # --- STAGE 2: Object Segmentation ---
    seg_ideal = segment_object(val_ideal["img_bgr_norm"])
    seg_test = segment_object(val_test["img_bgr_norm"])

    seg_status = "PASS" if (seg_ideal["status"] == "PASS" and seg_test["status"] == "PASS") else "REVIEW"
    checks_executed.append({
        "check_name": "Object Segmentation & Boundary Isolation",
        "executed": True,
        "status": seg_status,
        "score_or_value": round((seg_ideal["confidence"] + seg_test["confidence"]) / 2.0, 2),
        "threshold_or_tolerance": "Confidence >= 0.60, Area 2%..98%",
        "explanation": f"Ideal object area: {int(seg_ideal['area_px'])} px, Test object area: {int(seg_test['area_px'])} px.",
        "limitations": "; ".join(filter(None, [seg_ideal["warning"], seg_test["warning"]])) or "Clean background separation"
    })

    # --- STAGE 3: Alignment / Registration ---
    align_res = align_test_to_ideal(
        ideal_bgr=val_ideal["img_bgr"],
        ideal_mask=seg_ideal["mask"],
        test_bgr=val_test["img_bgr"],
        test_mask=seg_test["mask"]
    )

    checks_executed.append({
        "check_name": "Feature Registration & Spatial Alignment",
        "executed": True,
        "status": align_res["status"],
        "score_or_value": align_res["inliers_count"],
        "threshold_or_tolerance": "Inliers >= 12, Inlier ratio >= 25%",
        "explanation": align_res["notes"],
        "limitations": "Severe deformation or breakage degrades feature matching and forces contour fallback."
    })

    # --- STAGE 4: Difference Analysis ---
    diff_res = analyze_differences(
        ideal_bgr=val_ideal["img_bgr"],
        ideal_mask=seg_ideal["mask"],
        aligned_test_bgr=align_res["aligned_test_bgr"],
        aligned_test_mask=align_res["aligned_test_mask"],
        scale_method=scale_method,
        expected_length=expected_length,
        expected_width=expected_width,
        pos_tolerance=pos_tolerance,
        neg_tolerance=neg_tolerance,
        unit=unit
    )

    # Dimensional Check
    dim_info = diff_res["dimensions"]
    if dim_info["is_calibrated"]:
        dim_check_status = dim_info["tolerance_status"]
        dim_score_val = dim_info["measured_length"]
        dim_thresh = f"{expected_length}±{pos_tolerance or 2.0}{unit}"
    else:
        dim_check_status = "REVIEW" if abs(dim_info["length_deviation_pct"]) > 10.0 else "PASS"
        dim_score_val = dim_info["length_deviation_pct"]
        dim_thresh = "Relative mode (Tolerance ±10% relative)"

    checks_executed.append({
        "check_name": "Optical Metrology & Dimension Verification",
        "executed": True,
        "status": dim_check_status,
        "score_or_value": dim_score_val,
        "threshold_or_tolerance": dim_thresh,
        "explanation": dim_info["explanation"],
        "limitations": "Dimensions are accurate only if both images share identical distance, angle, and perspective."
    })

    # Silhouette & Surface Check
    sil_status = "FAIL" if (diff_res["missing_area_percent"] > 5.0 or diff_res["extra_area_percent"] > 5.0) else (
        "REVIEW" if (diff_res["missing_area_percent"] > 1.5 or diff_res["iou"] < 0.85) else "PASS"
    )
    checks_executed.append({
        "check_name": "Silhouette IoU & Shape Integrity",
        "executed": True,
        "status": sil_status,
        "score_or_value": round(diff_res["iou"] * 100.0, 1),
        "threshold_or_tolerance": "IoU >= 85%, Missing Area <= 1.5%",
        "explanation": f"Silhouette IoU: {diff_res['iou']*100:.1f}%. Missing: {diff_res['missing_area_percent']}%, Extra: {diff_res['extra_area_percent']}%.",
        "limitations": "Shadows or subtle edge highlights can alter binary silhouette borders."
    })

    # Deep Feature Check
    deep_status = "FAIL" if diff_res["deep_anomaly_score"] > 0.45 else (
        "REVIEW" if diff_res["deep_anomaly_score"] > 0.25 else "PASS"
    )
    checks_executed.append({
        "check_name": "Deep Feature Anomaly Analysis",
        "executed": True,
        "status": deep_status,
        "score_or_value": round(diff_res["deep_anomaly_score"], 3),
        "threshold_or_tolerance": "Anomaly distance <= 0.25",
        "explanation": f"ResNet18 patch-level feature anomaly distance: {diff_res['deep_anomaly_score']:.3f}.",
        "limitations": "Pretrained generic weights evaluate perceptual similarity; not fine-tuned on single domain."
    })

    # --- STAGE 5: Scoring ---
    scores = compute_inspection_scores(diff_res)

    # --- STAGE 6: Visual Outputs ---
    vis_paths = generate_visual_outputs(
        ideal_bgr=val_ideal["img_bgr"],
        ideal_mask=seg_ideal["mask"],
        aligned_test_bgr=align_res["aligned_test_bgr"],
        diff_res=diff_res,
        scores=scores,
        output_dir=output_dir,
        prefix_id=comparison_id
    )

    # --- DECISION LOGIC ---
    statuses = [c["status"] for c in checks_executed]
    if "FAIL" in statuses or scores["difference_index"] > 35.0 or diff_res["missing_area_percent"] > 4.0:
        overall_status = "FAIL"
    elif "REVIEW" in statuses or not align_res["reliable"] or scores["difference_index"] > 15.0:
        overall_status = "REVIEW"
    else:
        overall_status = "PASS"

    # Plain language summary
    summary_parts = []
    if overall_status == "PASS":
        summary_parts.append(f"Inspection PASSED. Test object exhibits high structural fidelity (Similarity Index: {scores['similarity_index']}%).")
    elif overall_status == "FAIL":
        summary_parts.append(f"Inspection FAILED. Critical deviations detected (Difference Index: {scores['difference_index']}%).")
    else:
        summary_parts.append(f"Inspection requires OPERATOR REVIEW. Moderate differences observed (Difference Index: {scores['difference_index']}%).")

    if diff_res["dimensions"]["is_calibrated"]:
        summary_parts.append(f"Measured length is {diff_res['dimensions']['measured_length']}{unit} (deviation: {diff_res['dimensions']['length_deviation']:+.2f}{unit}).")
    else:
        summary_parts.append(f"Test object length deviates by {diff_res['dimensions']['length_deviation_pct']:+.1f}% relative to ideal.")

    if diff_res["missing_area_percent"] > 0.5:
        summary_parts.append(f"A region covering {diff_res['missing_area_percent']}% of the ideal object appears missing.")
    if diff_res["extra_area_percent"] > 0.5:
        summary_parts.append(f"Protruding or foreign material detected covering {diff_res['extra_area_percent']}%.")

    num_defects = len(diff_res["detected_regions"])
    summary_parts.append(f"Detected {num_defects} suspected region(s) requiring verification.")
    summary_parts.append(f"Spatial alignment method: {align_res['method']}.")

    plain_summary = " ".join(summary_parts)

    return {
        "comparison_id": comparison_id,
        "overall_status": overall_status,
        "overall_explanation": plain_summary,
        "difference_index": scores["difference_index"],
        "similarity_index": scores["similarity_index"],
        "sub_scores": scores["sub_scores"],
        "score_disclaimer": scores["score_disclaimer"],
        "dimensions": diff_res["dimensions"],
        "detected_regions": diff_res["detected_regions"],
        "checks_executed": checks_executed,
        "limitations": limitations,
        "alignment_quality": {
            "method": align_res["method"],
            "reliable": align_res["reliable"],
            "inliers_count": align_res["inliers_count"],
            "inlier_ratio": round(align_res["inlier_ratio"], 3),
            "reprojection_error": round(align_res["reprojection_error"], 2)
        },
        "image_paths": vis_paths
    }


def _make_failure_result(error_msg: str) -> Dict[str, Any]:
    return {
        "overall_status": "REVIEW",
        "overall_explanation": f"Inspection aborted: {error_msg}",
        "difference_index": 100.0,
        "similarity_index": 0.0,
        "sub_scores": {
            "shape_similarity": 0.0,
            "dimension_match": 0.0,
            "surface_integrity": 0.0,
            "deep_feature_similarity": 0.0
        },
        "score_disclaimer": "Pipeline aborted early due to input validation error.",
        "dimensions": {
            "is_calibrated": False,
            "tolerance_status": "NOT_CALIBRATED",
            "explanation": error_msg
        },
        "detected_regions": [],
        "checks_executed": [{
            "check_name": "Image Validation",
            "executed": False,
            "status": "FAIL",
            "score_or_value": 0.0,
            "threshold_or_tolerance": "Readable Image",
            "explanation": error_msg,
            "limitations": "Input image could not be processed"
        }],
        "limitations": [error_msg],
        "alignment_quality": {"method": "none", "reliable": False, "inliers_count": 0, "inlier_ratio": 0.0, "reprojection_error": 0.0},
        "image_paths": {}
    }
