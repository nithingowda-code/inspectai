# InspectAI — Complete Consolidated Codebase

This document aggregates all source code files for **InspectAI — Universal AI Quality Inspection System** into a single consolidated file.

## Table of Contents

1. [README.md](#readmemd)
2. [.env.example](#envexample)
3. [.gitignore](#gitignore)
4. [scripts/train_anomaly_backbone.py](#scriptstrain_anomaly_backbonepy)
5. [backend/requirements.txt](#backendrequirementstxt)
6. [backend/app/main.py](#backendappmainpy)
7. [backend/app/database/session.py](#backendappdatabasesessionpy)
8. [backend/app/models/__init__.py](#backendappmodels__init__py)
9. [backend/app/models/product.py](#backendappmodelsproductpy)
10. [backend/app/models/inspection.py](#backendappmodelsinspectionpy)
11. [backend/app/models/model_metadata.py](#backendappmodelsmodel_metadatapy)
12. [backend/app/schemas/product.py](#backendappschemasproductpy)
13. [backend/app/schemas/inspection.py](#backendappschemasinspectionpy)
14. [backend/app/schemas/dashboard.py](#backendappschemasdashboardpy)
15. [backend/app/schemas/model_info.py](#backendappschemasmodel_infopy)
16. [backend/app/vision/measurement.py](#backendappvisionmeasurementpy)
17. [backend/app/ml/feature_extractor.py](#backendappmlfeature_extractorpy)
18. [backend/app/ml/reference_bank.py](#backendappmlreference_bankpy)
19. [backend/app/ml/anomaly_detector.py](#backendappmlanomaly_detectorpy)
20. [backend/app/services/inspection_engine.py](#backendappservicesinspection_enginepy)
21. [backend/app/services/report_generator.py](#backendappservicesreport_generatorpy)
22. [backend/app/services/seed_data.py](#backendappservicesseed_datapy)
23. [backend/app/api/health.py](#backendappapihealthpy)
24. [backend/app/api/dashboard.py](#backendappapidashboardpy)
25. [backend/app/api/products.py](#backendappapiproductspy)
26. [backend/app/api/inspections.py](#backendappapiinspectionspy)
27. [backend/app/api/model.py](#backendappapimodelpy)
28. [backend/tests/test_inspectai.py](#backendteststest_inspectaipy)
29. [frontend/package.json](#frontendpackagejson)
30. [frontend/vite.config.ts](#frontendviteconfigts)
31. [frontend/index.html](#frontendindexhtml)
32. [frontend/src/index.css](#frontendsrcindexcss)
33. [frontend/src/main.tsx](#frontendsrcmaintsx)
34. [frontend/src/App.tsx](#frontendsrcapptsx)
35. [frontend/src/types/index.ts](#frontendsrctypesindexts)
36. [frontend/src/services/api.ts](#frontendsrcservicesapits)
37. [frontend/src/components/Navbar.tsx](#frontendsrccomponentsnavbartsx)
38. [frontend/src/components/StatusBadge.tsx](#frontendsrccomponentsstatusbadgetsx)
39. [frontend/src/pages/DashboardPage.tsx](#frontendsrcpagesdashboardpagetsx)
40. [frontend/src/pages/NewInspectionPage.tsx](#frontendsrcpagesnewinspectionpagetsx)
41. [frontend/src/pages/InspectionResultsPage.tsx](#frontendsrcpagesinspectionresultspagetsx)
42. [frontend/src/pages/ProductRegistrationPage.tsx](#frontendsrcpagesproductregistrationpagetsx)
43. [frontend/src/pages/InspectionHistoryPage.tsx](#frontendsrcpagesinspectionhistorypagetsx)
44. [frontend/src/pages/ModelStatusPage.tsx](#frontendsrcpagesmodelstatuspagetsx)

---

## `README.md`

<a id="readmemd"></a>

```markdown
# InspectAI — Universal AI Quality Inspection System

InspectAI is an end-to-end, locally runnable web application and visual intelligence platform designed for manufacturing and industrial quality assurance. It automates sub-pixel optical metrology, deep visual anomaly detection, and reference-bank golden sample compliance checks.

---

## Key Capabilities

1. **Optical Dimensional Metrology:**
   - Detects boundary contours and calculates rotated minimum-area bounding rectangles (`minAreaRect`).
   - Translates pixel dimensions to physical units (`mm`, `cm`, `in`) via optical calibration scaling.
   - Calculates exact deviations: $\text{Deviation} = \text{Measured} - \text{Expected}$.
   - Verifies whether deviations conform to asymmetric tolerances ($-\text{Tol}_{\text{neg}} \le \text{Deviation} \le +\text{Tol}_{\text{pos}}$).
   - Generates an industrial HUD overlay with dimensions, arrows, crosshairs, and bounding boxes.

2. **Visual Anomaly & Surface Defect Detection:**
   - Pretrained ResNet-18 residual feature backbone (`512-dim` global embedding + `Layer 4` spatial patch representation).
   - Evaluates multi-scale patch difference maps against registered golden reference samples.
   - Morphological surface analysis detects sharp cracks, scratches, voids, pits, and localized tears.
   - Generates synthetic continuous anomaly scores ($0.00$ to $1.00$) and visual `JET` colormap heatmap overlays.

3. **Dynamic Product Reference Banks (Zero Downtime):**
   - Register new manufactured components with target dimensions, tolerances, and calibration factors.
   - Upload approved golden reference images; feature embeddings are automatically extracted and indexed into local `.npz` caches.
   - Dynamic comparison without rebuilding or retraining the application.

4. **Deterministic Decision Engine:**
   - **FAIL**: If any required check identifies an out-of-tolerance dimension or confirmed structural defect.
   - **REVIEW**: If a required check fails to execute, image quality is insufficient, or baseline is missing.
   - **PASS**: Only when all required checks succeed and satisfy their quality criteria.

---

## Technology Stack

- **Frontend:** React 19, Vite, TypeScript, Tailwind CSS v4, Lucide Icons.
- **Backend:** Python 3.12, FastAPI, Uvicorn, Pydantic v2, SQLAlchemy, ReportLab.
- **Computer Vision & ML:** PyTorch 2.x, TorchVision (ResNet-18), OpenCV (`cv2`), Pillow, NumPy, Scikit-Learn.
- **Database:** SQLite (`inspectai.db`) with persistent schema and disk-based image caching.

---

## Directory Structure

```text
inspectai/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI app & lifespan initialization
│   │   ├── api/                 # API routers (health, dashboard, products, inspections, model)
│   │   ├── database/            # SQLite engine & session management
│   │   ├── models/              # SQLAlchemy models (Product, InspectionRecord, ModelMetadata)
│   │   ├── schemas/             # Pydantic v2 models
│   │   ├── services/            # Inspection engine, ReportLab PDF generator, data seeding
│   │   ├── vision/              # OpenCV dimensional metrology module
│   │   └── ml/                  # ResNet18 feature extractor, reference bank, anomaly detector
│   ├── requirements.txt
│   └── tests/                   # Pytest test suite (7 comprehensive test cases)
├── frontend/
│   ├── src/
│   │   ├── components/          # Navbar, StatusBadge, ModeBadge
│   │   ├── pages/               # Dashboard, New Inspection, Product Registration, Results, History, Model
│   │   ├── services/api.ts      # API client
│   │   └── types/index.ts       # TypeScript schemas
│   ├── package.json
│   └── vite.config.ts
├── data/
│   ├── uploads/                 # Uploaded inspection frames, annotated HUDs, defect heatmaps
│   ├── references/              # Golden reference images by product ID
│   ├── reports/                 # Generated PDF inspection certificates
│   └── samples/                 # Pre-seeded test images for 1-click evaluation
├── model_artifacts/             # Saved feature embedding banks (.npz)
├── scripts/
│   └── train_anomaly_backbone.py # MVTec AD training & benchmark evaluation script
└── README.md
```

---

## Local Setup & Execution Instructions

### Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Node.js 18+ and npm

---

### Step 1: Backend Setup & Execution

#### On Windows (Command Prompt / PowerShell):
```powershell
# Navigate to project directory
cd inspectai

# Optional: Create and activate a Python virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Start the FastAPI backend server (Runs on port 8000)
python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### On macOS / Linux:
```bash
# Navigate to project directory
cd inspectai

# Optional: Create and activate virtualenv
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r backend/requirements.txt

# Start the FastAPI backend server (Runs on port 8000)
python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

- **Interactive API Documentation:** Open `http://localhost:8000/docs`
- **Health Check:** `http://localhost:8000/api/health`

---

### Step 2: Frontend Setup & Execution

Open a second terminal window:

```bash
cd inspectai/frontend

# Install dependencies (if not already installed)
npm install

# Start Vite dev server (Runs on port 5173)
npm run dev
```

- **InspectAI Web Interface:** Open `http://localhost:5173` in your browser.

---

### Step 3: Running Automated Tests

Run the test suite to verify all API endpoints, database persistence, optical metrology, anomaly detection, and PDF generation:

```bash
cd inspectai
python3 -m pytest backend/tests/test_inspectai.py -v
```

---

## End-to-End Workflow Demonstration

1. **Dashboard Overview:** Open `http://localhost:5173` to see real metrics (Total Inspections, Pass Rate, Defect Breakdown, Model Status).
2. **Product Catalog:** Navigate to **Product Catalog** to see pre-seeded products or register a new product with custom dimensions and tolerances.
3. **Execute Inspection:**
   - Go to **New Inspection**.
   - Select a product or test sample (e.g. click "Titanium Bracket [Pass Sample]" or "Titanium Bracket [Scratch Defect]").
   - Click **EXECUTE QUALITY AUDIT**.
4. **Interactive Results:**
   - Toggle between **Metrology HUD** (dimensions & deviations), **Defect Heatmap** (visual anomaly regions), and **Raw Specimen**.
   - Review the strict PASS / REVIEW / FAIL verdict and checkpoint breakdown.
   - Click **Download PDF** to generate an inspection certificate.
5. **Audit Logs:** Check **Inspection History** to search, filter past inspections, or re-download certificates after browser refresh.

```

---

## `.env.example`

<a id="envexample"></a>

```bash
# InspectAI Environment Configuration
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///data/inspectai.db
ANOMALY_THRESHOLD=0.32
LOG_LEVEL=info

```

---

## `.gitignore`

<a id="gitignore"></a>

```text
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
.venv/
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pytest_cache/

# Node / Frontend
node_modules/
frontend/dist/
frontend/node_modules/
frontend/.vite/
*.local

# Database & Runtime Uploads (Preserve sample templates, ignore transient runtime files)
*.db-journal
.DS_Store
*.swp

```

---

## `scripts/train_anomaly_backbone.py`

<a id="scriptstrain_anomaly_backbonepy"></a>

```python
#!/usr/bin/env python3
"""
InspectAI — Anomaly Detector Training & Evaluation Pipeline
Supports industrial inspection datasets structured similarly to MVTec AD:
  dataset_root/
    category/
      train/
        good/
          *.png / *.jpg
      test/
        good/
          *.png / *.jpg
        defect_type_1/
          *.png / *.jpg
        defect_type_2/
          *.png / *.jpg

Usage:
  python scripts/train_anomaly_backbone.py --dataset_dir ./data/datasets/mvtec --category metal_nut
"""

import os
import argparse
import glob
import numpy as np
from sklearn.metrics import roc_auc_score, precision_recall_fscore_support
from backend.app.ml.feature_extractor import ResNet18FeatureExtractor

def train_and_evaluate(dataset_dir: str, category: str):
    cat_dir = os.path.join(dataset_dir, category)
    if not os.path.exists(cat_dir):
        print(f"[InspectAI] Category path {cat_dir} not found.")
        print("Please download or place the dataset into the directory structure specified above.")
        return

    train_good = glob.glob(os.path.join(cat_dir, "train", "good", "*.*"))
    if not train_good:
        print(f"[InspectAI] No normal training images found in {os.path.join(cat_dir, 'train', 'good')}")
        return

    print(f"[InspectAI] Indexing {len(train_good)} reference images for category '{category}'...")
    extractor = ResNet18FeatureExtractor.get_instance()

    reference_embeddings = []
    for p in train_good:
        g_emb, _ = extractor.extract_features(p)
        if g_emb is not None:
            reference_embeddings.append(g_emb)

    ref_bank = np.array(reference_embeddings)
    print(f"[InspectAI] Reference bank constructed: shape {ref_bank.shape}")

    # Evaluate on test set
    test_good = glob.glob(os.path.join(cat_dir, "test", "good", "*.*"))
    test_defects = [p for p in glob.glob(os.path.join(cat_dir, "test", "*", "*.*")) if "/good/" not in p]

    if not test_good or not test_defects:
        print("[InspectAI] Insufficient test split found (needs both good and defective samples).")
        return

    print(f"[InspectAI] Evaluating on {len(test_good)} normal test samples and {len(test_defects)} defective samples...")
    y_true = []
    y_scores = []

    # Normal samples (label 0)
    for p in test_good:
        g_emb, _ = extractor.extract_features(p)
        if g_emb is not None:
            sims = np.dot(ref_bank, g_emb)
            score = 1.0 - np.max(sims)
            y_scores.append(score)
            y_true.append(0)

    # Defective samples (label 1)
    for p in test_defects:
        g_emb, _ = extractor.extract_features(p)
        if g_emb is not None:
            sims = np.dot(ref_bank, g_emb)
            score = 1.0 - np.max(sims)
            y_scores.append(score)
            y_true.append(1)

    y_true = np.array(y_true)
    y_scores = np.array(y_scores)

    auroc = roc_auc_score(y_true, y_scores)
    # At default threshold 0.32
    y_pred = (y_scores >= 0.32).astype(int)
    prec, rec, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='binary', zero_division=0)

    print("\n================ EVALUATION METRICS ================")
    print(f"Category:  {category}")
    print(f"AUROC:     {auroc:.4f}")
    print(f"Precision: {prec:.4f}")
    print(f"Recall:    {rec:.4f}")
    print(f"F1-Score:  {f1:.4f}")
    print("====================================================\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InspectAI Dataset Anomaly Training and Evaluation")
    parser.add_argument("--dataset_dir", type=str, default="./data/datasets/mvtec", help="Root path of industrial dataset")
    parser.add_argument("--category", type=str, default="metal_nut", help="Target component category")
    args = parser.parse_args()

    train_and_evaluate(args.dataset_dir, args.category)

```

---

## `backend/requirements.txt`

<a id="backendrequirementstxt"></a>

```text
fastapi>=0.110.0
uvicorn[standard]>=0.28.0
pydantic>=2.6.0
sqlalchemy>=2.0.0
python-multipart>=0.0.9
torch>=2.0.0
torchvision>=0.15.0
opencv-python>=4.8.0
pillow>=10.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
reportlab>=4.0.0
pytest>=8.0.0
httpx>=0.27.0

```

---

## `backend/app/main.py`

<a id="backendappmainpy"></a>

```python
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.database.session import engine, Base, SessionLocal, DATA_DIR
from backend.app.services.seed_data import seed_sample_products_and_images

# Import API routers
from backend.app.api.health import router as health_router
from backend.app.api.dashboard import router as dashboard_router
from backend.app.api.products import router as products_router
from backend.app.api.inspections import router as inspections_router
from backend.app.api.model import router as model_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure database schema is created
    print("[InspectAI] Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    
    # Seed default sample data if table is empty
    db = SessionLocal()
    try:
        seed_sample_products_and_images(db)
    finally:
        db.close()
        
    yield
    # Shutdown logic if needed
    print("[InspectAI] Server shutting down cleanly.")

app = FastAPI(
    title="InspectAI — Universal AI Quality Inspection API",
    description="Automated optical metrology, deep visual anomaly detection, and reference-bank product inspection API.",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount data directory for inspection images, heatmaps, references and reports
os.makedirs(DATA_DIR, exist_ok=True)
app.mount("/data", StaticFiles(directory=DATA_DIR), name="data")

# Register routers under /api
app.include_router(health_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(products_router, prefix="/api")
app.include_router(inspections_router, prefix="/api")
app.include_router(model_router, prefix="/api")

@app.get("/")
def root():
    return {
        "message": "InspectAI — Universal AI Quality Inspection API is running.",
        "documentation": "/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)

```

---

## `backend/app/database/session.py`

<a id="backendappdatabasesessionpy"></a>

```python
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Path configuration
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "uploads"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "references"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "reports"), exist_ok=True)
os.makedirs(os.path.join(DATA_DIR, "samples"), exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, "model_artifacts"), exist_ok=True)

DB_PATH = os.path.join(DATA_DIR, "inspectai.db")
DATABASE_URL = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

```

---

## `backend/app/models/__init__.py`

<a id="backendappmodels__init__py"></a>

```python
from backend.app.models.product import Product, ProductReference
from backend.app.models.inspection import InspectionRecord
from backend.app.models.model_metadata import ModelMetadata

__all__ = ["Product", "ProductReference", "InspectionRecord", "ModelMetadata"]

```

---

## `backend/app/models/product.py`

<a id="backendappmodelsproductpy"></a>

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Expected Dimensions
    expected_length = Column(Float, nullable=False, default=100.0)
    expected_width = Column(Float, nullable=False, default=50.0)
    expected_thickness = Column(Float, nullable=True)
    unit = Column(String(20), nullable=False, default="mm")
    
    # Tolerances
    pos_tolerance = Column(Float, nullable=False, default=2.0)
    neg_tolerance = Column(Float, nullable=False, default=2.0)
    
    # Calibration (pixels per physical unit)
    calibration_factor = Column(Float, nullable=False, default=10.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    references = relationship("ProductReference", back_populates="product", cascade="all, delete-orphan")
    inspections = relationship("InspectionRecord", back_populates="product", cascade="all, delete-orphan")

class ProductReference(Base):
    __tablename__ = "product_references"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id"), nullable=False)
    file_path = Column(String(512), nullable=False)
    filename = Column(String(255), nullable=False)
    is_primary = Column(Boolean, default=False)
    embedding_path = Column(String(512), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="references")

```

---

## `backend/app/models/inspection.py`

<a id="backendappmodelsinspectionpy"></a>

```python
import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.app.database.session import Base

class InspectionRecord(Base):
    __tablename__ = "inspection_records"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    product_id = Column(String(36), ForeignKey("products.id"), nullable=True)
    
    # Mode: 'dimensional', 'defect', 'reference', 'combined'
    mode = Column(String(50), nullable=False, default="combined")
    
    # Image file paths
    inspection_image_path = Column(String(512), nullable=False)
    annotated_image_path = Column(String(512), nullable=True)
    heatmap_image_path = Column(String(512), nullable=True)
    reference_image_path = Column(String(512), nullable=True)
    
    # Overall outcome: 'PASS', 'REVIEW', 'FAIL'
    overall_status = Column(String(20), nullable=False, index=True)
    overall_explanation = Column(Text, nullable=False)
    
    # Anomaly / Defect metrics
    anomaly_score = Column(Float, nullable=True)
    anomaly_threshold = Column(Float, nullable=True)
    anomaly_status = Column(String(20), nullable=True)  # PASS, REVIEW, FAIL, NOT_APPLICABLE
    
    # Dimensional metrics
    measured_length = Column(Float, nullable=True)
    measured_width = Column(Float, nullable=True)
    expected_length = Column(Float, nullable=True)
    expected_width = Column(Float, nullable=True)
    length_deviation = Column(Float, nullable=True)
    width_deviation = Column(Float, nullable=True)
    unit = Column(String(20), default="mm")
    dimensional_status = Column(String(20), nullable=True)
    
    # Reference Comparison metrics
    reference_similarity_score = Column(Float, nullable=True)
    reference_status = Column(String(20), nullable=True)
    
    # Detailed structured results (JSON strings)
    detected_defects_json = Column(Text, nullable=True, default="[]")
    checks_executed_json = Column(Text, nullable=True, default="[]")
    limitations_json = Column(Text, nullable=True, default="[]")
    metadata_json = Column(Text, nullable=True, default="{}")
    
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    product = relationship("Product", back_populates="inspections")

```

---

## `backend/app/models/model_metadata.py`

<a id="backendappmodelsmodel_metadatapy"></a>

```python
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, Text
from backend.app.database.session import Base

class ModelMetadata(Base):
    __tablename__ = "model_metadata"

    id = Column(String(50), primary_key=True, default="default_model")
    name = Column(String(255), nullable=False)
    architecture = Column(String(255), nullable=False)
    weights_info = Column(String(255), nullable=False)
    device = Column(String(50), nullable=False)
    embedding_dim = Column(Integer, default=512)
    reference_banks_count = Column(Integer, default=0)
    total_samples_indexed = Column(Integer, default=0)
    last_evaluated_at = Column(DateTime, nullable=True)
    evaluation_metrics_json = Column(Text, nullable=True, default="{}")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

```

---

## `backend/app/schemas/product.py`

<a id="backendappschemasproductpy"></a>

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class ProductReferenceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    file_path: str
    filename: str
    is_primary: bool
    created_at: datetime

class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    expected_length: float = Field(..., gt=0)
    expected_width: float = Field(..., gt=0)
    expected_thickness: Optional[float] = Field(None, gt=0)
    unit: str = Field(default="mm", max_length=20)
    pos_tolerance: float = Field(..., ge=0)
    neg_tolerance: float = Field(..., ge=0)
    calibration_factor: float = Field(default=10.0, gt=0)

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    expected_length: Optional[float] = Field(None, gt=0)
    expected_width: Optional[float] = Field(None, gt=0)
    expected_thickness: Optional[float] = Field(None, gt=0)
    unit: Optional[str] = None
    pos_tolerance: Optional[float] = Field(None, ge=0)
    neg_tolerance: Optional[float] = Field(None, ge=0)
    calibration_factor: Optional[float] = Field(None, gt=0)

class ProductOut(ProductBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime
    references: List[ProductReferenceOut] = []
    inspections_count: int = 0

```

---

## `backend/app/schemas/inspection.py`

<a id="backendappschemasinspectionpy"></a>

```python
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class DefectItem(BaseModel):
    id: str
    type: str  # scratch, crack, tear, hole, dent, surface_irregularity, missing_component, dimension_anomaly
    severity: str  # low, medium, high, critical
    location: Optional[Dict[str, Any]] = None  # bounding box {x, y, width, height}
    confidence: float
    description: str

class CheckResult(BaseModel):
    check_name: str
    executed: bool
    status: str  # PASS, REVIEW, FAIL, SKIPPED
    score_or_value: Optional[float] = None
    threshold_or_tolerance: Optional[str] = None
    explanation: str
    limitations: Optional[str] = None

class InspectionRunRequest(BaseModel):
    product_id: Optional[str] = None
    mode: str = "combined"  # 'dimensional', 'defect', 'reference', 'combined'
    calibration_factor: Optional[float] = None  # override pixels_per_unit if supplied
    custom_expected_length: Optional[float] = None
    custom_expected_width: Optional[float] = None
    custom_tolerance: Optional[float] = None

class InspectionRecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    product_id: Optional[str] = None
    product_name: Optional[str] = None
    mode: str
    inspection_image_path: str
    annotated_image_path: Optional[str] = None
    heatmap_image_path: Optional[str] = None
    reference_image_path: Optional[str] = None
    
    overall_status: str  # PASS, REVIEW, FAIL
    overall_explanation: str
    
    anomaly_score: Optional[float] = None
    anomaly_threshold: Optional[float] = None
    anomaly_status: Optional[str] = None
    
    measured_length: Optional[float] = None
    measured_width: Optional[float] = None
    expected_length: Optional[float] = None
    expected_width: Optional[float] = None
    length_deviation: Optional[float] = None
    width_deviation: Optional[float] = None
    unit: str
    dimensional_status: Optional[str] = None
    
    reference_similarity_score: Optional[float] = None
    reference_status: Optional[str] = None
    
    detected_defects: List[DefectItem] = []
    checks_executed: List[CheckResult] = []
    limitations: List[str] = []
    metadata: Dict[str, Any] = {}
    
    created_at: datetime

```

---

## `backend/app/schemas/dashboard.py`

<a id="backendappschemasdashboardpy"></a>

```python
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.app.schemas.inspection import InspectionRecordOut

class DashboardStats(BaseModel):
    total_inspections: int
    passed_inspections: int
    failed_inspections: int
    review_inspections: int
    pass_rate: float
    registered_products_count: int
    total_references_count: int
    model_ready: bool
    model_device: str
    recent_inspections: List[InspectionRecordOut]
    category_distribution: Dict[str, int]
    daily_trend: List[Dict[str, Any]]

```

---

## `backend/app/schemas/model_info.py`

<a id="backendappschemasmodel_infopy"></a>

```python
from datetime import datetime
from typing import Dict, Any, Optional
from pydantic import BaseModel

class ModelStatusOut(BaseModel):
    is_ready: bool
    model_name: str
    architecture: str
    backbone: str
    embedding_dim: int
    device: str
    device_name: str
    weights_status: str
    total_reference_banks: int
    total_reference_embeddings: int
    supported_defect_types: list[str]
    last_evaluated_at: Optional[datetime] = None
    evaluation_metrics: Dict[str, Any] = {}
    training_instructions: str

```

---

## `backend/app/vision/measurement.py`

<a id="backendappvisionmeasurementpy"></a>

```python
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

```

---

## `backend/app/ml/feature_extractor.py`

<a id="backendappmlfeature_extractorpy"></a>

```python
import os
import torch
import torch.nn as nn
from torchvision import models, transforms
from torchvision.models import ResNet18_Weights
from PIL import Image
import numpy as np
from typing import Tuple, Optional, List

class ResNet18FeatureExtractor:
    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        # Select optimal device (Apple Silicon MPS -> CUDA -> CPU)
        if torch.backends.mps.is_available() and torch.backends.mps.is_built():
            self.device = torch.device("mps")
            self.device_name = "Apple Silicon MPS"
        elif torch.cuda.is_available():
            self.device = torch.device("cuda")
            self.device_name = f"NVIDIA CUDA ({torch.cuda.get_device_name(0)})"
        else:
            self.device = torch.device("cpu")
            self.device_name = "Host CPU"

        print(f"[InspectAI] Initializing ResNet18 on {self.device_name}...")

        try:
            # Load ResNet18 with default pretrained ImageNet weights
            weights = ResNet18_Weights.DEFAULT
            base_model = models.resnet18(weights=weights)
            self.weights_status = "Pretrained ImageNet-1K Weights"
        except Exception as e:
            print(f"[InspectAI] Warning: could not download weights ({e}), using initialized backbone")
            base_model = models.resnet18(weights=None)
            self.weights_status = "Local Initialized Weights"

        base_model.eval()
        base_model.to(self.device)

        # Truncate before final classification head to keep spatial feature maps
        # Layers 0..7 produce [Batch, 512, H_feat, W_feat]
        self.feature_backbone = nn.Sequential(*list(base_model.children())[:-2]).to(self.device)
        self.feature_backbone.eval()

        self.avg_pool = nn.AdaptiveAvgPool2d((1, 1))

        # Standard industrial normalization
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225]
            )
        ])

    def preprocess_image(self, image_path: str) -> Optional[torch.Tensor]:
        if not os.path.exists(image_path):
            return None
        try:
            img = Image.open(image_path).convert("RGB")
            tensor = self.transform(img).unsqueeze(0).to(self.device)
            return tensor
        except Exception as e:
            print(f"[InspectAI] Preprocess error for {image_path}: {e}")
            return None

    def extract_features(self, image_path: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray]]:
        """
        Extracts both global embedding (512-dim) and spatial patch features (512, 8, 8).
        Returns:
            global_embedding: np.ndarray shape (512,)
            spatial_features: np.ndarray shape (512, 8, 8)
        """
        tensor = self.preprocess_image(image_path)
        if tensor is None:
            return None, None

        with torch.no_grad():
            # [1, 512, 8, 8]
            spatial = self.feature_backbone(tensor)
            # [1, 512, 1, 1]
            pooled = self.avg_pool(spatial)
            global_emb = pooled.squeeze().cpu().numpy()
            
            # Normalize global vector for cosine similarity
            norm = np.linalg.norm(global_emb)
            if norm > 1e-6:
                global_emb = global_emb / norm

            spatial_np = spatial.squeeze(0).cpu().numpy()  # (512, 8, 8)
            return global_emb, spatial_np

```

---

## `backend/app/ml/reference_bank.py`

<a id="backendappmlreference_bankpy"></a>

```python
import os
import numpy as np
from typing import List, Dict, Any, Optional
from backend.app.ml.feature_extractor import ResNet18FeatureExtractor

ARTIFACTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../model_artifacts/products"))
os.makedirs(ARTIFACTS_DIR, exist_ok=True)

class ProductReferenceBank:
    def __init__(self, product_id: str):
        self.product_id = product_id
        self.cache_file = os.path.join(ARTIFACTS_DIR, f"{product_id}_bank.npz")
        self.global_embeddings: List[np.ndarray] = []
        self.spatial_features: List[np.ndarray] = []
        self.reference_paths: List[str] = []
        self.load()

    def load(self):
        if os.path.exists(self.cache_file):
            try:
                data = np.load(self.cache_file, allow_pickle=True)
                self.global_embeddings = list(data["global_embeddings"])
                self.spatial_features = list(data["spatial_features"])
                self.reference_paths = list(data["reference_paths"])
            except Exception as e:
                print(f"[InspectAI] Error loading bank cache {self.cache_file}: {e}")

    def save(self):
        try:
            np.savez_compressed(
                self.cache_file,
                global_embeddings=np.array(self.global_embeddings),
                spatial_features=np.array(self.spatial_features),
                reference_paths=np.array(self.reference_paths)
            )
        except Exception as e:
            print(f"[InspectAI] Error saving bank cache {self.cache_file}: {e}")

    def build_or_update(self, reference_image_paths: List[str]):
        extractor = ResNet18FeatureExtractor.get_instance()
        new_globals = []
        new_spatials = []
        valid_paths = []

        for path in reference_image_paths:
            if not os.path.exists(path):
                continue
            g_emb, s_feat = extractor.extract_features(path)
            if g_emb is not None and s_feat is not None:
                new_globals.append(g_emb)
                new_spatials.append(s_feat)
                valid_paths.append(path)

        self.global_embeddings = new_globals
        self.spatial_features = new_spatials
        self.reference_paths = valid_paths
        self.save()

    def is_ready(self) -> bool:
        return len(self.global_embeddings) > 0

    def get_reference_count(self) -> int:
        return len(self.global_embeddings)

    def compute_anomaly_distance(self, inspection_global: np.ndarray, inspection_spatial: np.ndarray) -> Dict[str, Any]:
        """
        Calculates minimum distance to reference bank:
        1. Global cosine distance = 1.0 - max(dot(inspection, ref))
        2. Patch-level spatial anomaly distance map (8x8)
        """
        if not self.is_ready():
            return {
                "min_global_distance": 1.0,
                "similarity_score": 0.0,
                "best_ref_idx": -1,
                "spatial_diff_map": None
            }

        # Global cosine similarities
        sims = [float(np.dot(inspection_global, ref_emb)) for ref_emb in self.global_embeddings]
        best_idx = int(np.argmax(sims))
        max_sim = float(sims[best_idx])
        # Cosine distance in [0, 2], typically [0, 1] for positive normalized vectors
        global_dist = max(0.0, 1.0 - max_sim)

        # Spatial patch anomaly map compared to the best matching golden reference
        ref_spatial = self.spatial_features[best_idx]  # shape (512, 8, 8)
        # L2 norm across channel dimension (512) for each 8x8 patch
        diff = inspection_spatial - ref_spatial
        spatial_patch_dist = np.linalg.norm(diff, axis=0)  # shape (8, 8)

        return {
            "min_global_distance": round(global_dist, 4),
            "similarity_score": round(max_sim, 4),
            "best_ref_idx": best_idx,
            "best_ref_path": self.reference_paths[best_idx],
            "spatial_diff_map": spatial_patch_dist
        }

```

---

## `backend/app/ml/anomaly_detector.py`

<a id="backendappmlanomaly_detectorpy"></a>

```python
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

```

---

## `backend/app/services/inspection_engine.py`

<a id="backendappservicesinspection_enginepy"></a>

```python
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

```

---

## `backend/app/services/report_generator.py`

<a id="backendappservicesreport_generatorpy"></a>

```python
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from backend.app.models.inspection import InspectionRecord
from backend.app.database.session import DATA_DIR

def generate_pdf_report(inspection: InspectionRecord, product_name: str = "Unassigned Product") -> str:
    """
    Generates a formal industrial inspection PDF certificate and returns the file path.
    """
    reports_dir = os.path.join(DATA_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    report_filename = f"Inspection_Report_{inspection.id[:8]}.pdf"
    pdf_path = os.path.join(reports_dir, report_filename)

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0F172A')
    )
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569')
    )
    section_title = ParagraphStyle(
        'SectionTitle',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1E293B'),
        spaceBefore=10,
        spaceAfter=6
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155')
    )

    story = []

    # Header
    story.append(Paragraph("INSPECT-AI // QUALITY ASSURANCE REPORT", title_style))
    story.append(Paragraph(f"Universal AI Optical Metrology & Surface Inspection System | Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}", subtitle_style))
    story.append(Spacer(1, 12))

    # Status Banner
    status_bg = colors.HexColor('#DC2626') if inspection.overall_status == "FAIL" else (
        colors.HexColor('#16A34A') if inspection.overall_status == "PASS" else colors.HexColor('#D97706')
    )
    status_data = [
        [
            Paragraph(f"<b>INSPECTION ID:</b> {inspection.id}", body_style),
            Paragraph(f"<b>OVERALL STATUS:</b> <font color='white'><b>{inspection.overall_status}</b></font>", ParagraphStyle('StatusCell', parent=body_style, textColor=colors.white))
        ]
    ]
    status_table = Table(status_data, colWidths=[340, 200])
    status_table.setStyle(TableStyle([
        ('BACKGROUND', (1, 0), (1, 0), status_bg),
        ('BACKGROUND', (0, 0), (0, 0), colors.HexColor('#F1F5F9')),
        ('ALIGN', (1, 0), (1, 0), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('BOX', (0, 0), (-1, -1), 1, colors.HexColor('#CBD5E1')),
    ]))
    story.append(status_table)
    story.append(Spacer(1, 10))

    # Product & Inspection Details Table
    info_data = [
        [Paragraph("<b>Target Product:</b>", body_style), Paragraph(product_name, body_style),
         Paragraph("<b>Inspection Mode:</b>", body_style), Paragraph(inspection.mode.upper(), body_style)],
        [Paragraph("<b>Timestamp:</b>", body_style), Paragraph(inspection.created_at.strftime('%Y-%m-%d %H:%M:%S'), body_style),
         Paragraph("<b>Unit of Measure:</b>", body_style), Paragraph(inspection.unit, body_style)],
    ]
    info_table = Table(info_data, colWidths=[100, 170, 100, 170])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8FAFC')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E2E8F0')),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 12))

    # Executive Explanation
    story.append(Paragraph("<b>Executive Summary & Decision Rationale:</b>", section_title))
    story.append(Paragraph(inspection.overall_explanation, body_style))
    story.append(Spacer(1, 10))

    # Dimensional Metrology Section
    if inspection.measured_length is not None or inspection.measured_width is not None:
        story.append(Paragraph("<b>1. Dimensional Optical Metrology</b>", section_title))
        dim_data = [
            [Paragraph("<b>Dimension</b>", body_style), Paragraph("<b>Expected</b>", body_style),
             Paragraph("<b>Measured</b>", body_style), Paragraph("<b>Deviation</b>", body_style), Paragraph("<b>Result</b>", body_style)],
            [Paragraph("Length", body_style),
             Paragraph(f"{inspection.expected_length:.2f} {inspection.unit}" if inspection.expected_length else "N/A", body_style),
             Paragraph(f"{inspection.measured_length:.2f} {inspection.unit}" if inspection.measured_length else "N/A", body_style),
             Paragraph(f"{inspection.length_deviation:+.2f} {inspection.unit}" if inspection.length_deviation else "N/A", body_style),
             Paragraph(f"<b>{inspection.dimensional_status or 'N/A'}</b>", body_style)],
            [Paragraph("Width", body_style),
             Paragraph(f"{inspection.expected_width:.2f} {inspection.unit}" if inspection.expected_width else "N/A", body_style),
             Paragraph(f"{inspection.measured_width:.2f} {inspection.unit}" if inspection.measured_width else "N/A", body_style),
             Paragraph(f"{inspection.width_deviation:+.2f} {inspection.unit}" if inspection.width_deviation else "N/A", body_style),
             Paragraph(f"<b>{inspection.dimensional_status or 'N/A'}</b>", body_style)]
        ]
        dim_table = Table(dim_data, colWidths=[100, 110, 110, 110, 110])
        dim_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 5),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
        ]))
        story.append(dim_table)
        story.append(Spacer(1, 10))

    # Anomaly and Defect Detection Section
    story.append(Paragraph("<b>2. AI Visual Defect & Anomaly Analysis</b>", section_title))
    defects = json.loads(inspection.detected_defects_json or "[]")
    
    anomaly_summary_data = [
        [Paragraph("<b>Metric</b>", body_style), Paragraph("<b>Observed Value</b>", body_style), Paragraph("<b>Threshold / Criteria</b>", body_style), Paragraph("<b>Status</b>", body_style)],
        [Paragraph("Anomaly Score", body_style), Paragraph(f"{inspection.anomaly_score:.3f}" if inspection.anomaly_score is not None else "N/A", body_style), Paragraph(f"≤ {inspection.anomaly_threshold:.2f}" if inspection.anomaly_threshold else "N/A", body_style), Paragraph(f"<b>{inspection.anomaly_status or 'N/A'}</b>", body_style)],
        [Paragraph("Reference Similarity", body_style), Paragraph(f"{inspection.reference_similarity_score:.3f}" if inspection.reference_similarity_score is not None else "N/A", body_style), Paragraph("≥ 0.700", body_style), Paragraph(f"<b>{inspection.reference_status or 'N/A'}</b>", body_style)],
        [Paragraph("Detected Flaws Count", body_style), Paragraph(str(len(defects)), body_style), Paragraph("0 Permitted", body_style), Paragraph("PASS" if len(defects) == 0 else "FAIL", body_style)],
    ]
    anom_table = Table(anomaly_summary_data, colWidths=[140, 130, 140, 130])
    anom_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(anom_table)
    story.append(Spacer(1, 10))

    # Checks breakdown
    checks = json.loads(inspection.checks_executed_json or "[]")
    if checks:
        story.append(Paragraph("<b>3. Executed Quality Checkpoints</b>", section_title))
        checks_data = [[Paragraph("<b>Check Name</b>", body_style), Paragraph("<b>Executed</b>", body_style), Paragraph("<b>Status</b>", body_style), Paragraph("<b>Details</b>", body_style)]]
        for c in checks:
            checks_data.append([
                Paragraph(c.get("check_name", ""), body_style),
                Paragraph("YES" if c.get("executed") else "NO", body_style),
                Paragraph(f"<b>{c.get('status', '')}</b>", body_style),
                Paragraph(c.get("explanation", "")[:120], body_style)
            ])
        checks_table = Table(checks_data, colWidths=[150, 60, 70, 260])
        checks_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E2E8F0')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#CBD5E1')),
            ('PADDING', (0, 0), (-1, -1), 4),
        ]))
        story.append(checks_table)
        story.append(Spacer(1, 10))

    # Technical Disclaimers and Limitations
    limitations = json.loads(inspection.limitations_json or "[]")
    if limitations:
        story.append(Paragraph("<b>Technical Disclaimers & System Boundaries:</b>", section_title))
        for lim in limitations:
            story.append(Paragraph(f"• {lim}", ParagraphStyle('LimItem', parent=body_style, textColor=colors.HexColor('#64748B'))))
        story.append(Spacer(1, 10))

    # Sign-off footer
    story.append(Spacer(1, 15))
    sign_data = [
        [Paragraph("<b>Inspection Algorithm:</b> ResNet18 + OpenCV Metrology", subtitle_style),
         Paragraph("<b>Authorized Verification:</b> InspectAI System", subtitle_style)]
    ]
    sign_table = Table(sign_data, colWidths=[270, 270])
    story.append(sign_table)

    doc.build(story)
    return pdf_path

```

---

## `backend/app/services/seed_data.py`

<a id="backendappservicesseed_datapy"></a>

```python
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

```

---

## `backend/app/api/health.py`

<a id="backendappapihealthpy"></a>

```python
from fastapi import APIRouter
from datetime import datetime

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("")
def check_health():
    return {
        "status": "healthy",
        "service": "InspectAI Quality Inspection System",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

```

---

## `backend/app/api/dashboard.py`

<a id="backendappapidashboardpy"></a>

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Dict, Any

from backend.app.database.session import get_db
from backend.app.models.inspection import InspectionRecord
from backend.app.models.product import Product, ProductReference
from backend.app.schemas.dashboard import DashboardStats
from backend.app.api.inspections import format_inspection_out
from backend.app.ml.feature_extractor import ResNet18FeatureExtractor

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(db: Session = Depends(get_db)):
    total = db.query(InspectionRecord).count()
    passed = db.query(InspectionRecord).filter(InspectionRecord.overall_status == "PASS").count()
    failed = db.query(InspectionRecord).filter(InspectionRecord.overall_status == "FAIL").count()
    review = db.query(InspectionRecord).filter(InspectionRecord.overall_status == "REVIEW").count()
    
    pass_rate = round((passed / total * 100.0), 1) if total > 0 else 0.0

    products_count = db.query(Product).count()
    references_count = db.query(ProductReference).count()

    # Recent inspections (up to 6)
    recent = db.query(InspectionRecord).order_by(InspectionRecord.created_at.desc()).limit(6).all()
    recent_outs = [format_inspection_out(r) for r in recent]

    # Category distribution of products
    categories = db.query(Product.category, func.count(Product.id)).group_by(Product.category).all()
    cat_dist = {cat: count for cat, count in categories}

    # Daily trend (last 7 days from records)
    now = datetime.utcnow()
    trend = []
    for i in range(6, -1, -1):
        day_date = (now - timedelta(days=i)).date()
        day_start = datetime.combine(day_date, datetime.min.time())
        day_end = datetime.combine(day_date, datetime.max.time())
        
        day_total = db.query(InspectionRecord).filter(
            InspectionRecord.created_at >= day_start,
            InspectionRecord.created_at <= day_end
        ).count()
        day_passed = db.query(InspectionRecord).filter(
            InspectionRecord.created_at >= day_start,
            InspectionRecord.created_at <= day_end,
            InspectionRecord.overall_status == "PASS"
        ).count()
        day_failed = db.query(InspectionRecord).filter(
            InspectionRecord.created_at >= day_start,
            InspectionRecord.created_at <= day_end,
            InspectionRecord.overall_status == "FAIL"
        ).count()
        day_review = db.query(InspectionRecord).filter(
            InspectionRecord.created_at >= day_start,
            InspectionRecord.created_at <= day_end,
            InspectionRecord.overall_status == "REVIEW"
        ).count()

        trend.append({
            "date": day_date.strftime("%b %d"),
            "total": day_total,
            "pass": day_passed,
            "fail": day_failed,
            "review": day_review
        })

    extractor = ResNet18FeatureExtractor.get_instance()

    return DashboardStats(
        total_inspections=total,
        passed_inspections=passed,
        failed_inspections=failed,
        review_inspections=review,
        pass_rate=pass_rate,
        registered_products_count=products_count,
        total_references_count=references_count,
        model_ready=True,
        model_device=extractor.device_name,
        recent_inspections=recent_outs,
        category_distribution=cat_dist,
        daily_trend=trend
    )

```

---

## `backend/app/api/products.py`

<a id="backendappapiproductspy"></a>

```python
import os
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from sqlalchemy.orm import Session

from backend.app.database.session import get_db, DATA_DIR
from backend.app.models.product import Product, ProductReference
from backend.app.schemas.product import ProductCreate, ProductUpdate, ProductOut, ProductReferenceOut
from backend.app.ml.reference_bank import ProductReferenceBank

router = APIRouter(prefix="/products", tags=["Products"])

def format_product_out(p: Product) -> ProductOut:
    return ProductOut(
        id=p.id,
        name=p.name,
        category=p.category,
        description=p.description,
        expected_length=p.expected_length,
        expected_width=p.expected_width,
        expected_thickness=p.expected_thickness,
        unit=p.unit,
        pos_tolerance=p.pos_tolerance,
        neg_tolerance=p.neg_tolerance,
        calibration_factor=p.calibration_factor,
        created_at=p.created_at,
        updated_at=p.updated_at,
        references=[ProductReferenceOut.model_validate(r) for r in p.references],
        inspections_count=len(p.inspections) if p.inspections else 0
    )

@router.get("", response_model=List[ProductOut])
def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).order_by(Product.created_at.desc()).all()
    return [format_product_out(p) for p in products]

@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    product = Product(
        name=payload.name,
        category=payload.category,
        description=payload.description,
        expected_length=payload.expected_length,
        expected_width=payload.expected_width,
        expected_thickness=payload.expected_thickness,
        unit=payload.unit,
        pos_tolerance=payload.pos_tolerance,
        neg_tolerance=payload.neg_tolerance,
        calibration_factor=payload.calibration_factor
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return format_product_out(product)

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")
    return format_product_out(p)

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: str, payload: ProductUpdate, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    update_data = payload.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        if val is not None:
            setattr(p, field, val)

    db.commit()
    db.refresh(p)
    return format_product_out(p)

@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: str, db: Session = Depends(get_db)):
    p = db.query(Product).filter(Product.id == product_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Product not found")

    # Clean up reference files
    for ref in p.references:
        if os.path.exists(ref.file_path):
            try:
                os.remove(ref.file_path)
            except OSError:
                pass

    db.delete(p)
    db.commit()
    return None

@router.post("/{product_id}/references", response_model=ProductReferenceOut)
async def upload_reference_image(
    product_id: str,
    file: UploadFile = File(...),
    is_primary: bool = Form(False),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Validate file type
    allowed_types = ["image/jpeg", "image/png", "image/webp", "image/bmp"]
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Invalid image file format. Supported: JPEG, PNG, WEBP, BMP")

    ref_dir = os.path.join(DATA_DIR, "references", product_id)
    os.makedirs(ref_dir, exist_ok=True)

    ext = os.path.splitext(file.filename or "")[1] or ".jpg"
    safe_filename = f"ref_{uuid.uuid4().hex[:12]}{ext}"
    dest_path = os.path.join(ref_dir, safe_filename)

    contents = await file.read()
    with open(dest_path, "wb") as f:
        f.write(contents)

    ref = ProductReference(
        product_id=product_id,
        file_path=dest_path,
        filename=file.filename or safe_filename,
        is_primary=is_primary or (len(product.references) == 0)
    )
    db.add(ref)
    db.commit()
    db.refresh(ref)

    # Immediately update the product's visual feature bank
    all_refs = db.query(ProductReference).filter(ProductReference.product_id == product_id).all()
    all_paths = [r.file_path for r in all_refs if os.path.exists(r.file_path)]
    bank = ProductReferenceBank(product_id)
    bank.build_or_update(all_paths)

    return ProductReferenceOut.model_validate(ref)

@router.delete("/{product_id}/references/{ref_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reference_image(product_id: str, ref_id: str, db: Session = Depends(get_db)):
    ref = db.query(ProductReference).filter(
        ProductReference.id == ref_id,
        ProductReference.product_id == product_id
    ).first()
    if not ref:
        raise HTTPException(status_code=404, detail="Reference image not found")

    if os.path.exists(ref.file_path):
        try:
            os.remove(ref.file_path)
        except OSError:
            pass

    db.delete(ref)
    db.commit()

    # Rebuild reference bank with remaining references
    remaining_refs = db.query(ProductReference).filter(ProductReference.product_id == product_id).all()
    all_paths = [r.file_path for r in remaining_refs if os.path.exists(r.file_path)]
    bank = ProductReferenceBank(product_id)
    bank.build_or_update(all_paths)

    return None

```

---

## `backend/app/api/inspections.py`

<a id="backendappapiinspectionspy"></a>

```python
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

```

---

## `backend/app/api/model.py`

<a id="backendappapimodelpy"></a>

```python
import os
import glob
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from backend.app.database.session import get_db, BASE_DIR
from backend.app.schemas.model_info import ModelStatusOut
from backend.app.ml.feature_extractor import ResNet18FeatureExtractor
from backend.app.models.product import ProductReference

router = APIRouter(prefix="/model", tags=["Model Status"])

@router.get("/status", response_model=ModelStatusOut)
def get_model_status(db: Session = Depends(get_db)):
    extractor = ResNet18FeatureExtractor.get_instance()
    
    # Check physical cache files in model_artifacts
    artifacts_dir = os.path.join(BASE_DIR, "model_artifacts", "products")
    bank_files = glob.glob(os.path.join(artifacts_dir, "*_bank.npz"))
    
    # Check total reference embeddings in database
    total_refs = db.query(ProductReference).count()

    training_guide = (
        "Dataset Training & Fine-Tuning Instructions:\n"
        "1. Standard Reference Bank: Adding approved product reference images extracts ResNet18 layer-4 embeddings automatically (Zero retraining delay).\n"
        "2. Custom Anomaly Fine-Tuning: To train a customized patch autoencoder or Wide-ResNet50 backbone on industrial datasets (e.g., MVTec AD):\n"
        "   - Place normal training images into data/training/<product_name>/train/good/\n"
        "   - Place test defect samples into data/training/<product_name>/test/<defect_type>/\n"
        "   - Run: python scripts/train_anomaly_backbone.py --category <product_name>\n"
        "3. Metrics are evaluated on actual test splits with AUROC, Precision, and Recall recorded in model_metadata."
    )

    return ModelStatusOut(
        is_ready=True,
        model_name="InspectAI Visual Quality Engine",
        architecture="ResNet-18 Feature Extractor + Multi-Scale Patch Difference Bank & OpenCV Metrology",
        backbone="torchvision.models.resnet18",
        embedding_dim=512,
        device=str(extractor.device),
        device_name=extractor.device_name,
        weights_status=extractor.weights_status,
        total_reference_banks=len(bank_files),
        total_reference_embeddings=total_refs,
        supported_defect_types=[
            "Surface Scratches & Gouges",
            "Cracks & Fractures",
            "Surface Pits & Dent Voids",
            "Holes & Punctures",
            "Edge Tears & Notches",
            "Missing Components & Misalignment",
            "Dimensional Out-of-Tolerance"
        ],
        last_evaluated_at=None,
        evaluation_metrics={
            "status": "Untrained / Reference-Bank Zero-Shot Baseline",
            "note": "Evaluation metrics will populate when a benchmark dataset (e.g. MVTec AD) test run is executed via scripts/train_anomaly_backbone.py."
        },
        training_instructions=training_guide
    )

```

---

## `backend/tests/test_inspectai.py`

<a id="backendteststest_inspectaipy"></a>

```python
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

```

---

## `frontend/package.json`

<a id="frontendpackagejson"></a>

```json
{
  "name": "frontend",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "lint": "oxlint",
    "preview": "vite preview"
  },
  "dependencies": {
    "@tailwindcss/vite": "^4.3.3",
    "lucide-react": "^1.55.0",
    "react": "^19.2.8",
    "react-dom": "^19.2.8",
    "tailwindcss": "^4.3.3"
  },
  "devDependencies": {
    "@types/node": "^24.13.3",
    "@types/react": "^19.2.18",
    "@types/react-dom": "^19.2.7",
    "@vitejs/plugin-react": "^6.1.1",
    "oxlint": "^1.81.0",
    "typescript": "~6.0.2",
    "vite": "^8.3.0"
  }
}

```

---

## `frontend/vite.config.ts`

<a id="frontendviteconfigts"></a>

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    tailwindcss(),
  ],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
      '/data': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})

```

---

## `frontend/index.html`

<a id="frontendindexhtml"></a>

```html
<!doctype html>
<html lang="en" class="dark">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2306b6d4' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='12' cy='12' r='10'/><path d='m4.93 4.93 4.24 4.24'/><path d='m14.83 9.17 4.24-4.24'/><path d='m14.83 14.83 4.24 4.24'/><path d='m9.17 14.83-4.24 4.24'/></svg>" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>InspectAI — Universal AI Quality Inspection System</title>
    <meta name="description" content="AI-powered optical metrology, sub-pixel dimensional verification, and deep visual anomaly detection system for manufacturing." />
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
  </head>
  <body class="bg-[#070b12] text-slate-100 antialiased selection:bg-cyan-500 selection:text-black">
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
  </body>
</html>

```

---

## `frontend/src/index.css`

<a id="frontendsrcindexcss"></a>

```css
@import "tailwindcss";

@layer base {
  :root {
    --bg-main: #090d16;
    --bg-card: #0f172a;
    --bg-card-hover: #1e293b;
    --border-color: #1e293b;
    --border-glow: #06b6d4;
    --cyan-accent: #06b6d4;
    --cyan-glow: rgba(6, 182, 212, 0.25);
  }

  body {
    background-color: #070b12;
    color: #e2e8f0;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    min-height: 100vh;
    overflow-x: hidden;
  }

  /* Custom high-tech scrollbar */
  ::-webkit-scrollbar {
    width: 6px;
    height: 6px;
  }
  ::-webkit-scrollbar-track {
    background: #090d16;
  }
  ::-webkit-scrollbar-thumb {
    background: #1e293b;
    border-radius: 3px;
  }
  ::-webkit-scrollbar-thumb:hover {
    background: #06b6d4;
  }
}

/* Radar scanning grid effect */
.industrial-grid {
  background-image: 
    linear-gradient(to right, rgba(255, 255, 255, 0.03) 1px, transparent 1px),
    linear-gradient(to bottom, rgba(255, 255, 255, 0.03) 1px, transparent 1px);
  background-size: 32px 32px;
}

.radar-beam {
  background: linear-gradient(180deg, rgba(6, 182, 212, 0) 0%, rgba(6, 182, 212, 0.35) 50%, rgba(6, 182, 212, 0.8) 100%);
}

@keyframes scanline {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(1000%); }
}

.animate-scan {
  animation: scanline 3s linear infinite;
}

```

---

## `frontend/src/main.tsx`

<a id="frontendsrcmaintsx"></a>

```tsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
)

```

---

## `frontend/src/App.tsx`

<a id="frontendsrcapptsx"></a>

```tsx
import { useState, useEffect } from 'react';
import { Navbar } from './components/Navbar';
import { DashboardPage } from './pages/DashboardPage';
import { NewInspectionPage } from './pages/NewInspectionPage';
import { InspectionResultsPage } from './pages/InspectionResultsPage';
import { ProductRegistrationPage } from './pages/ProductRegistrationPage';
import { InspectionHistoryPage } from './pages/InspectionHistoryPage';
import { ModelStatusPage } from './pages/ModelStatusPage';

export function App() {
  const [currentTab, setCurrentTab] = useState<string>('dashboard');
  const [activeInspectionId, setActiveInspectionId] = useState<string | null>(null);
  const [systemStatus, setSystemStatus] = useState<'connected' | 'error' | 'checking'>('checking');

  // Verify backend connectivity
  const checkHealth = async () => {
    try {
      const res = await fetch('/api/health');
      if (res.ok) {
        setSystemStatus('connected');
      } else {
        setSystemStatus('error');
      }
    } catch {
      setSystemStatus('error');
    }
  };

  useEffect(() => {
    checkHealth();
    const interval = setInterval(checkHealth, 20000);
    return () => clearInterval(interval);
  }, []);

  const handleNavigate = (tab: string, inspectionId?: string) => {
    if (inspectionId) {
      setActiveInspectionId(inspectionId);
      setCurrentTab('results');
    } else {
      setCurrentTab(tab);
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handleInspectionComplete = (inspectionId: string) => {
    setActiveInspectionId(inspectionId);
    setCurrentTab('results');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-[#070b12] text-slate-100 flex flex-col industrial-grid">
      {/* Top Navbar */}
      <Navbar
        currentTab={currentTab}
        onTabChange={(tab) => handleNavigate(tab)}
        systemStatus={systemStatus}
      />

      {/* Main Content Area */}
      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 pt-6 sm:pt-8">
        {currentTab === 'dashboard' && (
          <DashboardPage onNavigate={handleNavigate} />
        )}

        {currentTab === 'inspect' && (
          <NewInspectionPage
            onInspectionComplete={handleInspectionComplete}
            onNavigateToProducts={() => handleNavigate('products')}
          />
        )}

        {currentTab === 'results' && activeInspectionId && (
          <InspectionResultsPage
            inspectionId={activeInspectionId}
            onBack={() => handleNavigate('dashboard')}
            onInspectAgain={() => handleNavigate('inspect')}
          />
        )}

        {currentTab === 'products' && (
          <ProductRegistrationPage
            onStartInspection={(_productId) => {
              handleNavigate('inspect');
            }}
          />
        )}

        {currentTab === 'history' && (
          <InspectionHistoryPage
            onSelectInspection={(id) => handleNavigate('results', id)}
          />
        )}

        {currentTab === 'model' && (
          <ModelStatusPage />
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950/80 py-6 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-slate-500 font-mono">
          <div>
            <span className="text-slate-300 font-bold">InspectAI System</span> // Universal AI Manufacturing Quality Metrology
          </div>
          <div className="flex items-center space-x-4">
            <span>FastAPI • PyTorch ResNet18 • OpenCV • SQLite</span>
            <span>Local Offline Architecture</span>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;

```

---

## `frontend/src/types/index.ts`

<a id="frontendsrctypesindexts"></a>

```typescript
export interface ProductReference {
  id: string;
  file_path: string;
  filename: string;
  is_primary: boolean;
  created_at: string;
}

export interface Product {
  id: string;
  name: string;
  category: string;
  description?: string;
  expected_length: number;
  expected_width: number;
  expected_thickness?: number;
  unit: string;
  pos_tolerance: number;
  neg_tolerance: number;
  calibration_factor: number;
  created_at: string;
  updated_at: string;
  references: ProductReference[];
  inspections_count: number;
}

export interface DefectItem {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  location?: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  confidence: number;
  description: string;
}

export interface CheckResult {
  check_name: string;
  executed: boolean;
  status: 'PASS' | 'REVIEW' | 'FAIL' | 'SKIPPED';
  score_or_value?: number | null;
  threshold_or_tolerance?: string | null;
  explanation: string;
  limitations?: string | null;
}

export interface InspectionRecord {
  id: string;
  product_id?: string | null;
  product_name?: string | null;
  mode: 'dimensional' | 'defect' | 'reference' | 'combined';
  inspection_image_path: string;
  annotated_image_path?: string | null;
  heatmap_image_path?: string | null;
  reference_image_path?: string | null;
  overall_status: 'PASS' | 'REVIEW' | 'FAIL';
  overall_explanation: string;
  anomaly_score?: number | null;
  anomaly_threshold?: number | null;
  anomaly_status?: string | null;
  measured_length?: number | null;
  measured_width?: number | null;
  expected_length?: number | null;
  expected_width?: number | null;
  length_deviation?: number | null;
  width_deviation?: number | null;
  unit: string;
  dimensional_status?: string | null;
  reference_similarity_score?: number | null;
  reference_status?: string | null;
  detected_defects: DefectItem[];
  checks_executed: CheckResult[];
  limitations: string[];
  metadata: Record<string, any>;
  created_at: string;
}

export interface DashboardStats {
  total_inspections: number;
  passed_inspections: number;
  failed_inspections: number;
  review_inspections: number;
  pass_rate: number;
  registered_products_count: number;
  total_references_count: number;
  model_ready: boolean;
  model_device: string;
  recent_inspections: InspectionRecord[];
  category_distribution: Record<string, number>;
  daily_trend: Array<{
    date: string;
    total: number;
    pass: number;
    fail: number;
    review: number;
  }>;
}

export interface ModelStatus {
  is_ready: boolean;
  model_name: string;
  architecture: string;
  backbone: string;
  embedding_dim: number;
  device: string;
  device_name: string;
  weights_status: string;
  total_reference_banks: number;
  total_reference_embeddings: number;
  supported_defect_types: string[];
  last_evaluated_at?: string | null;
  evaluation_metrics: Record<string, any>;
  training_instructions: string;
}

```

---

## `frontend/src/services/api.ts`

<a id="frontendsrcservicesapits"></a>

```typescript
import type {
  Product,
  InspectionRecord,
  DashboardStats,
  ModelStatus,
  ProductReference
} from '../types';

const API_BASE = '/api';

export function getImageUrl(filePath: string | null | undefined): string {
  if (!filePath) return '';
  if (filePath.startsWith('http://') || filePath.startsWith('https://')) {
    return filePath;
  }
  const idx = filePath.indexOf('/data/');
  if (idx !== -1) {
    return filePath.substring(idx);
  }
  if (filePath.startsWith('data/')) {
    return '/' + filePath;
  }
  return `/data/${filePath}`;
}

export async function fetchDashboardStats(): Promise<DashboardStats> {
  const res = await fetch(`${API_BASE}/dashboard/stats`);
  if (!res.ok) throw new Error(`Failed to fetch dashboard statistics: ${res.statusText}`);
  return res.json();
}

export async function fetchProducts(): Promise<Product[]> {
  const res = await fetch(`${API_BASE}/products`);
  if (!res.ok) throw new Error(`Failed to fetch products: ${res.statusText}`);
  return res.json();
}

export async function fetchProduct(id: string): Promise<Product> {
  const res = await fetch(`${API_BASE}/products/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch product: ${res.statusText}`);
  return res.json();
}

export async function createProduct(productData: Partial<Product>): Promise<Product> {
  const res = await fetch(`${API_BASE}/products`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to create product: ${res.statusText}`);
  }
  return res.json();
}

export async function updateProduct(id: string, productData: Partial<Product>): Promise<Product> {
  const res = await fetch(`${API_BASE}/products/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(productData),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to update product: ${res.statusText}`);
  }
  return res.json();
}

export async function deleteProduct(id: string): Promise<void> {
  const res = await fetch(`${API_BASE}/products/${id}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete product: ${res.statusText}`);
}

export async function uploadReferenceImage(
  productId: string,
  file: File,
  isPrimary: boolean = false
): Promise<ProductReference> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('is_primary', String(isPrimary));

  const res = await fetch(`${API_BASE}/products/${productId}/references`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Failed to upload reference image: ${res.statusText}`);
  }
  return res.json();
}

export async function deleteReferenceImage(productId: string, refId: string): Promise<void> {
  const res = await fetch(`${API_BASE}/products/${productId}/references/${refId}`, {
    method: 'DELETE',
  });
  if (!res.ok) throw new Error(`Failed to delete reference: ${res.statusText}`);
}

export async function runInspection(formData: FormData): Promise<InspectionRecord> {
  const res = await fetch(`${API_BASE}/inspections/run`, {
    method: 'POST',
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Inspection failed: ${res.statusText}`);
  }
  return res.json();
}

export async function fetchInspections(params: {
  productId?: string;
  status?: string;
  mode?: string;
  search?: string;
  limit?: number;
  offset?: number;
} = {}): Promise<InspectionRecord[]> {
  const query = new URLSearchParams();
  if (params.productId) query.append('product_id', params.productId);
  if (params.status) query.append('status', params.status);
  if (params.mode) query.append('mode', params.mode);
  if (params.search) query.append('search', params.search);
  if (params.limit) query.append('limit', String(params.limit));
  if (params.offset) query.append('offset', String(params.offset));

  const res = await fetch(`${API_BASE}/inspections?${query.toString()}`);
  if (!res.ok) throw new Error(`Failed to fetch inspections: ${res.statusText}`);
  return res.json();
}

export async function fetchInspection(id: string): Promise<InspectionRecord> {
  const res = await fetch(`${API_BASE}/inspections/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch inspection details: ${res.statusText}`);
  return res.json();
}

export async function fetchModelStatus(): Promise<ModelStatus> {
  const res = await fetch(`${API_BASE}/model/status`);
  if (!res.ok) throw new Error(`Failed to fetch model status: ${res.statusText}`);
  return res.json();
}

export function getPdfReportUrl(id: string): string {
  return `${API_BASE}/inspections/${id}/report`;
}

export function getJsonReportUrl(id: string): string {
  return `${API_BASE}/inspections/${id}/report/json`;
}

```

---

## `frontend/src/components/Navbar.tsx`

<a id="frontendsrccomponentsnavbartsx"></a>

```tsx
import React from 'react';
import { 
  Activity, 
  Scan, 
  Layers, 
  History, 
  Cpu
} from 'lucide-react';

interface NavbarProps {
  currentTab: string;
  onTabChange: (tab: string) => void;
  systemStatus: 'connected' | 'error' | 'checking';
}

export const Navbar: React.FC<NavbarProps> = ({
  currentTab,
  onTabChange,
  systemStatus
}) => {
  const navItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'inspect', label: 'New Inspection', icon: Scan },
    { id: 'products', label: 'Product Catalog', icon: Layers },
    { id: 'history', label: 'Inspection History', icon: History },
    { id: 'model', label: 'Model Intelligence', icon: Cpu },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800 bg-slate-950/80 backdrop-blur-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand */}
          <div className="flex items-center space-x-3 cursor-pointer" onClick={() => onTabChange('dashboard')}>
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20 border border-cyan-400/30">
              <Scan className="w-5 h-5 text-white animate-pulse" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="text-xl font-bold tracking-tight text-white font-mono">
                  Inspect<span className="text-cyan-400">AI</span>
                </span>
                <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-cyan-950 text-cyan-300 border border-cyan-800 tracking-wider">
                  Industrial v1.0
                </span>
              </div>
              <p className="text-xs text-slate-400 hidden sm:block">Universal AI Quality Inspection System</p>
            </div>
          </div>

          {/* Navigation Items */}
          <nav className="hidden md:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => onTabChange(item.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-md text-sm font-medium transition-all duration-200 ${
                    isActive
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 shadow-sm shadow-cyan-500/10'
                      : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Engine Status Indicator */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 px-3 py-1 rounded-full bg-slate-900 border border-slate-800 text-xs">
              <span className="relative flex h-2 w-2">
                {systemStatus === 'connected' ? (
                  <>
                    <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                  </>
                ) : (
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-rose-500"></span>
                )}
              </span>
              <span className="text-slate-300 font-mono text-xs">
                {systemStatus === 'connected' ? 'ENGINE ONLINE' : 'ENGINE OFFLINE'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile nav bar */}
      <div className="flex md:hidden border-t border-slate-800 bg-slate-950 px-2 py-1 justify-around">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={`p-2 flex flex-col items-center text-xs ${
                isActive ? 'text-cyan-400' : 'text-slate-400'
              }`}
            >
              <Icon className="w-5 h-5 mb-0.5" />
              <span className="text-[10px]">{item.label}</span>
            </button>
          );
        })}
      </div>
    </header>
  );
};

```

---

## `frontend/src/components/StatusBadge.tsx`

<a id="frontendsrccomponentsstatusbadgetsx"></a>

```tsx
import React from 'react';
import { CheckCircle2, AlertTriangle, XCircle, HelpCircle } from 'lucide-react';

interface StatusBadgeProps {
  status: string;
  size?: 'sm' | 'md' | 'lg';
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({ status, size = 'md' }) => {
  const norm = (status || '').toUpperCase();

  let bg = 'bg-slate-800 text-slate-300 border-slate-700';
  let Icon = HelpCircle;

  if (norm === 'PASS') {
    bg = 'bg-emerald-950/80 text-emerald-400 border-emerald-500/40 shadow-sm shadow-emerald-950';
    Icon = CheckCircle2;
  } else if (norm === 'FAIL') {
    bg = 'bg-rose-950/80 text-rose-400 border-rose-500/40 shadow-sm shadow-rose-950';
    Icon = XCircle;
  } else if (norm === 'REVIEW') {
    bg = 'bg-amber-950/80 text-amber-300 border-amber-500/40 shadow-sm shadow-amber-950';
    Icon = AlertTriangle;
  }

  const sizeClasses = {
    sm: 'text-xs px-2 py-0.5 space-x-1',
    md: 'text-xs px-2.5 py-1 space-x-1.5',
    lg: 'text-sm px-3.5 py-1.5 space-x-2 font-semibold',
  };

  const iconSizes = {
    sm: 'w-3 h-3',
    md: 'w-3.5 h-3.5',
    lg: 'w-4 h-4',
  };

  return (
    <span
      className={`inline-flex items-center font-mono font-medium rounded-full border tracking-wide uppercase ${bg} ${sizeClasses[size]}`}
    >
      <Icon className={iconSizes[size]} />
      <span>{norm}</span>
    </span>
  );
};

export const ModeBadge: React.FC<{ mode: string }> = ({ mode }) => {
  const colors: Record<string, string> = {
    dimensional: 'bg-blue-950 text-blue-300 border-blue-800',
    defect: 'bg-purple-950 text-purple-300 border-purple-800',
    reference: 'bg-amber-950 text-amber-300 border-amber-800',
    combined: 'bg-cyan-950 text-cyan-300 border-cyan-700',
  };

  const labels: Record<string, string> = {
    dimensional: 'Dimensional Metrology',
    defect: 'Defect Analysis',
    reference: 'Golden Reference',
    combined: 'Combined System',
  };

  const m = (mode || 'combined').toLowerCase();

  return (
    <span className={`inline-flex items-center text-[11px] px-2 py-0.5 rounded border font-mono ${colors[m] || 'bg-slate-800 text-slate-300 border-slate-700'}`}>
      {labels[m] || m}
    </span>
  );
};

```

---

## `frontend/src/pages/DashboardPage.tsx`

<a id="frontendsrcpagesdashboardpagetsx"></a>

```tsx
import React, { useEffect, useState } from 'react';
import { 
  CheckCircle2, 
  XCircle, 
  AlertTriangle, 
  Scan, 
  Layers, 
  ArrowUpRight, 
  Cpu, 
  RefreshCw,
  Plus,
  Clock
} from 'lucide-react';
import type { DashboardStats, Product } from '../types';
import { fetchDashboardStats, fetchProducts } from '../services/api';
import { StatusBadge, ModeBadge } from '../components/StatusBadge';

interface DashboardPageProps {
  onNavigate: (tab: string, inspectionId?: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [statsData, prodsData] = await Promise.all([
        fetchDashboardStats(),
        fetchProducts()
      ]);
      setStats(statsData);
      setProducts(prodsData);
    } catch (err: any) {
      setError(err.message || 'Failed to connect to backend server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading && !stats) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-slate-400 font-mono text-sm">Querying inspection database & hardware telemetry...</p>
      </div>
    );
  }

  if (error && !stats) {
    return (
      <div className="p-8 max-w-4xl mx-auto">
        <div className="bg-rose-950/40 border border-rose-800/60 rounded-xl p-6 text-center space-y-3">
          <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto" />
          <h3 className="text-lg font-bold text-white">Connection Error</h3>
          <p className="text-sm text-slate-300">{error}</p>
          <button
            onClick={loadData}
            className="px-4 py-2 bg-rose-600 hover:bg-rose-500 text-white rounded-lg text-sm font-medium transition-colors"
          >
            Retry Connection
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-12">
      {/* Top Banner / Hero */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <h1 className="text-3xl font-bold tracking-tight text-white font-mono">
            MISSION CONTROL // <span className="text-cyan-400">QUALITY AUDIT</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Real-time optical metrology, deep anomaly scores, and golden reference compliance telemetry.
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <button
            onClick={loadData}
            className="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg transition-colors"
            title="Refresh statistics"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
          <button
            onClick={() => onNavigate('products')}
            className="flex items-center space-x-2 px-4 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white rounded-lg text-sm font-medium transition-colors"
          >
            <Plus className="w-4 h-4 text-cyan-400" />
            <span>Register Product</span>
          </button>
          <button
            onClick={() => onNavigate('inspect')}
            className="flex items-center space-x-2 px-5 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-sm transition-all shadow-lg shadow-cyan-500/20"
          >
            <Scan className="w-4 h-4" />
            <span>New Inspection</span>
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Total Inspections */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-slate-400">Total Inspections</span>
            <span className="p-2 bg-slate-800 rounded-lg text-slate-300">
              <Scan className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline space-x-3">
            <span className="text-3xl font-bold text-white font-mono">{stats?.total_inspections ?? 0}</span>
            <span className="text-xs text-slate-400 font-mono">records in DB</span>
          </div>
          <div className="mt-2 text-xs text-slate-500 flex items-center space-x-1">
            <span>Pass rate:</span>
            <span className="font-semibold text-emerald-400">{stats?.pass_rate ?? 0}%</span>
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-gradient-to-r from-blue-500 to-cyan-500" />
        </div>

        {/* Passed */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-emerald-400">Passed Quality</span>
            <span className="p-2 bg-emerald-950/60 text-emerald-400 border border-emerald-800/40 rounded-lg">
              <CheckCircle2 className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline space-x-3">
            <span className="text-3xl font-bold text-emerald-400 font-mono">{stats?.passed_inspections ?? 0}</span>
            <span className="text-xs text-slate-400">within tolerances</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Acceptance standard fully verified
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-emerald-500" />
        </div>

        {/* Failed */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-rose-400">Rejected / Failed</span>
            <span className="p-2 bg-rose-950/60 text-rose-400 border border-rose-800/40 rounded-lg">
              <XCircle className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline space-x-3">
            <span className="text-3xl font-bold text-rose-400 font-mono">{stats?.failed_inspections ?? 0}</span>
            <span className="text-xs text-slate-400">anomalous / out-of-tol</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Flaws or dimensional deviation flagged
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-rose-500" />
        </div>

        {/* Requiring Review */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 relative overflow-hidden group hover:border-slate-700 transition-all">
          <div className="flex items-center justify-between">
            <span className="text-xs font-mono uppercase tracking-wider text-amber-400">Operator Review</span>
            <span className="p-2 bg-amber-950/60 text-amber-400 border border-amber-800/40 rounded-lg">
              <AlertTriangle className="w-4 h-4" />
            </span>
          </div>
          <div className="mt-3 flex items-baseline space-x-3">
            <span className="text-3xl font-bold text-amber-400 font-mono">{stats?.review_inspections ?? 0}</span>
            <span className="text-xs text-slate-400">inconclusive / uncalibrated</span>
          </div>
          <div className="mt-2 text-xs text-slate-500">
            Requires human visual verification
          </div>
          <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-amber-500" />
        </div>
      </div>

      {/* Hardware & Model Readiness Status Banner */}
      <div className="bg-slate-900 border border-cyan-900/40 rounded-xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/30">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-lg bg-cyan-950 text-cyan-400 border border-cyan-800 flex items-center justify-center">
            <Cpu className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-sm font-semibold text-white">AI Vision Engine: ResNet-18 Backbone Active</span>
              <span className="text-[10px] font-mono px-2 py-0.5 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800">
                {stats?.model_device || 'Host CPU'}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Multi-scale patch anomaly estimation • Zero-shot reference comparison • OpenCV sub-pixel metrology
            </p>
          </div>
        </div>
        <button
          onClick={() => onNavigate('model')}
          className="flex items-center space-x-1.5 text-xs text-cyan-400 hover:text-cyan-300 font-medium px-3 py-1.5 rounded-md bg-cyan-950/50 border border-cyan-800/60 self-start sm:self-auto transition-colors"
        >
          <span>View Model Intelligence</span>
          <ArrowUpRight className="w-3.5 h-3.5" />
        </button>
      </div>

      {/* Main Content: Recent Inspections & Product Catalog */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Recent Inspections Table (2 columns wide) */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Clock className="w-4 h-4 text-cyan-400" />
              <h2 className="text-base font-bold text-white font-mono uppercase tracking-wide">
                Recent Quality Audits
              </h2>
            </div>
            <button
              onClick={() => onNavigate('history')}
              className="text-xs text-cyan-400 hover:text-cyan-300 flex items-center space-x-1 font-mono"
            >
              <span>View Full History ({stats?.total_inspections ?? 0})</span>
              <ArrowUpRight className="w-3 h-3" />
            </button>
          </div>

          <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden">
            {stats?.recent_inspections && stats.recent_inspections.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-950/80 text-slate-400 border-b border-slate-800 font-mono">
                    <tr>
                      <th className="py-3 px-4">Inspection ID</th>
                      <th className="py-3 px-4">Product</th>
                      <th className="py-3 px-4">Mode</th>
                      <th className="py-3 px-4">Anomaly</th>
                      <th className="py-3 px-4">Outcome</th>
                      <th className="py-3 px-4 text-right">Action</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800/60 text-slate-300">
                    {stats.recent_inspections.map((rec) => (
                      <tr 
                        key={rec.id} 
                        className="hover:bg-slate-800/40 transition-colors cursor-pointer group"
                        onClick={() => onNavigate('results', rec.id)}
                      >
                        <td className="py-3.5 px-4 font-mono font-medium text-cyan-400">
                          {rec.id.substring(0, 8)}...
                        </td>
                        <td className="py-3.5 px-4 font-medium text-white max-w-[160px] truncate">
                          {rec.product_name || 'Generic Sample'}
                        </td>
                        <td className="py-3.5 px-4">
                          <ModeBadge mode={rec.mode} />
                        </td>
                        <td className="py-3.5 px-4 font-mono">
                          {rec.anomaly_score !== null && rec.anomaly_score !== undefined ? (
                            <span className={rec.anomaly_score >= (rec.anomaly_threshold || 0.32) ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                              {rec.anomaly_score.toFixed(3)}
                            </span>
                          ) : (
                            <span className="text-slate-500">—</span>
                          )}
                        </td>
                        <td className="py-3.5 px-4">
                          <StatusBadge status={rec.overall_status} size="sm" />
                        </td>
                        <td className="py-3.5 px-4 text-right">
                          <span className="text-xs text-slate-400 group-hover:text-cyan-400 inline-flex items-center space-x-1">
                            <span>Open</span>
                            <ArrowUpRight className="w-3 h-3" />
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="p-8 text-center space-y-3">
                <Scan className="w-8 h-8 text-slate-600 mx-auto" />
                <p className="text-sm text-slate-400">No inspection records logged yet.</p>
                <button
                  onClick={() => onNavigate('inspect')}
                  className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-semibold"
                >
                  Run First Inspection
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Registered Products Quick Card (1 column wide) */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Layers className="w-4 h-4 text-cyan-400" />
              <h2 className="text-base font-bold text-white font-mono uppercase tracking-wide">
                Registered Catalog ({products.length})
              </h2>
            </div>
            <button
              onClick={() => onNavigate('products')}
              className="text-xs text-cyan-400 hover:text-cyan-300 font-mono"
            >
              Manage
            </button>
          </div>

          <div className="space-y-3">
            {products.slice(0, 4).map((p) => (
              <div
                key={p.id}
                onClick={() => onNavigate('products')}
                className="bg-slate-900/90 border border-slate-800 hover:border-slate-700 p-4 rounded-xl cursor-pointer transition-all hover:bg-slate-800/40 space-y-2"
              >
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-white text-sm truncate max-w-[180px]">{p.name}</span>
                  <span className="text-[10px] uppercase font-mono px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                    {p.category}
                  </span>
                </div>
                <div className="flex items-center justify-between text-xs text-slate-400 font-mono">
                  <span>Target: {p.expected_length}×{p.expected_width} {p.unit}</span>
                  <span className="text-slate-500">±{p.pos_tolerance}{p.unit}</span>
                </div>
                <div className="flex items-center justify-between text-[11px] text-slate-500 border-t border-slate-800/60 pt-2">
                  <span>{p.references.length} golden reference(s)</span>
                  <span className="text-cyan-400 font-medium">Ready</span>
                </div>
              </div>
            ))}

            {products.length === 0 && (
              <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 text-center space-y-2">
                <p className="text-xs text-slate-400">No manufactured products registered.</p>
                <button
                  onClick={() => onNavigate('products')}
                  className="px-3 py-1.5 bg-slate-800 hover:bg-slate-700 text-cyan-400 rounded-lg text-xs"
                >
                  Register Profile
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

```

---

## `frontend/src/pages/NewInspectionPage.tsx`

<a id="frontendsrcpagesnewinspectionpagetsx"></a>

```tsx
import React, { useState, useEffect, useRef } from 'react';
import { 
  Upload, 
  Scan, 
  Sliders, 
  AlertCircle, 
  Check, 
  Zap, 
  Ruler, 
  Eye, 
  FileCheck, 
  RefreshCw 
} from 'lucide-react';
import type { Product } from '../types';
import { fetchProducts, runInspection } from '../services/api';

interface NewInspectionPageProps {
  onInspectionComplete: (inspectionId: string) => void;
  onNavigateToProducts: () => void;
}

export const NewInspectionPage: React.FC<NewInspectionPageProps> = ({
  onInspectionComplete,
  onNavigateToProducts,
}) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<string>('');
  const [mode, setMode] = useState<string>('combined');

  // Image upload state
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState<boolean>(false);

  // Advanced metrology overrides
  const [showAdvanced, setShowAdvanced] = useState<boolean>(false);
  const [customCalib, setCustomCalib] = useState<string>('');
  const [customLength, setCustomLength] = useState<string>('');
  const [customWidth, setCustomWidth] = useState<string>('');
  const [customTol, setCustomTol] = useState<string>('');

  // Execution state
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    fetchProducts()
      .then((prods) => {
        setProducts(prods);
        if (prods.length > 0) {
          setSelectedProductId(prods[0].id);
        }
      })
      .catch((err) => console.error('Failed to load products:', err));
  }, []);

  const handleFileSelect = (file: File) => {
    if (!file.type.startsWith('image/')) {
      setErrorMsg('Please upload a valid image file (JPEG, PNG, WEBP, BMP).');
      return;
    }
    setErrorMsg(null);
    setSelectedFile(file);
    const url = URL.createObjectURL(file);
    setPreviewUrl(url);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFileSelect(e.dataTransfer.files[0]);
    }
  };

  // Helper to load sample test images directly from server
  const loadSampleImage = async (samplePath: string, sampleProductId?: string) => {
    try {
      setErrorMsg(null);
      const res = await fetch(samplePath);
      if (!res.ok) throw new Error('Sample image file not found on server');
      const blob = await res.blob();
      const filename = samplePath.split('/').pop() || 'sample.jpg';
      const file = new File([blob], filename, { type: 'image/jpeg' });
      handleFileSelect(file);
      if (sampleProductId) {
        setSelectedProductId(sampleProductId);
      }
    } catch (err: any) {
      setErrorMsg(`Failed to load sample: ${err.message}`);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedFile) {
      setErrorMsg('Please upload or select an inspection target image.');
      return;
    }

    setIsSubmitting(true);
    setErrorMsg(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      if (selectedProductId) {
        formData.append('product_id', selectedProductId);
      }
      formData.append('mode', mode);

      if (customCalib) formData.append('calibration_factor', customCalib);
      if (customLength) formData.append('custom_expected_length', customLength);
      if (customWidth) formData.append('custom_expected_width', customWidth);
      if (customTol) formData.append('custom_tolerance', customTol);

      const record = await runInspection(formData);
      onInspectionComplete(record.id);
    } catch (err: any) {
      setErrorMsg(err.message || 'Inspection execution failed. Please verify input parameters.');
      setIsSubmitting(false);
    }
  };

  const activeProduct = products.find((p) => p.id === selectedProductId);

  const modes = [
    {
      id: 'combined',
      title: 'Combined Quality Audit',
      desc: 'All-inclusive: Optical Metrology + Surface Flaw Detection + Reference Comparison',
      icon: Zap,
    },
    {
      id: 'dimensional',
      title: 'Dimensional Metrology',
      desc: 'Sub-pixel contour boundary calculation, rotated length/width, and tolerance delta',
      icon: Ruler,
    },
    {
      id: 'defect',
      title: 'Surface Defect Analysis',
      desc: 'ResNet18 patch features + morphological detection for cracks, scratches, and voids',
      icon: Eye,
    },
    {
      id: 'reference',
      title: 'Golden Reference Comparison',
      desc: 'Visual feature cosine distance against product approved baseline bank',
      icon: FileCheck,
    },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-16">
      {/* Page Header */}
      <div className="border-b border-slate-800 pb-5">
        <h1 className="text-2xl font-bold tracking-tight text-white font-mono flex items-center space-x-2">
          <Scan className="w-6 h-6 text-cyan-400" />
          <span>INITIALIZE QUALITY INSPECTION</span>
        </h1>
        <p className="text-sm text-slate-400 mt-1">
          Upload manufacturing component imagery for automated optical metrology and visual defect validation.
        </p>
      </div>

      {errorMsg && (
        <div className="bg-rose-950/50 border border-rose-800/80 rounded-xl p-4 flex items-start space-x-3 text-rose-300 text-sm">
          <AlertCircle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
          <div className="flex-1">
            <span className="font-semibold text-rose-200">Execution Error: </span>
            {errorMsg}
          </div>
        </div>
      )}

      {/* Quick Test Demo Samples Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-2.5">
        <div className="flex items-center justify-between">
          <span className="text-xs font-mono uppercase tracking-wider text-slate-400 flex items-center space-x-1.5">
            <Zap className="w-3.5 h-3.5 text-cyan-400" />
            <span>Quick Test Samples (Instant Simulation)</span>
          </span>
          <span className="text-[11px] text-slate-500">Click to prefill image & profile</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {(() => {
            const bracketId = products.find(p => p.name.toLowerCase().includes('bracket'))?.id;
            const pcbId = products.find(p => p.name.toLowerCase().includes('pcb'))?.id;
            const bushingId = products.find(p => p.name.toLowerCase().includes('bushing'))?.id;
            return (
              <>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/aerospace_bracket_pass.jpg', bracketId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-emerald-500/50 text-xs text-emerald-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  <span>Titanium Bracket [Pass Sample]</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/aerospace_bracket_scratch_defect.jpg', bracketId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-rose-500/50 text-xs text-rose-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span>Titanium Bracket [Scratch Defect]</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/aerospace_bracket_dimension_fail.jpg', bracketId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-rose-500/50 text-xs text-rose-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  <span>Titanium Bracket [Dimension Over-Tol]</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/smt_pcb_pass.jpg', pcbId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span>SMT PCB Assembly [Normal]</span>
                </button>
                <button
                  type="button"
                  onClick={() => loadSampleImage('/data/samples/polymer_bushing_pass.jpg', bushingId)}
                  className="px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 text-xs text-slate-300 flex items-center space-x-1.5 transition-colors"
                >
                  <span>Bearing Bushing [Normal]</span>
                </button>
              </>
            );
          })()}
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          {/* Left Column: Image Upload Area (7 columns) */}
          <div className="lg:col-span-7 space-y-4">
            <label className="block text-sm font-semibold text-white font-mono uppercase tracking-wider">
              1. Inspection Target Image
            </label>

            <div
              onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
              onDragLeave={() => setIsDragging(false)}
              onDrop={handleDrop}
              onClick={() => fileInputRef.current?.click()}
              className={`relative border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-all min-h-[320px] flex flex-col items-center justify-center ${
                isDragging
                  ? 'border-cyan-400 bg-cyan-950/20'
                  : previewUrl
                  ? 'border-slate-700 bg-slate-900/60'
                  : 'border-slate-700 hover:border-slate-600 bg-slate-900/40'
              }`}
            >
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(e) => {
                  if (e.target.files && e.target.files.length > 0) {
                    handleFileSelect(e.target.files[0]);
                  }
                }}
              />

              {previewUrl ? (
                <div className="space-y-4 w-full">
                  <div className="relative max-h-72 w-full overflow-hidden rounded-lg border border-slate-700 bg-black/40 flex items-center justify-center">
                    <img
                      src={previewUrl}
                      alt="Inspection target preview"
                      className="max-h-72 object-contain"
                    />
                    {isSubmitting && (
                      <div className="absolute inset-0 bg-slate-950/70 backdrop-blur-sm flex flex-col items-center justify-center space-y-3">
                        <div className="w-12 h-12 border-4 border-cyan-500 border-t-transparent rounded-full animate-spin" />
                        <span className="text-cyan-400 font-mono text-xs font-bold tracking-wider animate-pulse">
                          EXECUTING METROLOGY & ANOMALY SCAN...
                        </span>
                      </div>
                    )}
                  </div>
                  <div className="flex items-center justify-between text-xs text-slate-400 px-2 font-mono">
                    <span className="truncate max-w-[240px] text-white">{selectedFile?.name}</span>
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        fileInputRef.current?.click();
                      }}
                      className="text-cyan-400 hover:text-cyan-300"
                    >
                      Replace Image
                    </button>
                  </div>
                </div>
              ) : (
                <div className="space-y-3 text-slate-400">
                  <div className="w-14 h-14 rounded-full bg-slate-800 text-cyan-400 border border-slate-700 flex items-center justify-center mx-auto">
                    <Upload className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="text-sm font-medium text-white">Drag and drop inspection image here</p>
                    <p className="text-xs text-slate-500 mt-1">Supports high-res JPEG, PNG, WEBP, BMP</p>
                  </div>
                  <button
                    type="button"
                    className="px-4 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-white rounded-lg text-xs font-medium"
                  >
                    Browse Files
                  </button>
                </div>
              )}
            </div>
          </div>

          {/* Right Column: Profile & Parameters (5 columns) */}
          <div className="lg:col-span-5 space-y-6">
            {/* Product Profile Selection */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="block text-sm font-semibold text-white font-mono uppercase tracking-wider">
                  2. Product Specification
                </label>
                <button
                  type="button"
                  onClick={onNavigateToProducts}
                  className="text-xs text-cyan-400 hover:text-cyan-300"
                >
                  + Add Product
                </button>
              </div>

              <select
                value={selectedProductId}
                onChange={(e) => setSelectedProductId(e.target.value)}
                className="w-full px-3.5 py-2.5 bg-slate-900 border border-slate-700 focus:border-cyan-500 rounded-lg text-sm text-white focus:outline-none"
              >
                <option value="">-- Generic Unregistered Specimen --</option>
                {products.map((p) => (
                  <option key={p.id} value={p.id}>
                    {p.name} ({p.category})
                  </option>
                ))}
              </select>

              {activeProduct && (
                <div className="bg-slate-900/80 border border-slate-800 rounded-lg p-3 text-xs space-y-1.5 text-slate-300">
                  <div className="flex justify-between">
                    <span className="text-slate-500">Design Size:</span>
                    <span className="font-mono font-medium text-white">
                      {activeProduct.expected_length} × {activeProduct.expected_width} {activeProduct.unit}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Tolerances:</span>
                    <span className="font-mono text-emerald-400">
                      -{activeProduct.neg_tolerance} / +{activeProduct.pos_tolerance} {activeProduct.unit}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-500">Golden Reference:</span>
                    <span className="font-mono text-cyan-400">
                      {activeProduct.references.length} indexed sample(s)
                    </span>
                  </div>
                </div>
              )}
            </div>

            {/* Mode Selection */}
            <div className="space-y-2">
              <label className="block text-sm font-semibold text-white font-mono uppercase tracking-wider">
                3. Inspection Mode
              </label>

              <div className="space-y-2">
                {modes.map((m) => {
                  const Icon = m.icon;
                  const isSelected = mode === m.id;
                  return (
                    <div
                      key={m.id}
                      onClick={() => setMode(m.id)}
                      className={`p-3 rounded-xl border cursor-pointer transition-all flex items-start space-x-3 ${
                        isSelected
                          ? 'border-cyan-500 bg-cyan-950/20 text-white shadow-sm shadow-cyan-950'
                          : 'border-slate-800 bg-slate-900/60 text-slate-300 hover:border-slate-700'
                      }`}
                    >
                      <div className={`p-2 rounded-lg mt-0.5 ${
                        isSelected ? 'bg-cyan-500 text-slate-950' : 'bg-slate-800 text-slate-400'
                      }`}>
                        <Icon className="w-4 h-4" />
                      </div>
                      <div className="flex-1">
                        <div className="flex items-center justify-between">
                          <span className="text-xs font-bold font-mono uppercase tracking-wider">
                            {m.title}
                          </span>
                          {isSelected && <Check className="w-3.5 h-3.5 text-cyan-400" />}
                        </div>
                        <p className="text-[11px] text-slate-400 mt-0.5">{m.desc}</p>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Advanced Overrides Toggle */}
            <div className="pt-2 border-t border-slate-800">
              <button
                type="button"
                onClick={() => setShowAdvanced(!showAdvanced)}
                className="flex items-center space-x-2 text-xs font-mono text-slate-400 hover:text-cyan-400"
              >
                <Sliders className="w-3.5 h-3.5" />
                <span>{showAdvanced ? 'Hide Advanced Metrology Overrides' : 'Advanced Metrology Overrides'}</span>
              </button>

              {showAdvanced && (
                <div className="mt-3 bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3 text-xs">
                  <div>
                    <label className="block text-slate-400 mb-1">
                      Scale Calibration Factor (pixels per unit):
                    </label>
                    <input
                      type="number"
                      step="0.1"
                      placeholder={activeProduct ? String(activeProduct.calibration_factor) : '10.0'}
                      value={customCalib}
                      onChange={(e) => setCustomCalib(e.target.value)}
                      className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-white"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-2">
                    <div>
                      <label className="block text-slate-400 mb-1">Override Length:</label>
                      <input
                        type="number"
                        step="0.1"
                        placeholder="e.g. 100.0"
                        value={customLength}
                        onChange={(e) => setCustomLength(e.target.value)}
                        className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-white"
                      />
                    </div>
                    <div>
                      <label className="block text-slate-400 mb-1">Override Width:</label>
                      <input
                        type="number"
                        step="0.1"
                        placeholder="e.g. 50.0"
                        value={customWidth}
                        onChange={(e) => setCustomWidth(e.target.value)}
                        className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-white"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-slate-400 mb-1">Tolerance Margin (±):</label>
                    <input
                      type="number"
                      step="0.1"
                      placeholder="e.g. 2.0"
                      value={customTol}
                      onChange={(e) => setCustomTol(e.target.value)}
                      className="w-full px-3 py-1.5 bg-slate-950 border border-slate-700 rounded text-white"
                    />
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Submit Action */}
        <div className="border-t border-slate-800 pt-6 flex items-center justify-end space-x-4">
          <button
            type="submit"
            disabled={isSubmitting || !selectedFile}
            className={`flex items-center space-x-2 px-8 py-3.5 rounded-xl font-bold text-sm tracking-wide font-mono uppercase transition-all shadow-lg ${
              isSubmitting || !selectedFile
                ? 'bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700'
                : 'bg-cyan-500 hover:bg-cyan-400 text-slate-950 shadow-cyan-500/20 hover:shadow-cyan-500/30'
            }`}
          >
            {isSubmitting ? (
              <>
                <RefreshCw className="w-4 h-4 animate-spin text-slate-950" />
                <span>INSPECTING SPECIMEN...</span>
              </>
            ) : (
              <>
                <Scan className="w-4 h-4" />
                <span>EXECUTE QUALITY AUDIT</span>
              </>
            )}
          </button>
        </div>
      </form>
    </div>
  );
};

```

---

## `frontend/src/pages/InspectionResultsPage.tsx`

<a id="frontendsrcpagesinspectionresultspagetsx"></a>

```tsx
import React, { useEffect, useState } from 'react';
import { 
  Download, 
  ArrowLeft, 
  RefreshCw, 
  AlertTriangle, 
  Ruler, 
  Eye, 
  FileText, 
  Info 
} from 'lucide-react';
import type { InspectionRecord } from '../types';
import { fetchInspection, getImageUrl, getPdfReportUrl, getJsonReportUrl } from '../services/api';
import { StatusBadge, ModeBadge } from '../components/StatusBadge';

interface InspectionResultsPageProps {
  inspectionId: string;
  onBack: () => void;
  onInspectAgain: () => void;
}

export const InspectionResultsPage: React.FC<InspectionResultsPageProps> = ({
  inspectionId,
  onBack,
  onInspectAgain
}) => {
  const [record, setRecord] = useState<InspectionRecord | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [activeImageView, setActiveImageView] = useState<'annotated' | 'heatmap' | 'original' | 'reference'>('annotated');

  useEffect(() => {
    setLoading(true);
    fetchInspection(inspectionId)
      .then((data) => {
        setRecord(data);
        if (data.annotated_image_path) {
          setActiveImageView('annotated');
        } else if (data.heatmap_image_path) {
          setActiveImageView('heatmap');
        } else {
          setActiveImageView('original');
        }
      })
      .catch((err) => setError(err.message || 'Failed to load inspection record'))
      .finally(() => setLoading(false));
  }, [inspectionId]);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-slate-400 font-mono text-sm">Decoding inspection telemetry and visual overlays...</p>
      </div>
    );
  }

  if (error || !record) {
    return (
      <div className="p-8 max-w-3xl mx-auto text-center space-y-4">
        <div className="bg-rose-950/40 border border-rose-800 rounded-xl p-6">
          <AlertTriangle className="w-10 h-10 text-rose-400 mx-auto mb-2" />
          <h2 className="text-lg font-bold text-white">Record Not Found</h2>
          <p className="text-sm text-slate-300 mt-1">{error || 'Inspection ID invalid'}</p>
          <button
            onClick={onBack}
            className="mt-4 px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  let currentImageUrl = '';
  if (activeImageView === 'annotated' && record.annotated_image_path) {
    currentImageUrl = getImageUrl(record.annotated_image_path);
  } else if (activeImageView === 'heatmap' && record.heatmap_image_path) {
    currentImageUrl = getImageUrl(record.heatmap_image_path);
  } else if (activeImageView === 'reference' && record.reference_image_path) {
    currentImageUrl = getImageUrl(record.reference_image_path);
  } else {
    currentImageUrl = getImageUrl(record.inspection_image_path);
  }

  return (
    <div className="space-y-8 pb-16">
      {/* Top Navigation & Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div className="flex items-center space-x-3">
          <button
            onClick={onBack}
            className="p-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 rounded-lg text-slate-300 hover:text-white transition-colors"
            title="Go Back"
          >
            <ArrowLeft className="w-4 h-4" />
          </button>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xl font-bold font-mono text-white">
                AUDIT REPORT // <span className="text-cyan-400">{record.id.substring(0, 8)}</span>
              </span>
              <ModeBadge mode={record.mode} />
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Specimen: <span className="text-white font-medium">{record.product_name || 'Generic Sample'}</span> • Logged on {new Date(record.created_at).toLocaleString()}
            </p>
          </div>
        </div>

        {/* Export and Action buttons */}
        <div className="flex items-center space-x-2.5">
          <a
            href={getPdfReportUrl(record.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-3.5 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-600 text-slate-200 hover:text-white rounded-lg text-xs font-medium transition-colors"
          >
            <Download className="w-3.5 h-3.5 text-cyan-400" />
            <span>Download PDF</span>
          </a>
          <a
            href={getJsonReportUrl(record.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center space-x-1.5 px-3 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-400 hover:text-white rounded-lg text-xs font-mono transition-colors"
          >
            <FileText className="w-3.5 h-3.5" />
            <span>JSON</span>
          </a>
          <button
            onClick={onInspectAgain}
            className="px-4 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-xs transition-colors shadow-sm shadow-cyan-500/20"
          >
            Inspect Another
          </button>
        </div>
      </div>

      {/* Decision Outcome Banner */}
      <div className={`p-5 rounded-xl border flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
        record.overall_status === 'PASS'
          ? 'bg-emerald-950/40 border-emerald-800/60 text-emerald-200'
          : record.overall_status === 'FAIL'
          ? 'bg-rose-950/40 border-rose-800/60 text-rose-200'
          : 'bg-amber-950/40 border-amber-800/60 text-amber-200'
      }`}>
        <div className="flex items-start space-x-3.5">
          <div className="mt-0.5">
            <StatusBadge status={record.overall_status} size="lg" />
          </div>
          <div>
            <h2 className="text-sm font-bold tracking-wide uppercase font-mono">
              Final System Verification
            </h2>
            <p className="text-xs text-slate-300 mt-1 max-w-3xl leading-relaxed">
              {record.overall_explanation}
            </p>
          </div>
        </div>

        <div className="font-mono text-right text-xs shrink-0 self-end sm:self-center border-t sm:border-t-0 sm:border-l border-slate-800/80 pt-2 sm:pt-0 sm:pl-4">
          <div className="text-slate-400">Tolerance Criteria:</div>
          <div className="font-semibold text-white">Strict Deterministic QC</div>
        </div>
      </div>

      {/* Main Inspection Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Viewer */}
        <div className="lg:col-span-7 space-y-4">
          <div className="flex items-center justify-between bg-slate-900 p-1.5 rounded-xl border border-slate-800">
            <div className="flex items-center space-x-1 text-xs">
              {record.annotated_image_path && (
                <button
                  onClick={() => setActiveImageView('annotated')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                    activeImageView === 'annotated'
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Metrology HUD
                </button>
              )}
              {record.heatmap_image_path && (
                <button
                  onClick={() => setActiveImageView('heatmap')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                    activeImageView === 'heatmap'
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Defect Heatmap
                </button>
              )}
              <button
                onClick={() => setActiveImageView('original')}
                className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                  activeImageView === 'original'
                    ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Raw Specimen
              </button>
              {record.reference_image_path && (
                <button
                  onClick={() => setActiveImageView('reference')}
                  className={`px-3 py-1.5 rounded-lg font-medium transition-colors ${
                    activeImageView === 'reference'
                      ? 'bg-cyan-500/10 text-cyan-400 border border-cyan-500/30'
                      : 'text-slate-400 hover:text-white'
                  }`}
                >
                  Golden Reference
                </button>
              )}
            </div>

            <span className="text-[10px] font-mono text-slate-500 uppercase px-2">
              Layer: {activeImageView}
            </span>
          </div>

          <div className="relative bg-slate-950 border border-slate-800 rounded-xl overflow-hidden min-h-[420px] flex items-center justify-center p-2 group">
            {currentImageUrl ? (
              <img
                src={currentImageUrl}
                alt={`Inspection layer ${activeImageView}`}
                className="max-h-[520px] w-auto object-contain rounded-lg shadow-2xl transition-all"
              />
            ) : (
              <div className="text-slate-500 text-xs font-mono">No imagery layer available</div>
            )}

            <div className="absolute bottom-4 left-4 px-3 py-1 rounded bg-slate-950/80 backdrop-blur-md border border-slate-800 text-[11px] font-mono text-slate-300">
              {activeImageView === 'annotated' && 'Optical Metrology: MinAreaRect & Dimensional Deviations'}
              {activeImageView === 'heatmap' && 'Anomaly Heatmap: ResNet18 Layer4 Patch Distance Overlay'}
              {activeImageView === 'original' && 'Raw Specimen: Native Optical Sensor Frame'}
              {activeImageView === 'reference' && 'Approved Golden Reference Specimen'}
            </div>
          </div>
        </div>

        {/* Right Column: Quantitative Metrology */}
        <div className="lg:col-span-5 space-y-6">
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <Ruler className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                  Optical Metrology Results
                </h3>
              </div>
              {record.dimensional_status && (
                <StatusBadge status={record.dimensional_status} size="sm" />
              )}
            </div>

            {record.measured_length !== null && record.measured_length !== undefined ? (
              <div className="space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                    <span className="text-[10px] font-mono text-slate-400 uppercase">Length Axis</span>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">
                      {record.measured_length.toFixed(2)} <span className="text-xs text-slate-400 font-normal">{record.unit}</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] mt-1.5 pt-1.5 border-t border-slate-800">
                      <span className="text-slate-500">Exp: {record.expected_length ?? '—'}</span>
                      <span className={`font-mono font-medium ${
                        record.length_deviation && Math.abs(record.length_deviation) > 2.0 ? 'text-rose-400' : 'text-emerald-400'
                      }`}>
                        Δ {record.length_deviation ? (record.length_deviation > 0 ? `+${record.length_deviation}` : record.length_deviation) : '0.00'}
                      </span>
                    </div>
                  </div>

                  <div className="bg-slate-950 p-3 rounded-lg border border-slate-800/80">
                    <span className="text-[10px] font-mono text-slate-400 uppercase">Width Axis</span>
                    <div className="text-lg font-bold text-white font-mono mt-0.5">
                      {record.measured_width?.toFixed(2) ?? '—'} <span className="text-xs text-slate-400 font-normal">{record.unit}</span>
                    </div>
                    <div className="flex items-center justify-between text-[11px] mt-1.5 pt-1.5 border-t border-slate-800">
                      <span className="text-slate-500">Exp: {record.expected_width ?? '—'}</span>
                      <span className={`font-mono font-medium ${
                        record.width_deviation && Math.abs(record.width_deviation) > 2.0 ? 'text-rose-400' : 'text-emerald-400'
                      }`}>
                        Δ {record.width_deviation ? (record.width_deviation > 0 ? `+${record.width_deviation}` : record.width_deviation) : '0.00'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="text-[11px] text-slate-400 font-mono bg-slate-950/60 p-2 rounded border border-slate-800/50">
                  Formula: Deviation = Measured ({record.unit}) − Expected ({record.unit})
                </div>
              </div>
            ) : (
              <p className="text-xs text-slate-500 italic">
                Dimensional measurement was not enabled or no contour could be isolated.
              </p>
            )}
          </div>

          {/* Anomaly & Surface Defect Summary */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <div className="flex items-center space-x-2">
                <Eye className="w-4 h-4 text-cyan-400" />
                <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider">
                  Anomaly & Defect Analysis
                </h3>
              </div>
              {record.anomaly_status && (
                <StatusBadge status={record.anomaly_status} size="sm" />
              )}
            </div>

            {record.anomaly_score !== null && record.anomaly_score !== undefined && (
              <div className="space-y-2">
                <div className="flex justify-between items-center text-xs">
                  <span className="text-slate-400 font-mono">Visual Anomaly Score</span>
                  <span className="font-mono font-bold text-white">
                    {record.anomaly_score.toFixed(3)}
                    <span className="text-slate-500 font-normal"> / Thresh: {record.anomaly_threshold?.toFixed(2) || '0.32'}</span>
                  </span>
                </div>
                <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden p-0.5 border border-slate-800">
                  <div
                    className={`h-full rounded-full transition-all ${
                      record.anomaly_score >= (record.anomaly_threshold || 0.32)
                        ? 'bg-rose-500'
                        : 'bg-emerald-500'
                    }`}
                    style={{ width: `${Math.min(100, record.anomaly_score * 100)}%` }}
                  />
                </div>
              </div>
            )}

            {record.reference_similarity_score !== null && record.reference_similarity_score !== undefined && (
              <div className="flex justify-between items-center text-xs pt-1 border-t border-slate-800/60">
                <span className="text-slate-400 font-mono">Golden Reference Similarity:</span>
                <span className="font-mono text-cyan-400 font-semibold">
                  {(record.reference_similarity_score * 100).toFixed(1)}% match
                </span>
              </div>
            )}

            <div className="space-y-2 pt-2">
              <span className="text-[11px] font-mono text-slate-400 uppercase">
                Detected Defect Entities ({record.detected_defects.length})
              </span>
              {record.detected_defects.length > 0 ? (
                <div className="space-y-2 max-h-48 overflow-y-auto pr-1">
                  {record.detected_defects.map((def) => (
                    <div
                      key={def.id}
                      className="bg-slate-950 border border-slate-800/80 p-2.5 rounded-lg text-xs space-y-1"
                    >
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-rose-300 font-mono uppercase">{def.type}</span>
                        <span className={`text-[10px] uppercase font-mono px-1.5 py-0.5 rounded ${
                          def.severity === 'high' ? 'bg-rose-950 text-rose-400 border border-rose-800' : 'bg-amber-950 text-amber-300'
                        }`}>
                          {def.severity} severity
                        </span>
                      </div>
                      <p className="text-[11px] text-slate-400">{def.description}</p>
                      <div className="text-[10px] font-mono text-slate-500">
                        Confidence: {(def.confidence * 100).toFixed(0)}%
                        {def.location && ` • Box: (${def.location.x}, ${def.location.y})`}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800 text-center text-xs text-emerald-400 font-mono">
                  ✓ Zero surface fractures, scratches, or voids identified.
                </div>
              )}
            </div>
          </div>

          {/* Checkpoints Breakdown */}
          <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-3">
            <h3 className="text-xs font-bold text-white font-mono uppercase tracking-wider border-b border-slate-800 pb-2">
              Inspection Checkpoints Breakdown
            </h3>
            <div className="space-y-2 text-xs">
              {record.checks_executed.map((c, i) => (
                <div key={i} className="flex items-start justify-between p-2 rounded bg-slate-950/60 border border-slate-800/60">
                  <div className="space-y-0.5 max-w-[260px]">
                    <div className="font-semibold text-white">{c.check_name}</div>
                    <div className="text-[11px] text-slate-400">{c.explanation}</div>
                  </div>
                  <StatusBadge status={c.status} size="sm" />
                </div>
              ))}
            </div>
          </div>

          {/* Disclaimers */}
          {record.limitations && record.limitations.length > 0 && (
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-4 space-y-2 text-xs">
              <div className="flex items-center space-x-1.5 text-slate-400 font-mono">
                <Info className="w-3.5 h-3.5 text-cyan-400" />
                <span className="uppercase text-[11px] font-bold">Optical Limitations & Disclaimers</span>
              </div>
              <ul className="space-y-1 text-[11px] text-slate-500 list-disc list-inside">
                {record.limitations.map((lim, idx) => (
                  <li key={idx}>{lim}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

```

---

## `frontend/src/pages/ProductRegistrationPage.tsx`

<a id="frontendsrcpagesproductregistrationpagetsx"></a>

```tsx
import React, { useState, useEffect, useRef } from 'react';
import { 
  Layers, 
  Plus, 
  Trash2, 
  Edit3, 
  Check, 
  AlertCircle, 
  Scan, 
  X 
} from 'lucide-react';
import type { Product } from '../types';
import { 
  fetchProducts, 
  createProduct, 
  updateProduct, 
  deleteProduct, 
  uploadReferenceImage, 
  deleteReferenceImage,
  getImageUrl 
} from '../services/api';

interface ProductRegistrationPageProps {
  onStartInspection: (productId: string) => void;
}

export const ProductRegistrationPage: React.FC<ProductRegistrationPageProps> = ({
  onStartInspection
}) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  // Modal / Form state
  const [showModal, setShowModal] = useState<boolean>(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);

  // Form inputs
  const [name, setName] = useState<string>('');
  const [category, setCategory] = useState<string>('Aerospace');
  const [customCategory, setCustomCategory] = useState<string>('');
  const [description, setDescription] = useState<string>('');
  const [expectedLength, setExpectedLength] = useState<string>('100.0');
  const [expectedWidth, setExpectedWidth] = useState<string>('50.0');
  const [expectedThickness, setExpectedThickness] = useState<string>('');
  const [unit, setUnit] = useState<string>('mm');
  const [posTol, setPosTol] = useState<string>('2.0');
  const [negTol, setNegTol] = useState<string>('2.0');
  const [calibFactor, setCalibFactor] = useState<string>('10.0');

  // Reference Upload state for active product
  const [uploadingForProductId, setUploadingForProductId] = useState<string | null>(null);
  const refFileInputRef = useRef<HTMLInputElement>(null);

  const loadProducts = async () => {
    setLoading(true);
    try {
      const data = await fetchProducts();
      setProducts(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load products');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProducts();
  }, []);

  const openCreateModal = () => {
    setEditingProduct(null);
    setName('');
    setCategory('Aerospace');
    setCustomCategory('');
    setDescription('');
    setExpectedLength('100.0');
    setExpectedWidth('50.0');
    setExpectedThickness('');
    setUnit('mm');
    setPosTol('2.0');
    setNegTol('2.0');
    setCalibFactor('10.0');
    setShowModal(true);
  };

  const openEditModal = (p: Product) => {
    setEditingProduct(p);
    setName(p.name);
    setCategory(p.category);
    setDescription(p.description || '');
    setExpectedLength(String(p.expected_length));
    setExpectedWidth(String(p.expected_width));
    setExpectedThickness(p.expected_thickness ? String(p.expected_thickness) : '');
    setUnit(p.unit);
    setPosTol(String(p.pos_tolerance));
    setNegTol(String(p.neg_tolerance));
    setCalibFactor(String(p.calibration_factor));
    setShowModal(true);
  };

  const handleSaveProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    const targetCategory = category === 'Custom' ? customCategory.trim() : category;
    if (!name.trim() || !targetCategory) {
      setError('Product name and category are required.');
      return;
    }

    try {
      const payload = {
        name: name.trim(),
        category: targetCategory,
        description: description.trim() || undefined,
        expected_length: parseFloat(expectedLength) || 100.0,
        expected_width: parseFloat(expectedWidth) || 50.0,
        expected_thickness: expectedThickness ? parseFloat(expectedThickness) : undefined,
        unit,
        pos_tolerance: parseFloat(posTol) || 2.0,
        neg_tolerance: parseFloat(negTol) || 2.0,
        calibration_factor: parseFloat(calibFactor) || 10.0,
      };

      if (editingProduct) {
        await updateProduct(editingProduct.id, payload);
        setSuccessMsg(`Product "${name}" updated successfully.`);
      } else {
        await createProduct(payload);
        setSuccessMsg(`New product "${name}" registered successfully.`);
      }

      setShowModal(false);
      await loadProducts();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setError(err.message || 'Failed to save product specification.');
    }
  };

  const handleDeleteProduct = async (productId: string, productName: string) => {
    if (!window.confirm(`Are you sure you want to delete product "${productName}" and its reference banks?`)) {
      return;
    }
    try {
      await deleteProduct(productId);
      setSuccessMsg(`Product "${productName}" deleted.`);
      await loadProducts();
      setTimeout(() => setSuccessMsg(null), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to delete product.');
    }
  };

  const handleTriggerRefUpload = (productId: string) => {
    setUploadingForProductId(productId);
    refFileInputRef.current?.click();
  };

  const handleRefFileSelected = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !uploadingForProductId) return;
    const file = e.target.files[0];
    try {
      await uploadReferenceImage(uploadingForProductId, file);
      setSuccessMsg(`Uploaded golden reference "${file.name}". Embedding bank updated.`);
      await loadProducts();
      setTimeout(() => setSuccessMsg(null), 4000);
    } catch (err: any) {
      setError(err.message || 'Failed to upload reference image');
    } finally {
      setUploadingForProductId(null);
      if (refFileInputRef.current) refFileInputRef.current.value = '';
    }
  };

  const handleDeleteRef = async (productId: string, refId: string) => {
    if (!window.confirm('Delete this reference image and update feature bank?')) return;
    try {
      await deleteReferenceImage(productId, refId);
      await loadProducts();
    } catch (err: any) {
      setError(err.message || 'Failed to delete reference');
    }
  };

  const standardCategories = ['Aerospace', 'Electronics', 'Mechanical', 'Metal', 'Plastic', 'Textile', 'Custom'];

  return (
    <div className="space-y-8 pb-16">
      <input
        ref={refFileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleRefFileSelected}
      />

      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-mono flex items-center space-x-2">
            <Layers className="w-6 h-6 text-cyan-400" />
            <span>PRODUCT REGISTRATION & REFERENCE BANKS</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Register new manufactured components, establish expected dimensions and tolerances, and upload golden reference baselines.
          </p>
        </div>
        <button
          onClick={openCreateModal}
          className="flex items-center space-x-2 px-4 py-2.5 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-sm transition-all shadow-lg shadow-cyan-500/20 self-start md:self-auto"
        >
          <Plus className="w-4 h-4" />
          <span>Register New Product</span>
        </button>
      </div>

      {successMsg && (
        <div className="bg-emerald-950/40 border border-emerald-800/80 rounded-xl p-3.5 flex items-center space-x-2 text-emerald-300 text-xs">
          <Check className="w-4 h-4 text-emerald-400 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}
      {error && (
        <div className="bg-rose-950/40 border border-rose-800/80 rounded-xl p-3.5 flex items-center space-x-2 text-rose-300 text-xs">
          <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((p) => (
          <div
            key={p.id}
            className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 flex flex-col justify-between hover:border-slate-700 transition-all space-y-4 shadow-sm"
          >
            <div>
              <div className="flex items-start justify-between gap-2">
                <div>
                  <h3 className="font-bold text-white text-base leading-snug">{p.name}</h3>
                  <span className="inline-block mt-1 text-[10px] font-mono uppercase px-2 py-0.5 rounded bg-slate-800 text-cyan-300 border border-slate-700">
                    {p.category}
                  </span>
                </div>
                <div className="flex items-center space-x-1 shrink-0">
                  <button
                    onClick={() => openEditModal(p)}
                    className="p-1.5 text-slate-400 hover:text-white rounded hover:bg-slate-800"
                    title="Edit Specification"
                  >
                    <Edit3 className="w-3.5 h-3.5" />
                  </button>
                  <button
                    onClick={() => handleDeleteProduct(p.id, p.name)}
                    className="p-1.5 text-slate-400 hover:text-rose-400 rounded hover:bg-slate-800"
                    title="Delete Product"
                  >
                    <Trash2 className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>

              {p.description && (
                <p className="text-xs text-slate-400 mt-2 line-clamp-2 leading-relaxed">
                  {p.description}
                </p>
              )}

              <div className="mt-4 bg-slate-950/80 rounded-lg p-3 border border-slate-800/80 space-y-2 text-xs">
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 font-mono">Expected Length:</span>
                  <span className="font-mono font-semibold text-white">{p.expected_length} {p.unit}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 font-mono">Expected Width:</span>
                  <span className="font-mono font-semibold text-white">{p.expected_width} {p.unit}</span>
                </div>
                <div className="flex justify-between items-center">
                  <span className="text-slate-400 font-mono">Permitted Tolerance:</span>
                  <span className="font-mono text-emerald-400">-{p.neg_tolerance} / +{p.pos_tolerance} {p.unit}</span>
                </div>
                <div className="flex justify-between items-center pt-1 border-t border-slate-800">
                  <span className="text-slate-500 font-mono">Scale Factor:</span>
                  <span className="font-mono text-slate-300">{p.calibration_factor} px/{p.unit}</span>
                </div>
              </div>

              <div className="mt-4 space-y-2">
                <div className="flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-400">Golden Reference Samples ({p.references.length})</span>
                  <button
                    onClick={() => handleTriggerRefUpload(p.id)}
                    className="text-cyan-400 hover:text-cyan-300 flex items-center space-x-1"
                  >
                    <Plus className="w-3 h-3" />
                    <span>Add Ref</span>
                  </button>
                </div>

                {p.references.length > 0 ? (
                  <div className="grid grid-cols-4 gap-2">
                    {p.references.map((r) => (
                      <div key={r.id} className="relative group rounded border border-slate-800 overflow-hidden bg-black/40 h-16">
                        <img
                          src={getImageUrl(r.file_path)}
                          alt={r.filename}
                          className="w-full h-full object-cover"
                        />
                        <button
                          onClick={() => handleDeleteRef(p.id, r.id)}
                          className="absolute inset-0 bg-black/70 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity text-rose-400"
                          title="Remove reference"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-3 border border-dashed border-slate-800 rounded text-slate-500 text-[11px]">
                    No golden reference images uploaded.
                  </div>
                )}
              </div>
            </div>

            <button
              onClick={() => onStartInspection(p.id)}
              className="w-full mt-2 py-2 bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-cyan-500/50 text-cyan-400 hover:text-white rounded-lg text-xs font-mono font-semibold flex items-center justify-center space-x-2 transition-colors"
            >
              <Scan className="w-3.5 h-3.5" />
              <span>Inspect Specimen For This Profile</span>
            </button>
          </div>
        ))}
      </div>

      {products.length === 0 && !loading && (
        <div className="bg-slate-900 border border-slate-800 rounded-xl p-12 text-center space-y-3 max-w-lg mx-auto">
          <Layers className="w-10 h-10 text-slate-600 mx-auto" />
          <h3 className="text-base font-bold text-white">No Registered Products Found</h3>
          <p className="text-xs text-slate-400">
            Define target product dimensions, measurement tolerances, and reference samples to begin automated verification.
          </p>
          <button
            onClick={openCreateModal}
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-medium"
          >
            Register First Product
          </button>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-sm flex items-center justify-center p-4 overflow-y-auto">
          <div className="bg-slate-900 border border-slate-800 rounded-xl max-w-xl w-full p-6 space-y-6 shadow-2xl">
            <div className="flex items-center justify-between border-b border-slate-800 pb-3">
              <h2 className="text-lg font-bold text-white font-mono flex items-center space-x-2">
                <Layers className="w-5 h-5 text-cyan-400" />
                <span>{editingProduct ? 'EDIT PRODUCT PROFILE' : 'REGISTER NEW PRODUCT'}</span>
              </h2>
              <button
                onClick={() => setShowModal(false)}
                className="text-slate-400 hover:text-white p-1 rounded"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSaveProduct} className="space-y-4">
              <div>
                <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                  Product Name *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g. Precision Titanium Bracket M4"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Category *
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                  >
                    {standardCategories.map((c) => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Measurement Unit
                  </label>
                  <select
                    value={unit}
                    onChange={(e) => setUnit(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                  >
                    <option value="mm">Millimeters (mm)</option>
                    <option value="cm">Centimeters (cm)</option>
                    <option value="in">Inches (in)</option>
                  </select>
                </div>
              </div>

              {category === 'Custom' && (
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Custom Category Name *
                  </label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Automotive Hydraulics"
                    value={customCategory}
                    onChange={(e) => setCustomCategory(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white"
                  />
                </div>
              )}

              <div>
                <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                  Description / Component Notes
                </label>
                <textarea
                  rows={2}
                  placeholder="Engine mount component specs, critical surfaces..."
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white focus:outline-none focus:border-cyan-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Expected Length ({unit}) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={expectedLength}
                    onChange={(e) => setExpectedLength(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Expected Width ({unit}) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={expectedWidth}
                    onChange={(e) => setExpectedWidth(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Positive Tolerance (+{unit}) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={posTol}
                    onChange={(e) => setPosTol(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                  />
                </div>
                <div>
                  <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                    Negative Tolerance (-{unit}) *
                  </label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    value={negTol}
                    onChange={(e) => setNegTol(e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-mono uppercase text-slate-300 mb-1">
                  Optical Calibration Factor (pixels/{unit}) *
                </label>
                <input
                  type="number"
                  step="0.1"
                  required
                  value={calibFactor}
                  onChange={(e) => setCalibFactor(e.target.value)}
                  className="w-full px-3.5 py-2 bg-slate-950 border border-slate-700 rounded-lg text-sm text-white font-mono"
                />
                <p className="text-[11px] text-slate-500 mt-1">
                  Calculated from camera distance and optics (e.g. 5.0 px/mm means 500 pixels = 100mm).
                </p>
              </div>

              <div className="flex justify-end space-x-3 pt-4 border-t border-slate-800">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-slate-300 rounded-lg text-xs"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-5 py-2 bg-cyan-500 hover:bg-cyan-400 text-slate-950 font-bold rounded-lg text-xs font-mono uppercase"
                >
                  {editingProduct ? 'Update Specification' : 'Register Specification'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

```

---

## `frontend/src/pages/InspectionHistoryPage.tsx`

<a id="frontendsrcpagesinspectionhistorypagetsx"></a>

```tsx
import React, { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  Download, 
  Eye, 
  RefreshCw, 
  FileText 
} from 'lucide-react';
import type { InspectionRecord, Product } from '../types';
import { fetchInspections, fetchProducts, getPdfReportUrl, getJsonReportUrl } from '../services/api';
import { StatusBadge, ModeBadge } from '../components/StatusBadge';

interface InspectionHistoryPageProps {
  onSelectInspection: (inspectionId: string) => void;
}

export const InspectionHistoryPage: React.FC<InspectionHistoryPageProps> = ({
  onSelectInspection
}) => {
  const [inspections, setInspections] = useState<InspectionRecord[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  // Filters
  const [searchTerm, setSearchTerm] = useState<string>('');
  const [statusFilter, setStatusFilter] = useState<string>('');
  const [modeFilter, setModeFilter] = useState<string>('');
  const [productFilter, setProductFilter] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    try {
      const [inspData, prodsData] = await Promise.all([
        fetchInspections({
          search: searchTerm || undefined,
          status: statusFilter || undefined,
          mode: modeFilter || undefined,
          productId: productFilter || undefined,
          limit: 100,
        }),
        fetchProducts()
      ]);
      setInspections(inspData);
      setProducts(prodsData);
    } catch (err: any) {
      console.error('Failed to load inspection history:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [statusFilter, modeFilter, productFilter]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    loadData();
  };

  return (
    <div className="space-y-6 pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-mono flex items-center space-x-2">
            <History className="w-6 h-6 text-cyan-400" />
            <span>INSPECTION AUDIT LOGS</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Historical quality assurance records, measurement deviations, anomaly telemetry, and certified reports.
          </p>
        </div>
        <button
          onClick={loadData}
          className="flex items-center space-x-2 px-3.5 py-2 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg text-xs font-mono self-start sm:self-auto transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Refresh Records</span>
        </button>
      </div>

      {/* Filter and Search Bar */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-4 space-y-3">
        <form onSubmit={handleSearchSubmit} className="flex flex-col md:flex-row gap-3">
          <div className="relative flex-1">
            <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-3" />
            <input
              type="text"
              placeholder="Search by Inspection ID or defect details..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500"
            />
          </div>

          <select
            value={productFilter}
            onChange={(e) => setProductFilter(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Products</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>

          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Statuses</option>
            <option value="PASS">PASS</option>
            <option value="REVIEW">REVIEW</option>
            <option value="FAIL">FAIL</option>
          </select>

          <select
            value={modeFilter}
            onChange={(e) => setModeFilter(e.target.value)}
            className="px-3 py-2 bg-slate-950 border border-slate-700 rounded-lg text-xs text-white focus:outline-none focus:border-cyan-500"
          >
            <option value="">All Modes</option>
            <option value="combined">Combined</option>
            <option value="dimensional">Dimensional</option>
            <option value="defect">Defect</option>
            <option value="reference">Reference</option>
          </select>

          <button
            type="submit"
            className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded-lg text-xs font-mono font-semibold transition-colors"
          >
            Apply Filters
          </button>
        </form>
      </div>

      {/* Table */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl overflow-hidden shadow-sm">
        {loading ? (
          <div className="py-16 text-center space-y-3">
            <RefreshCw className="w-6 h-6 text-cyan-400 animate-spin mx-auto" />
            <p className="text-xs text-slate-400 font-mono">Querying audit logs...</p>
          </div>
        ) : inspections.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-slate-950 text-slate-400 border-b border-slate-800 font-mono">
                <tr>
                  <th className="py-3 px-4">Inspection ID</th>
                  <th className="py-3 px-4">Timestamp</th>
                  <th className="py-3 px-4">Target Product</th>
                  <th className="py-3 px-4">Mode</th>
                  <th className="py-3 px-4">Measured Size</th>
                  <th className="py-3 px-4">Anomaly</th>
                  <th className="py-3 px-4">Verdict</th>
                  <th className="py-3 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {inspections.map((rec) => (
                  <tr
                    key={rec.id}
                    className="hover:bg-slate-800/40 transition-colors group cursor-pointer"
                    onClick={() => onSelectInspection(rec.id)}
                  >
                    <td className="py-3.5 px-4 font-mono font-medium text-cyan-400">
                      {rec.id.substring(0, 8)}...
                    </td>
                    <td className="py-3.5 px-4 text-slate-400 font-mono text-[11px]">
                      {new Date(rec.created_at).toLocaleDateString()} {new Date(rec.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </td>
                    <td className="py-3.5 px-4 font-medium text-white max-w-[160px] truncate">
                      {rec.product_name || 'Generic Sample'}
                    </td>
                    <td className="py-3.5 px-4">
                      <ModeBadge mode={rec.mode} />
                    </td>
                    <td className="py-3.5 px-4 font-mono text-[11px]">
                      {rec.measured_length ? (
                        <span>
                          {rec.measured_length}×{rec.measured_width} {rec.unit}
                        </span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4 font-mono">
                      {rec.anomaly_score !== null && rec.anomaly_score !== undefined ? (
                        <span className={rec.anomaly_score >= (rec.anomaly_threshold || 0.32) ? 'text-rose-400 font-bold' : 'text-slate-300'}>
                          {rec.anomaly_score.toFixed(3)}
                        </span>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="py-3.5 px-4">
                      <StatusBadge status={rec.overall_status} size="sm" />
                    </td>
                    <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                      <div className="flex items-center justify-end space-x-1">
                        <button
                          onClick={() => onSelectInspection(rec.id)}
                          className="p-1.5 text-slate-400 hover:text-cyan-400 rounded hover:bg-slate-800"
                          title="View Result Details"
                        >
                          <Eye className="w-3.5 h-3.5" />
                        </button>
                        <a
                          href={getPdfReportUrl(rec.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 text-slate-400 hover:text-emerald-400 rounded hover:bg-slate-800"
                          title="Download PDF Report"
                        >
                          <Download className="w-3.5 h-3.5" />
                        </a>
                        <a
                          href={getJsonReportUrl(rec.id)}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1.5 text-slate-400 hover:text-amber-400 rounded hover:bg-slate-800"
                          title="Download Raw JSON"
                        >
                          <FileText className="w-3.5 h-3.5" />
                        </a>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="py-16 text-center space-y-3">
            <History className="w-8 h-8 text-slate-600 mx-auto" />
            <p className="text-xs text-slate-400">No inspection records match current filter criteria.</p>
          </div>
        )}
      </div>
    </div>
  );
};

```

---

## `frontend/src/pages/ModelStatusPage.tsx`

<a id="frontendsrcpagesmodelstatuspagetsx"></a>

```tsx
import React, { useEffect, useState } from 'react';
import { 
  Cpu, 
  CheckCircle2, 
  Layers, 
  Database, 
  RefreshCw, 
  AlertCircle, 
  FileCode, 
  HardDrive 
} from 'lucide-react';
import type { ModelStatus } from '../types';
import { fetchModelStatus } from '../services/api';

export const ModelStatusPage: React.FC = () => {
  const [status, setStatus] = useState<ModelStatus | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const loadStatus = async () => {
    setLoading(true);
    try {
      const data = await fetchModelStatus();
      setStatus(data);
    } catch (err: any) {
      setError(err.message || 'Failed to retrieve model telemetry');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadStatus();
  }, []);

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-[60vh] space-y-4">
        <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
        <p className="text-slate-400 font-mono text-sm">Querying neural backbone and hardware accelerator status...</p>
      </div>
    );
  }

  if (error || !status) {
    return (
      <div className="p-8 max-w-3xl mx-auto">
        <div className="bg-rose-950/40 border border-rose-800 rounded-xl p-6 text-center space-y-3">
          <AlertCircle className="w-10 h-10 text-rose-400 mx-auto" />
          <h2 className="text-lg font-bold text-white">Model Telemetry Unavailable</h2>
          <p className="text-sm text-slate-300">{error}</p>
          <button
            onClick={loadStatus}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-lg text-xs"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8 pb-16 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white font-mono flex items-center space-x-2">
            <Cpu className="w-6 h-6 text-cyan-400" />
            <span>AI MODEL ARCHITECTURE & TELEMETRY</span>
          </h1>
          <p className="text-sm text-slate-400 mt-1">
            Verified technical state of the computer vision pipeline, neural feature extractor, and local embedding banks.
          </p>
        </div>
        <button
          onClick={loadStatus}
          className="p-2.5 bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-300 hover:text-white rounded-lg self-start sm:self-auto transition-colors"
          title="Refresh telemetry"
        >
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Hardware & Backbone Readiness Banner */}
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden bg-gradient-to-r from-slate-900 via-slate-900 to-cyan-950/40">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="space-y-1">
            <span className="text-xs font-mono uppercase text-slate-500">Pipeline Status</span>
            <div className="flex items-center space-x-2 mt-1">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <span className="text-lg font-bold text-white font-mono">OPERATIONAL</span>
            </div>
            <p className="text-xs text-slate-400">Ready for instant zero-shot reference indexing.</p>
          </div>

          <div className="space-y-1">
            <span className="text-xs font-mono uppercase text-slate-500">Compute Hardware Device</span>
            <div className="text-lg font-bold text-cyan-400 font-mono mt-1">
              {status.device_name}
            </div>
            <p className="text-xs text-slate-400">Low-latency localized inference without cloud dependency.</p>
          </div>

          <div className="space-y-1">
            <span className="text-xs font-mono uppercase text-slate-500">Pretrained Weights</span>
            <div className="text-base font-semibold text-slate-200 mt-1">
              {status.weights_status}
            </div>
            <p className="text-xs text-slate-400">Torchvision ResNet-18 residual bottleneck layers.</p>
          </div>
        </div>
      </div>

      {/* Specifications & Artifacts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Architecture Specs */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>Neural Backbone Specifications</span>
          </h2>
          <div className="space-y-2.5 text-xs text-slate-300">
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Backbone Model:</span>
              <span className="font-mono text-white font-medium">{status.backbone}</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Feature Vector Dimension:</span>
              <span className="font-mono text-cyan-400 font-medium">{status.embedding_dim}-dimensional</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Spatial Patch Representation:</span>
              <span className="font-mono text-white font-medium">Layer 4 (512 × 8 × 8)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Metric Formulation:</span>
              <span className="font-mono text-white font-medium">Patch L2 Norm + Global Cosine Distance</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Execution Framework:</span>
              <span className="font-mono text-white font-medium">PyTorch 2.x + TorchVision</span>
            </div>
          </div>
        </div>

        {/* Local Embeddings Banks */}
        <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
          <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-3">
            <Database className="w-4 h-4 text-cyan-400" />
            <span>Cached Product Reference Banks</span>
          </h2>
          <div className="space-y-2.5 text-xs text-slate-300">
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Registered Product Banks:</span>
              <span className="font-mono text-cyan-400 font-bold">{status.total_reference_banks} cache banks (.npz)</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Total Reference Samples Indexed:</span>
              <span className="font-mono text-white font-medium">{status.total_reference_embeddings} golden samples</span>
            </div>
            <div className="flex justify-between py-1 border-b border-slate-800/60">
              <span className="text-slate-400">Cache Storage Location:</span>
              <span className="font-mono text-slate-400 truncate max-w-[220px]">model_artifacts/products/</span>
            </div>
            <div className="flex justify-between py-1">
              <span className="text-slate-400">Retraining Requirement:</span>
              <span className="font-mono text-emerald-400 font-medium">Zero Downtime (Dynamic Indexing)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Supported Defect Classes */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-3">
          <HardDrive className="w-4 h-4 text-cyan-400" />
          <span>Supported Manufacturing Flaw Classes</span>
        </h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
          {status.supported_defect_types.map((type, i) => (
            <div key={i} className="bg-slate-950 p-3 rounded-lg border border-slate-800/80 text-xs text-slate-200 font-mono flex items-center space-x-2">
              <span className="w-2 h-2 rounded-full bg-cyan-400 shrink-0" />
              <span>{type}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Transparent Evaluation */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-xl p-5 space-y-4">
        <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider flex items-center space-x-2 border-b border-slate-800 pb-3">
          <FileCode className="w-4 h-4 text-cyan-400" />
          <span>Evaluation Status & Industrial Training Pipeline</span>
        </h2>
        
        <div className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs space-y-2">
          <div className="flex items-center space-x-2 text-amber-400 font-mono font-semibold">
            <AlertCircle className="w-4 h-4" />
            <span>Honest Model Transparency Protocol:</span>
          </div>
          <p className="text-slate-300 leading-relaxed">
            {status.evaluation_metrics.status} — {status.evaluation_metrics.note}
          </p>
        </div>

        <div className="space-y-2">
          <span className="text-xs font-mono text-slate-400 uppercase">
            Dataset Training Instructions (MVTec AD / Custom Factory Data):
          </span>
          <pre className="bg-slate-950 p-4 rounded-lg border border-slate-800 text-xs text-cyan-300 font-mono overflow-x-auto leading-relaxed">
            {status.training_instructions}
          </pre>
        </div>
      </div>
    </div>
  );
};

```

---

