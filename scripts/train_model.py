#!/usr/bin/env python3
"""
Train ML model to classify checkboxes using extracted features.
Uses logistic regression with cross-validation.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix
import joblib

def main():
    print("🎓 TRAINING ML MODEL FOR CHECKBOX DETECTION")
    print("=" * 100)
    
    # Load features
    features_file = Path("data/features.json")
    if not features_file.exists():
        print(f"❌ Error: {features_file} not found!")
        print("Run 'python scripts/extract_features.py' first")
        return
    
    with open(features_file) as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    print(f"✅ Loaded {len(df)} feature vectors")
    print(f"   - Checked: {(df['label'] == 1).sum()}")
    print(f"   - Unchecked: {(df['label'] == 0).sum()}")
    
    # Prepare features and labels
    feature_cols = ['fill_pct', 'edge_density', 'stroke_length', 'corner_count', 
                    'num_components', 'hv_ratio', 'variance']
    
    X = df[feature_cols].values
    y = df['label'].values
    
    print(f"\n📊 Feature matrix: {X.shape}")
    
    # Standardize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print("\n📈 Feature scaling (mean ≈ 0, std ≈ 1):")
    print(f"   Mean: {X_scaled.mean(axis=0).round(3)}")
    print(f"   Std:  {X_scaled.std(axis=0).round(3)}")
    
    # Train model with cross-validation
    print("\n🔄 Training with 5-fold cross-validation...")
    
    model = LogisticRegression(
        C=1.0,
        max_iter=1000,
        random_state=42,
        class_weight='balanced'  # Handle class imbalance
    )
    
    # Cross-validation
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    cv_scores = cross_val_score(model, X_scaled, y, cv=cv, scoring='accuracy')
    
    print(f"\n✅ Cross-validation scores: {cv_scores.round(4)}")
    print(f"   Mean accuracy: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Train final model on all data
    print("\n🎯 Training final model on all data...")
    model.fit(X_scaled, y)
    
    # Predict on training data (for analysis)
    y_pred = model.predict(X_scaled)
    y_prob = model.predict_proba(X_scaled)[:, 1]
    
    # Classification report
    print("\n📋 CLASSIFICATION REPORT:")
    print("=" * 100)
    print(classification_report(y, y_pred, target_names=['Unchecked', 'Checked'], digits=4))
    
    # Confusion matrix
    cm = confusion_matrix(y, y_pred)
    print("\n📊 CONFUSION MATRIX:")
    print("=" * 100)
    print(f"                 Predicted")
    print(f"                 Unchecked  Checked")
    print(f"Actual Unchecked    {cm[0, 0]:<7d}  {cm[0, 1]:<7d}")
    print(f"Actual Checked      {cm[1, 0]:<7d}  {cm[1, 1]:<7d}")
    
    tn, fp, fn, tp = cm.ravel()
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    
    print(f"\n✅ Training accuracy: {accuracy:.4f} ({tp + tn}/{len(y)})")
    print(f"   - False Positives: {fp}")
    print(f"   - False Negatives: {fn}")
    
    # Feature importance (coefficients)
    print("\n🔍 FEATURE IMPORTANCE (Logistic Regression Coefficients):")
    print("=" * 100)
    
    coefs = model.coef_[0]
    importance_df = pd.DataFrame({
        'Feature': feature_cols,
        'Coefficient': coefs,
        'Abs_Coefficient': np.abs(coefs)
    }).sort_values('Abs_Coefficient', ascending=False)
    
    for _, row in importance_df.iterrows():
        direction = "📈" if row['Coefficient'] > 0 else "📉"
        print(f"  {direction} {row['Feature']:<20s}: {row['Coefficient']:>8.4f}")
    
    # Save model and scaler
    model_dir = Path("templates/crc_survey_l_anchors_v1")
    model_file = model_dir / "ml_model.pkl"
    scaler_file = model_dir / "ml_scaler.pkl"
    
    joblib.dump(model, model_file)
    joblib.dump(scaler, scaler_file)
    
    print(f"\n💾 Saved model to {model_file}")
    print(f"💾 Saved scaler to {scaler_file}")
    
    # Save feature names for reference
    feature_info = {
        "feature_names": feature_cols,
        "feature_importance": {
            name: float(coef) 
            for name, coef in zip(feature_cols, coefs)
        },
        "scaler_mean": scaler.mean_.tolist(),
        "scaler_std": scaler.scale_.tolist(),
        "training_accuracy": float(accuracy),
        "cv_mean_accuracy": float(cv_scores.mean()),
        "cv_std_accuracy": float(cv_scores.std()),
        "num_samples": len(y),
        "num_checked": int((y == 1).sum()),
        "num_unchecked": int((y == 0).sum())
    }
    
    info_file = model_dir / "ml_model_info.json"
    with open(info_file, 'w') as f:
        json.dump(feature_info, f, indent=2)
    
    print(f"💾 Saved model info to {info_file}")
    
    print("\n" + "=" * 100)
    print("✅ MODEL TRAINING COMPLETE!")
    print("=" * 100)
    print(f"\nExpected improvement over threshold-only: +1-2%")
    print(f"Baseline (threshold): 96.31%")
    print(f"Expected (ML):        97.5-98.5%")
    print(f"\nNext step: Integrate model into run_ocr.py")

if __name__ == "__main__":
    main()
