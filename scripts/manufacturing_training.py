# manufacturing_training_autonomous.py
import pandas as pd
import numpy as np
import json
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import argparse
import os
import warnings
warnings.filterwarnings('ignore')

def main():
    parser = argparse.ArgumentParser(description='Train autonomous manufacturing model')
    parser.add_argument('--train', type=str, default=os.environ.get('SM_CHANNEL_TRAIN'))
    parser.add_argument('--model-dir', type=str, default=os.environ.get('SM_MODEL_DIR'))
    parser.add_argument('--output-dir', type=str, default=os.environ.get('SM_OUTPUT_DIR'))
    parser.add_argument('--n-estimators', type=int, default=200)
    parser.add_argument('--test-size', type=float, default=0.2)
    args = parser.parse_args()
    
    print("="*60)
    print("🚀 TRAINING AUTONOMOUS MANUFACTURING MODEL")
    print("="*60)
    
    # Load data
    print("📥 Loading manufacturing data...")
    train_files = [os.path.join(args.train, f) for f in os.listdir(args.train) 
                   if f.endswith('.csv') or f.endswith('.parquet')]
    
    if not train_files:
        raise ValueError(f"No training files found in {args.train}")
    
    # Load and concatenate data
    data_frames = []
    for file in train_files:
        if file.endswith('.csv'):
            df = pd.read_csv(file)
        elif file.endswith('.parquet'):
            df = pd.read_parquet(file)
        data_frames.append(df)
    
    df = pd.concat(data_frames, ignore_index=True)
    
    print(f"✅ Loaded {len(df)} samples with {df.shape[1]} columns")
    
    # ===== ENHANCED FEATURE ENGINEERING =====
    print("⚙️ Engineering features for autonomous operations...")
    
    # Define ALL 17+ features for autonomous manufacturing
    base_features = [
        # Core maintenance (original 4)
        'temperature_c', 'pressure_bar', 'ph_level', 'flow_rate_lph',
        
        # Equipment health expansion
        'vibration_x', 'vibration_y', 'vibration_z',
        'ultrasound_leak_db', 'acoustic_emission',
        
        # Quality & process control  
        'orp_redox_mv', 'humidity_rh',
        'vision_defect_score', 'vision_contaminant_score',
        
        # Safety & environment
        'co2_ppm', 'o2_percent', 'voc_ppm',
        'differential_pressure_bar', 'refrigerant_pressure_bar'
    ]
    
    # Check which features exist in data
    available_features = [f for f in base_features if f in df.columns]
    missing_features = [f for f in base_features if f not in df.columns]
    
    if missing_features:
        print(f"⚠️  Missing features: {missing_features}")
        print("   Using available features for training")
    
    # Create derived features for better predictions
    print("🔬 Creating derived features...")
    
    # Vibration magnitude (important for imbalance detection)
    if all(f in df.columns for f in ['vibration_x', 'vibration_y', 'vibration_z']):
        df['vibration_magnitude'] = np.sqrt(
            df['vibration_x']**2 + df['vibration_y']**2 + df['vibration_z']**2
        )
        available_features.append('vibration_magnitude')
    
    # Process stability indicators
    if 'flow_rate_lph' in df.columns:
        df['flow_rate_normalized'] = df['flow_rate_lph'] / df['flow_rate_lph'].median()
        available_features.append('flow_rate_normalized')
    
    if 'temperature_c' in df.columns:
        df['temperature_deviation'] = abs(df['temperature_c'] - df['temperature_c'].median())
        available_features.append('temperature_deviation')
    
    # Safety composite score
    safety_features = ['co2_ppm', 'voc_ppm', 'pressure_bar']
    if all(f in df.columns for f in safety_features):
        df['safety_risk_score'] = (
            (df['co2_ppm'] > 1000).astype(int) * 0.4 +
            (df['voc_ppm'] > 10).astype(int) * 0.3 +
            (df['pressure_bar'] > 20).astype(int) * 0.3
        )
        available_features.append('safety_risk_score')
    
    # Quality composite score
    quality_features = ['ph_level', 'vision_defect_score', 'vision_contaminant_score']
    if all(f in df.columns for f in quality_features):
        df['quality_risk_score'] = (
            ((df['ph_level'] < 5.5) | (df['ph_level'] > 7.5)).astype(int) * 0.4 +
            (df['vision_defect_score'] > 0.05).astype(int) * 0.3 +
            (df['vision_contaminant_score'] > 0.01).astype(int) * 0.3
        )
        available_features.append('quality_risk_score')
    
    print(f"✅ Total features for training: {len(available_features)}")
    print(f"   Features: {available_features}")
    
    # ===== PREPARE TRAINING DATA =====
    print("\n📊 Preparing training data...")
    
    # Handle missing values
    X = df[available_features].copy()
    
    # Fill missing values with median (better than 0 for sensors)
    for col in X.columns:
        if X[col].isnull().any():
            median_val = X[col].median()
            X[col].fillna(median_val, inplace=True)
            print(f"   Filled missing values in '{col}' with median: {median_val:.2f}")
    
    # Determine target variable
    # For autonomous operations, we need multi-dimensional prediction
    # Let's create a composite failure target that considers all risks
    
    if 'failure_risk' in df.columns:
        # If we have existing failure labels
        y = df['failure_risk']
        print(f"✅ Using existing 'failure_risk' as target")
    else:
        # Create synthetic target based on sensor anomalies
        print("⚠️  No 'failure_risk' column found. Creating synthetic target...")
        
        # Create composite failure score from multiple indicators
        failure_score = np.zeros(len(df))
        
        # Temperature anomalies
        if 'temperature_c' in df.columns:
            temp_zscore = abs((df['temperature_c'] - df['temperature_c'].mean()) / df['temperature_c'].std())
            failure_score += (temp_zscore > 2).astype(int) * 0.2
        
        # Vibration anomalies
        if 'vibration_magnitude' in df.columns:
            vib_zscore = abs((df['vibration_magnitude'] - df['vibration_magnitude'].mean()) / df['vibration_magnitude'].std())
            failure_score += (vib_zscore > 2).astype(int) * 0.3
        
        # Pressure anomalies
        if 'pressure_bar' in df.columns:
            pressure_zscore = abs((df['pressure_bar'] - df['pressure_bar'].mean()) / df['pressure_bar'].std())
            failure_score += (pressure_zscore > 2).astype(int) * 0.2
        
        # Quality failures
        if 'vision_contaminant_score' in df.columns:
            failure_score += (df['vision_contaminant_score'] > 0.01).astype(int) * 0.3
        
        # Convert to binary target (failure if score > 0.5)
        y = (failure_score > 0.5).astype(int)
        print(f"✅ Created synthetic target: {y.sum()} failures out of {len(y)} samples")
    
    # ===== TRAIN MODEL =====
    print("\n🎯 Training RandomForest model...")
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=args.test_size, random_state=42, stratify=y
    )
    
    print(f"   Training samples: {len(X_train)}")
    print(f"   Test samples: {len(X_test)}")
    print(f"   Positive class ratio: {y.mean():.3f}")
    
    # Scale features (optional for tree-based models, but good practice)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train model with more estimators for complex patterns
    model = RandomForestClassifier(
        n_estimators=args.n_estimators,
        max_depth=20,
        min_samples_split=5,
        min_samples_leaf=2,
        random_state=42,
        n_jobs=-1,  # Use all CPU cores
        class_weight='balanced'  # Handle imbalanced data
    )
    
    print(f"   Training with {args.n_estimators} estimators...")
    model.fit(X_train_scaled, y_train)
    
    # ===== EVALUATE MODEL =====
    print("\n📈 Evaluating model performance...")
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_pred_proba = model.predict_proba(X_test_scaled)
    
    # Calculate metrics
    accuracy = accuracy_score(y_test, y_pred)
    
    print(f"✅ Test Accuracy: {accuracy:.3f}")
    print(f"✅ Test AUC (ROC): {np.mean(cross_val_score(model, X, y, cv=5, scoring='roc_auc')):.3f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': available_features,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n🔝 Top 10 most important features:")
    for i, row in feature_importance.head(10).iterrows():
        print(f"   {row['feature']}: {row['importance']:.3f}")
    
    # ===== SAVE MODEL & ARTIFACTS =====
    print("\n💾 Saving model and artifacts...")
    
    # Save model
    model_path = os.path.join(args.model_dir, 'autonomous_model.joblib')
    joblib.dump(model, model_path)
    print(f"✅ Model saved to {model_path}")
    
    # Save scaler (critical for inference)
    scaler_path = os.path.join(args.model_dir, 'scaler.joblib')
    joblib.dump(scaler, scaler_path)
    print(f"✅ Scaler saved to {scaler_path}")
    
    # Save feature list (critical for inference.py)
    features_dict = {
        'features': available_features,
        'feature_importance': feature_importance.to_dict('records'),
        'training_date': pd.Timestamp.now().isoformat()
    }
    
    features_path = os.path.join(args.model_dir, 'features.json')
    with open(features_path, 'w') as f:
        json.dump(features_dict, f, indent=2)
    print(f"✅ Features metadata saved to {features_path}")
    
    # Save comprehensive metrics
    metrics = {
        'model_type': 'RandomForestClassifier',
        'accuracy': float(accuracy),
        'n_estimators': args.n_estimators,
        'training_samples': len(X_train),
        'test_samples': len(X_test),
        'feature_count': len(available_features),
        'class_distribution': {
            'total_samples': len(y),
            'failures': int(y.sum()),
            'non_failures': int(len(y) - y.sum()),
            'failure_rate': float(y.mean())
        },
        'top_features': feature_importance.head(10).to_dict('records')
    }
    
    metrics_path = os.path.join(args.output_dir, 'training_metrics.json')
    with open(metrics_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Metrics saved to {metrics_path}")
    
    # Create example payload for testing inference
    example_payload = {
        feature: float(X_test.iloc[0][feature]) if feature in X_test.columns else 0.0
        for feature in base_features
    }
    
    example_path = os.path.join(args.output_dir, 'example_payload.json')
    with open(example_path, 'w') as f:
        json.dump(example_payload, f, indent=2)
    print(f"✅ Example payload saved to {example_path}")
    
    print("\n" + "="*60)
    print("🎉 AUTONOMOUS MANUFACTURING MODEL TRAINING COMPLETE!")
    print("="*60)
    print(f"\n📊 Model Performance: {accuracy:.1%} accuracy")
    print(f"📁 Model saved as: autonomous_model.joblib")
    print(f"🔧 Features used: {len(available_features)}")
    print(f"\n🚀 Next steps:")
    print(f"   1. Update inference.py to use new features")
    print(f"   2. Deploy model to SageMaker endpoint")
    print(f"   3. Test with example_payload.json")
    print("="*60)

if __name__ == '__main__':
    main()
    