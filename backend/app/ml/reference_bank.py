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
