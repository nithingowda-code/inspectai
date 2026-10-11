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
