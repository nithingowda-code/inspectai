import os
import pytest
from fastapi.testclient import TestClient
import numpy as np
import cv2

from backend.app.main import app
from backend.app.database.session import SessionLocal, DATA_DIR
from backend.app.models.product import Product
from backend.app.vision.measurement import analyze_dimensions
from backend.app.ml.anomaly_detector import analyze_anomalies_and_defects

client = TestClient(app)

@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    # Trigger lifespan by using TestClient with context manager
    with TestClient(app) as c:
        yield c

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data

def test_model_status():
    response = client.get("/api/model/status")
    assert response.status_code == 200
    data = response.json()
    assert data["is_ready"] is True
    assert "ResNet" in data["architecture"]
    assert "device_name" in data

def test_dashboard_stats():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_inspections" in data
    assert "pass_rate" in data
    assert "registered_products_count" in data

def test_product_crud():
    # 1. Create product
    payload = {
        "name": "Precision Titanium Bolt M10",
        "category": "Fasteners",
        "description": "Aerospace hex flange bolt",
        "expected_length": 50.0,
        "expected_width": 10.0,
        "expected_thickness": 10.0,
        "unit": "mm",
        "pos_tolerance": 0.5,
        "neg_tolerance": 0.5,
        "calibration_factor": 10.0
    }
    create_res = client.post("/api/products", json=payload)
    assert create_res.status_code == 201
    prod = create_res.json()
    prod_id = prod["id"]
    assert prod["name"] == payload["name"]

    # 2. Get product
    get_res = client.get(f"/api/products/{prod_id}")
    assert get_res.status_code == 200
    assert get_res.json()["category"] == "Fasteners"

    # 3. Update product
    update_res = client.put(f"/api/products/{prod_id}", json={"description": "Updated description"})
    assert update_res.status_code == 200
    assert update_res.json()["description"] == "Updated description"

    # 4. Upload reference image
    test_img = np.full((200, 200, 3), 180, dtype=np.uint8)
    _, img_encoded = cv2.imencode(".jpg", test_img)
    files = {"file": ("test_ref.jpg", img_encoded.tobytes(), "image/jpeg")}
    ref_res = client.post(f"/api/products/{prod_id}/references", files=files, data={"is_primary": "true"})
    assert ref_res.status_code == 200
    assert ref_res.json()["filename"] == "test_ref.jpg"

    # 5. Delete product
    del_res = client.delete(f"/api/products/{prod_id}")
    assert del_res.status_code == 204

def test_optical_metrology_calculation():
    # Create a synthetic rectangular test image: 300x150 pixels on dark background
    test_img_path = os.path.join(DATA_DIR, "uploads", "test_metrology.jpg")
    out_annotated = os.path.join(DATA_DIR, "uploads", "test_metrology_annotated.jpg")
    
    img = np.zeros((400, 500, 3), dtype=np.uint8)
    cv2.rectangle(img, (100, 125), (400, 275), (220, 220, 220), -1)  # 300 wide, 150 high
    cv2.imwrite(test_img_path, img)

    # calibration_factor = 5.0 -> 300/5 = 60.0 mm, 150/5 = 30.0 mm
    res = analyze_dimensions(
        image_path=test_img_path,
        output_annotated_path=out_annotated,
        expected_length=60.0,
        expected_width=30.0,
        pos_tolerance=2.0,
        neg_tolerance=2.0,
        calibration_factor=5.0,
        unit="mm"
    )

    assert res["executed"] is True
    assert res["status"] == "PASS"
    assert abs(res["measured_length"] - 60.0) <= 2.0
    assert abs(res["measured_width"] - 30.0) <= 2.0
    assert os.path.exists(out_annotated)

def test_anomaly_detector_execution():
    test_img_path = os.path.join(DATA_DIR, "uploads", "test_anomaly.jpg")
    out_heatmap = os.path.join(DATA_DIR, "uploads", "test_anomaly_heatmap.jpg")

    # Create image with artificial scratch
    img = np.full((300, 400, 3), 160, dtype=np.uint8)
    cv2.line(img, (150, 100), (250, 200), (20, 20, 20), 4)  # dark scratch
    cv2.imwrite(test_img_path, img)

    res = analyze_anomalies_and_defects(
        inspection_image_path=test_img_path,
        output_heatmap_path=out_heatmap
    )

    assert res["executed"] is True
    assert res["anomaly_score"] is not None
    assert os.path.exists(out_heatmap)
    assert len(res["defects"]) > 0

def test_run_inspection_pipeline_end_to_end():
    # Use one of the seeded sample images
    sample_img = os.path.join(DATA_DIR, "samples", "aerospace_bracket_pass.jpg")
    assert os.path.exists(sample_img), "Seeded sample image should exist"

    with open(sample_img, "rb") as f:
        img_bytes = f.read()

    # Get first product ID
    prods_res = client.get("/api/products")
    prods = prods_res.json()
    assert len(prods) > 0
    prod_id = prods[0]["id"]

    # Run combined inspection
    run_res = client.post(
        "/api/inspections/run",
        files={"file": ("bracket_inspect.jpg", img_bytes, "image/jpeg")},
        data={"product_id": prod_id, "mode": "combined"}
    )
    assert run_res.status_code == 201
    insp_data = run_res.json()
    insp_id = insp_data["id"]
    assert insp_data["overall_status"] in ["PASS", "REVIEW", "FAIL"]
    assert insp_data["mode"] == "combined"
    assert len(insp_data["checks_executed"]) >= 2

    # Verify retrieval from history
    hist_res = client.get(f"/api/inspections/{insp_id}")
    assert hist_res.status_code == 200
    assert hist_res.json()["id"] == insp_id

    # Verify PDF report generation
    rep_res = client.get(f"/api/inspections/{insp_id}/report")
    assert rep_res.status_code == 200
    assert rep_res.headers["content-type"] == "application/pdf"
