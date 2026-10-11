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
