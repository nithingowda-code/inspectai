import os
import cv2
import numpy as np
from sqlalchemy.orm import Session
from backend.app.models.product import Product, ProductReference
from backend.app.database.session import DATA_DIR
from backend.app.ml.reference_bank import ProductReferenceBank

def generate_sample_industrial_image(
    filename: str,
    product_type: str,
    defect: str = "none",
    width_px: int = 600,
    height_px: int = 400
) -> str:
    """
    Generates synthetic manufactured component images with realistic industrial
    textures, chamfers, mounting holes, and optional physical defects.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    img = np.full((height_px, width_px, 3), 28, dtype=np.uint8)  # Dark industrial inspection background
    # Subtle background grid pattern
    for x in range(0, width_px, 40):
        cv2.line(img, (x, 0), (x, height_px), (35, 35, 38), 1)
    for y in range(0, height_px, 40):
        cv2.line(img, (0, y), (width_px, y), (35, 35, 38), 1)

    cx, cy = width_px // 2, height_px // 2

    if product_type == "aerospace_bracket":
        # Metallic machined bracket
        base_w, base_h = 420, 210
        if defect == "dimension_fail":
            base_w = 480  # Too long!
        top_left = (cx - base_w // 2, cy - base_h // 2)
        bottom_right = (cx + base_w // 2, cy + base_h // 2)

        # Metallic gradient fill
        bracket = np.zeros((base_h, base_w, 3), dtype=np.uint8)
        for i in range(base_h):
            shade = int(140 + 35 * np.sin(i / 15.0))
            bracket[i, :] = (shade - 10, shade, shade + 15)  # Silver-blue metallic

        img[top_left[1]:bottom_right[1], top_left[0]:bottom_right[0]] = bracket
        cv2.rectangle(img, top_left, bottom_right, (210, 220, 230), 2)  # Chamfer border

        # Machined mounting holes
        cv2.circle(img, (top_left[0] + 50, cy), 22, (20, 20, 24), -1)
        cv2.circle(img, (top_left[0] + 50, cy), 24, (180, 190, 200), 2)
        cv2.circle(img, (bottom_right[0] - 50, cy), 22, (20, 20, 24), -1)
        cv2.circle(img, (bottom_right[0] - 50, cy), 24, (180, 190, 200), 2)

        if defect == "scratch":
            # Sharp scratch across bracket surface
            pts = np.array([[cx - 40, cy - 35], [cx - 10, cy - 10], [cx + 35, cy + 25], [cx + 65, cy + 40]], np.int32)
            cv2.polylines(img, [pts], False, (30, 30, 35), 4)  # Deep groove
            cv2.polylines(img, [pts + 1], False, (240, 245, 255), 2)  # Highlight

        elif defect == "crack":
            # Jagged fracture line
            cv2.line(img, (cx, top_left[1]), (cx + 8, top_left[1] + 25), (15, 15, 18), 3)
            cv2.line(img, (cx + 8, top_left[1] + 25), (cx - 5, top_left[1] + 60), (15, 15, 18), 3)
            cv2.line(img, (cx - 5, top_left[1] + 60), (cx + 12, top_left[1] + 85), (15, 15, 18), 3)

    elif product_type == "smt_pcb":
        # Green FR4 PCB substrate
        base_w, base_h = 360, 240
        if defect == "dimension_fail":
            base_h = 290  # Too tall!
        top_left = (cx - base_w // 2, cy - base_h // 2)
        bottom_right = (cx + base_w // 2, cy + base_h // 2)

        # Dark green solder mask
        cv2.rectangle(img, top_left, bottom_right, (35, 95, 45), -1)
        cv2.rectangle(img, top_left, bottom_right, (180, 200, 120), 2)

        # Copper traces
        for trace_y in range(top_left[1] + 30, bottom_right[1] - 30, 35):
            cv2.line(img, (top_left[0] + 30, trace_y), (bottom_right[0] - 30, trace_y), (70, 140, 190), 2)

        # Microcontroller chip
        chip_w, chip_h = 90, 90
        chip_tl = (cx - chip_w // 2, cy - chip_h // 2)
        chip_br = (cx + chip_w // 2, cy + chip_h // 2)
        cv2.rectangle(img, chip_tl, chip_br, (20, 20, 20), -1)
        cv2.rectangle(img, chip_tl, chip_br, (100, 100, 100), 1)
        cv2.putText(img, "ARM", (cx - 20, cy + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200, 200, 200), 1)

        if defect == "hole":
            # Burn void or puncture hole on PCB
            cv2.circle(img, (cx + 70, cy - 40), 18, (15, 15, 15), -1)
            cv2.circle(img, (cx + 70, cy - 40), 20, (30, 45, 120), 2)

    elif product_type == "polymer_bushing":
        # Circular polymer bushing
        r = 130
        if defect == "dimension_fail":
            r = 155
        cv2.circle(img, (cx, cy), r, (75, 75, 80), -1)
        cv2.circle(img, (cx, cy), r, (120, 120, 130), 2)
        # Inner bore
        cv2.circle(img, (cx, cy), 50, (28, 28, 30), -1)
        cv2.circle(img, (cx, cy), 50, (110, 110, 120), 2)

        if defect == "dent":
            # Perimeter dent void
            dent_center = (cx + r - 10, cy)
            cv2.circle(img, dent_center, 25, (28, 28, 30), -1)

    cv2.imwrite(filename, img)
    return filename

def seed_sample_products_and_images(db: Session):
    """
    Seeds initial reference products and sample inspection images if empty.
    """
    if db.query(Product).count() > 0:
        return

    samples_dir = os.path.join(DATA_DIR, "samples")
    os.makedirs(samples_dir, exist_ok=True)

    products_spec = [
        {
            "name": "Aerospace Titanium Turbine Bracket",
            "category": "Aerospace",
            "description": "High-tensile Ti-6Al-4V machined engine mounting bracket subjected to rigorous optical metrology and surface flaw inspection.",
            "expected_length": 84.0,  # 420 px / 5.0 px/mm = 84.0 mm
            "expected_width": 42.0,   # 210 px / 5.0 px/mm = 42.0 mm
            "expected_thickness": 12.0,
            "unit": "mm",
            "pos_tolerance": 2.0,
            "neg_tolerance": 2.0,
            "calibration_factor": 5.0,
            "sample_key": "aerospace_bracket"
        },
        {
            "name": "Industrial IoT Controller PCB Assembly",
            "category": "Electronics",
            "description": "Dual-layer FR4 industrial embedded controller PCB board with surface-mounted microcontroller and optical fiducial alignment marks.",
            "expected_length": 72.0,  # 360 px / 5.0 px/mm = 72.0 mm
            "expected_width": 48.0,   # 240 px / 5.0 px/mm = 48.0 mm
            "expected_thickness": 1.6,
            "unit": "mm",
            "pos_tolerance": 1.5,
            "neg_tolerance": 1.5,
            "calibration_factor": 5.0,
            "sample_key": "smt_pcb"
        },
        {
            "name": "Polymer Drive Bushing Ring",
            "category": "Mechanical",
            "description": "Precision molded composite bearing bushing with concentric bore for low-friction rotary shaft couplings.",
            "expected_length": 52.0,  # 260 px / 5.0 px/mm = 52.0 mm
            "expected_width": 52.0,   # 260 px / 5.0 px/mm = 52.0 mm
            "expected_thickness": 20.0,
            "unit": "mm",
            "pos_tolerance": 1.5,
            "neg_tolerance": 1.5,
            "calibration_factor": 5.0,
            "sample_key": "polymer_bushing"
        }
    ]

    for p_info in products_spec:
        sample_key = p_info.pop("sample_key")
        product = Product(**p_info)
        db.add(product)
        db.commit()
        db.refresh(product)

        # Generate and attach Golden Reference Image
        ref_dir = os.path.join(DATA_DIR, "references", product.id)
        os.makedirs(ref_dir, exist_ok=True)
        ref_file = os.path.join(ref_dir, "golden_ref_01.jpg")
        generate_sample_industrial_image(ref_file, sample_key, defect="none")

        ref = ProductReference(
            product_id=product.id,
            file_path=ref_file,
            filename="golden_ref_01.jpg",
            is_primary=True
        )
        db.add(ref)
        db.commit()

        # Build visual feature bank for the sample product
        bank = ProductReferenceBank(product.id)
        bank.build_or_update([ref_file])

        # Generate sample inspection images in samples_dir for easy testing
        generate_sample_industrial_image(os.path.join(samples_dir, f"{sample_key}_pass.jpg"), sample_key, defect="none")
        generate_sample_industrial_image(os.path.join(samples_dir, f"{sample_key}_scratch_defect.jpg"), sample_key, defect="scratch" if sample_key == "aerospace_bracket" else ("hole" if sample_key == "smt_pcb" else "dent"))
        generate_sample_industrial_image(os.path.join(samples_dir, f"{sample_key}_dimension_fail.jpg"), sample_key, defect="dimension_fail")

    print("[InspectAI] Successfully seeded sample products, reference images, and test images.")
