import os
import pytest
import numpy as np
import cv2
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.database.session import DATA_DIR
from backend.app.vision.compare import (
    validate_and_preprocess,
    segment_object,
    align_test_to_ideal,
    analyze_differences,
    run_two_image_comparison,
)

client = TestClient(app)

@pytest.fixture
def temp_images_dir():
    test_dir = os.path.join(DATA_DIR, "test_synthetic")
    os.makedirs(test_dir, exist_ok=True)
    return test_dir

def create_base_object_image(w=400, h=300, obj_w=200, obj_h=100, bg_color=30, fg_color=200):
    """Creates a clean synthetic rectangular manufactured object on dark background."""
    img = np.full((h, w, 3), bg_color, dtype=np.uint8)
    x1 = (w - obj_w) // 2
    y1 = (h - obj_h) // 2
    cv2.rectangle(img, (x1, y1), (x1 + obj_w, y1 + obj_h), (fg_color, fg_color, fg_color), -1)
    # Add a couple distinct markings so feature matching has distinct keypoints
    cv2.circle(img, (x1 + 30, y1 + 30), 8, (50, 50, 50), -1)
    cv2.circle(img, (x1 + obj_w - 30, y1 + 30), 8, (50, 50, 50), -1)
    cv2.rectangle(img, (x1 + 70, y1 + 40), (x1 + 130, y1 + 60), (70, 70, 70), -1)
    return img

def test_identical_images_comparison(temp_images_dir):
    """Identical images -> very low Difference Index, alignment succeeds."""
    img = create_base_object_image()
    path_a = os.path.join(temp_images_dir, "identical_a.jpg")
    path_b = os.path.join(temp_images_dir, "identical_b.jpg")
    cv2.imwrite(path_a, img)
    cv2.imwrite(path_b, img)

    res = run_two_image_comparison(
        ideal_image_path=path_a,
        test_image_path=path_b,
        output_dir=temp_images_dir,
        comparison_id="ident_test",
        scale_method="same_setup",
        expected_length=100.0,
        expected_width=50.0
    )

    assert res["overall_status"] == "PASS"
    assert res["difference_index"] < 5.0
    assert res["similarity_index"] > 95.0
    assert res["alignment_quality"]["reliable"] is True

def test_rotated_and_shifted_object_alignment(temp_images_dir):
    """Same object rotated and shifted -> alignment succeeds."""
    img_ideal = create_base_object_image()
    path_ideal = os.path.join(temp_images_dir, "rot_ideal.jpg")
    cv2.imwrite(path_ideal, img_ideal)

    # Rotate by 15 degrees and translate
    h, w = img_ideal.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), 15, 1.0)
    M[0, 2] += 10
    M[1, 2] -= 8
    img_rot = cv2.warpAffine(img_ideal, M, (w, h), borderValue=(30, 30, 30))
    path_rot = os.path.join(temp_images_dir, "rot_test.jpg")
    cv2.imwrite(path_rot, img_rot)

    res = run_two_image_comparison(
        ideal_image_path=path_ideal,
        test_image_path=path_rot,
        output_dir=temp_images_dir,
        comparison_id="rot_test"
    )

    assert res["alignment_quality"]["inliers_count"] >= 8
    assert res["difference_index"] < 25.0

def test_missing_rectangular_piece_detected(temp_images_dir):
    """Object with rectangular piece removed -> missing region detected."""
    img_ideal = create_base_object_image(obj_w=200, obj_h=100)
    path_ideal = os.path.join(temp_images_dir, "missing_ideal.jpg")
    cv2.imwrite(path_ideal, img_ideal)

    # Cut out a piece from the top right corner
    img_broken = img_ideal.copy()
    w, h = 400, 300
    x1 = (w - 200) // 2
    y1 = (h - 100) // 2
    # Missing chunk 40x40 px on right side
    cv2.rectangle(img_broken, (x1 + 150, y1), (x1 + 200, y1 + 40), (30, 30, 30), -1)
    path_broken = os.path.join(temp_images_dir, "missing_broken.jpg")
    cv2.imwrite(path_broken, img_broken)

    res = run_two_image_comparison(
        ideal_image_path=path_ideal,
        test_image_path=path_broken,
        output_dir=temp_images_dir,
        comparison_id="missing_test"
    )

    assert res["overall_status"] in ["FAIL", "REVIEW"]
    # Check that missing regions were detected
    missing_regs = [r for r in res["detected_regions"] if "missing" in r["classification"]]
    assert len(missing_regs) > 0
    assert res["difference_index"] > 5.0

