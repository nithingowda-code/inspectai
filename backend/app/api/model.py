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
