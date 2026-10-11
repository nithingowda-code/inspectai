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