def test_shorter_narrower_object_deviation(temp_images_dir):
    """Object that is shorter -> negative length deviation computed correctly."""
    img_ideal = create_base_object_image(obj_w=200, obj_h=100)
    # Shorter test object: 150 wide instead of 200 (25% shorter)
    img_shorter = create_base_object_image(obj_w=150, obj_h=100)

    path_ideal = os.path.join(temp_images_dir, "short_ideal.jpg")
    path_shorter = os.path.join(temp_images_dir, "short_test.jpg")
    cv2.imwrite(path_ideal, img_ideal)
    cv2.imwrite(path_shorter, img_shorter)

    res = run_two_image_comparison(
        ideal_image_path=path_ideal,
        test_image_path=path_shorter,
        output_dir=temp_images_dir,
        comparison_id="short_test",
        scale_method="same_setup",
        expected_length=100.0,
        expected_width=50.0,
        pos_tolerance=2.0,
        neg_tolerance=2.0
    )

    # Length deviation percentage must be negative
    len_dev_pct = res["dimensions"]["length_deviation_pct"]
    assert len_dev_pct < -10.0
    assert res["dimensions"]["measured_length"] < 100.0
    assert res["overall_status"] in ["FAIL", "REVIEW"]

def test_added_scratch_or_spot_defect(temp_images_dir):
    """Object with added scratch or spot -> surface difference detected."""
    img_ideal = create_base_object_image()
    img_scratched = img_ideal.copy()
    # Draw dark diagonal scratch
    cv2.line(img_scratched, (140, 120), (220, 180), (10, 10, 10), 3)

    path_ideal = os.path.join(temp_images_dir, "scratch_ideal.jpg")
    path_scratched = os.path.join(temp_images_dir, "scratch_test.jpg")
    cv2.imwrite(path_ideal, img_ideal)
    cv2.imwrite(path_scratched, img_scratched)

    res = run_two_image_comparison(
        ideal_image_path=path_ideal,
        test_image_path=path_scratched,
        output_dir=temp_images_dir,
        comparison_id="scratch_test"
    )

    surface_regs = [r for r in res["detected_regions"] if "surface" in r["category"]]
    assert len(surface_regs) > 0

def test_blurred_or_blank_image_never_passes(temp_images_dir):
    """Blank or blurred image -> REVIEW, never PASS."""
    img_ideal = create_base_object_image()
    # Heavily blurred image
    img_blurred = cv2.GaussianBlur(img_ideal, (51, 51), 25.0)

    path_ideal = os.path.join(temp_images_dir, "blur_ideal.jpg")
    path_blurred = os.path.join(temp_images_dir, "blur_test.jpg")
    cv2.imwrite(path_ideal, img_ideal)
    cv2.imwrite(path_blurred, img_blurred)

    res = run_two_image_comparison(
        ideal_image_path=path_ideal,
        test_image_path=path_blurred,
        output_dir=temp_images_dir,
        comparison_id="blur_test"
    )

    assert res["overall_status"] != "PASS"
    assert res["overall_status"] in ["REVIEW", "FAIL"]

def test_relative_only_mode_no_absolute_units(temp_images_dir):
    """Relative-only mode must never output absolute units."""
    img_ideal = create_base_object_image()
    path_ideal = os.path.join(temp_images_dir, "rel_ideal.jpg")
    path_test = os.path.join(temp_images_dir, "rel_test.jpg")
    cv2.imwrite(path_ideal, img_ideal)
    cv2.imwrite(path_test, img_ideal)

    res = run_two_image_comparison(
        ideal_image_path=path_ideal,
        test_image_path=path_test,
        output_dir=temp_images_dir,
        comparison_id="rel_test",
        scale_method="relative_only"
    )

    assert res["dimensions"]["is_calibrated"] is False
    assert res["dimensions"]["unit"] == "%"
    assert res["dimensions"]["measured_length"] is None
    assert res["dimensions"]["tolerance_status"] == "RELATIVE_ONLY"

def test_api_compare_endpoint(temp_images_dir):
    """Tests POST /api/compare endpoint end-to-end via FastAPI TestClient."""
    img = create_base_object_image()
    _, enc = cv2.imencode(".jpg", img)
    img_bytes = enc.tobytes()

    response = client.post(
        "/api/compare",
        files={
            "reference_file": ("ref.jpg", img_bytes, "image/jpeg"),
            "inspection_file": ("test.jpg", img_bytes, "image/jpeg")
        },
        data={
            "expected_length": "100.0",
            "expected_width": "50.0",
            "unit": "mm",
            "scale_method": "same_setup",
            "pos_tolerance": "2.0",
            "neg_tolerance": "2.0"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert "comparison_id" in data
    assert "inspection_id" in data
    assert data["overall_status"] in ["PASS", "REVIEW", "FAIL"]
    assert "difference_index" in data
    assert "similarity_index" in data
    assert "reference_image_url" in data
    assert "inspection_image_url" in data
    assert len(data["checks_executed"]) >= 5
