import joblib
import numpy as np
import pandas as pd
import json

def model_fn(model_dir):
    """Load the enhanced model from disk"""
    model = joblib.load(f'{model_dir}/model.joblib')
    print(f"✅ Model loaded. Expected features: {model.n_features_in_}")
    return model

def input_fn(request_body, request_content_type):
    """Parse autonomous manufacturing sensor data"""
    if request_content_type == 'application/json':
        data = json.loads(request_body)
        
        # Expected features for autonomous operations
        expected_features = [
            # Core maintenance (existing)
            'Temperature', 'Pressure', 'pH_Level', 'Flow_Rate',
            
            # Equipment health expansion
            'Vibration_X', 'Vibration_Y', 'Vibration_Z',
            'Ultrasound_Leak', 'Acoustic_Emission',
            
            # Quality & process control
            'ORP_Redox', 'Humidity_RH',
            'Vision_Defect_Score', 'Vision_Contaminant_Score',
            
            # Safety & environment
            'CO2_ppm', 'O2_Percent', 'VOC_ppm',
            'Differential_Pressure', 'Refrigerant_Pressure',
            
            # Context (not for prediction, but for analysis)
            'Production_Phase', 'Product_Batch', 'Recipe_ID'
        ]
        
        # Fill missing values with defaults
        defaults = {
            'Temperature': 72.5,
            'Pressure': 14.2,
            'pH_Level': 6.8,
            'Flow_Rate': 1200,
            'Vibration_X': 0.0,
            'Vibration_Y': 0.0,
            'Vibration_Z': 0.0,
            'Ultrasound_Leak': 0.0,
            'Acoustic_Emission': 0.0,
            'ORP_Redox': 400.0,
            'Humidity_RH': 50.0,
            'Vision_Defect_Score': 0.0,
            'Vision_Contaminant_Score': 0.0,
            'CO2_ppm': 420.0,
            'O2_Percent': 20.8,
            'VOC_ppm': 0.0,
            'Differential_Pressure': 0.1,
            'Refrigerant_Pressure': 8.0
        }
        
        # Ensure all expected features are present
        for feature in expected_features:
            if feature not in data and feature in defaults:
                data[feature] = defaults[feature]
                print(f"⚠️  Using default for missing feature: {feature} = {defaults[feature]}")
        
        # Separate prediction features from context
        prediction_features = [f for f in expected_features if f not in 
                             ['Production_Phase', 'Product_Batch', 'Recipe_ID']]
        
        # Create DataFrame with correct feature order
        prediction_data = {k: [data[k]] for k in prediction_features if k in data}
        
        # Store context for later use
        request_body['_context'] = {
            'Production_Phase': data.get('Production_Phase', 'Unknown'),
            'Product_Batch': data.get('Product_Batch', 'Unknown'),
            'Recipe_ID': data.get('Recipe_ID', 'Default')
        }
        
        print(f"📊 Input shape: {len(prediction_data)} features")
        return pd.DataFrame(prediction_data)
        
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}")

def predict_fn(input_data, model):
    """Make predictions with enhanced analysis"""
    try:
        # Standard prediction
        prediction = model.predict(input_data)
        probability = model.predict_proba(input_data)
        
        # Extract failure probability
        failure_prob = float(probability[0][1])
        confidence = float(np.max(probability[0]))
        
        # Get context if available
        context = getattr(input_data, '_context', {}) if hasattr(input_data, '_context') else {}
        
        # Enhanced analysis based on sensor values
        analysis = {
            'prediction': int(prediction[0]),
            'probability_failure': failure_prob,
            'confidence': confidence,
            
            # Sensor health indicators
            'sensor_health': analyze_sensor_health(input_data.iloc[0].to_dict()),
            
            # Quality indicators
            'quality_risk': calculate_quality_risk(input_data.iloc[0].to_dict()),
            
            # Safety indicators
            'safety_risk': calculate_safety_risk(input_data.iloc[0].to_dict()),
            
            # Maintenance urgency
            'maintenance_urgency': calculate_maintenance_urgency(
                failure_prob, 
                input_data.iloc[0].to_dict()
            ),
            
            # Context
            'production_phase': context.get('Production_Phase', 'Unknown'),
            'product_batch': context.get('Product_Batch', 'Unknown'),
            'recipe_id': context.get('Recipe_ID', 'Default'),
            
            # Timestamp
            'timestamp': pd.Timestamp.now().isoformat()
        }
        
        # Add recommendations
        analysis['recommendations'] = generate_recommendations(analysis)
        
        print(f"✅ Prediction complete: {analysis['prediction']} "
              f"(fail prob: {failure_prob:.2%}, confidence: {confidence:.2%})")
        
        return analysis
        
    except Exception as e:
        print(f"❌ Prediction error: {e}")
        raise

def output_fn(prediction, response_content_type):
    """Format enhanced output"""
    if response_content_type == 'application/json':
        return json.dumps(prediction, default=str)
    else:
        raise ValueError(f"Unsupported content type: {response_content_type}")

# ===== ENHANCED ANALYSIS FUNCTIONS =====

def analyze_sensor_health(sensor_data):
    """Check if sensors are operating within expected ranges"""
    health_checks = []
    
    # Vibration sensor correlation
    vib_magnitude = np.sqrt(
        sensor_data.get('Vibration_X', 0)**2 +
        sensor_data.get('Vibration_Y', 0)**2 +
        sensor_data.get('Vibration_Z', 0)**2
    )
    
    if vib_magnitude > 5.0:
        health_checks.append("HIGH_VIBRATION_IMBALANCE")
    
    # Sensor consistency check
    if sensor_data.get('Temperature', 72) > 85:
        health_checks.append("TEMPERATURE_SENSOR_OUT_OF_RANGE")
    
    if sensor_data.get('pH_Level', 7.0) < 4.0 or sensor_data.get('pH_Level', 7.0) > 9.0:
        health_checks.append("PH_SENSOR_POSSIBLE_FAULT")
    
    return health_checks if health_checks else ["ALL_SENSORS_NORMAL"]

def calculate_quality_risk(sensor_data):
    """Calculate product quality risk score (0-100%)"""
    risk_score = 0
    
    # pH deviation from ideal (6.5-7.0 for most beverages)
    ph_deviation = abs(sensor_data.get('pH_Level', 6.8) - 6.75)
    risk_score += min(ph_deviation * 10, 30)  # Up to 30% risk
    
    # Temperature stability (should be ±2°C)
    if abs(sensor_data.get('Temperature', 72) - 75) > 5:
        risk_score += 25
    
    # Vision system defects
    risk_score += sensor_data.get('Vision_Defect_Score', 0) * 40
    risk_score += sensor_data.get('Vision_Contaminant_Score', 0) * 100
    
    # Humidity control
    if sensor_data.get('Humidity_RH', 50) > 70:
        risk_score += 20
    
    return min(risk_score, 100)

def calculate_safety_risk(sensor_data):
    """Calculate safety risk score (0-100%)"""
    risk_score = 0
    
    # Explosive atmosphere risk
    if sensor_data.get('CO2_ppm', 0) > 1000:
        risk_score += 40
    if sensor_data.get('VOC_ppm', 0) > 5:
        risk_score += 30
    
    # Pressure hazards
    if sensor_data.get('Pressure', 0) > 20:
        risk_score += 30
    if sensor_data.get('Differential_Pressure', 0) > 0.3:
        risk_score += 20
    
    # Ultrasound leak detection
    if sensor_data.get('Ultrasound_Leak', 0) > 50:
        risk_score += 25
    
    return min(risk_score, 100)

def calculate_maintenance_urgency(failure_prob, sensor_data):
    """Calculate maintenance urgency score"""
    urgency = failure_prob * 100  # Base on failure probability
    
    # Add vibration factors
    vib_total = (abs(sensor_data.get('Vibration_X', 0)) +
                 abs(sensor_data.get('Vibration_Y', 0)) +
                 abs(sensor_data.get('Vibration_Z', 0)))
    
    if vib_total > 6:
        urgency += 30
    
    # Add acoustic factors
    if sensor_data.get('Acoustic_Emission', 0) > 0.7:
        urgency += 20
    
    # Critical pH sensor for food/beverage
    if sensor_data.get('pH_Level', 6.8) < 5.5 or sensor_data.get('pH_Level', 6.8) > 7.5:
        urgency += 40  # HACCP violation risk
    
    return min(urgency, 100)

def generate_recommendations(analysis):
    """Generate autonomous recommendations"""
    recs = []
    
    # Safety first
    if analysis['safety_risk'] > 60:
        recs.append("IMMEDIATE_SAFETY_SHUTDOWN")
        recs.append("ACTIVATE_EMERGENCY_VENTILATION")
    
    # Quality control
    if analysis['quality_risk'] > 40:
        recs.append("ISOLATE_CURRENT_BATCH")
        if analysis['quality_risk'] > 70:
            recs.append("AUTO_REJECT_BATCH")
    
    # Maintenance scheduling
    if analysis['maintenance_urgency'] > 80:
        recs.append("SCHEDULE_MAINTENANCE_IMMEDIATELY")
    elif analysis['maintenance_urgency'] > 60:
        recs.append("SCHEDULE_MAINTENANCE_NEXT_SHIFT")
    elif analysis['maintenance_urgency'] > 40:
        recs.append("PLANNED_MAINTENANCE_72H")
    
    # Process optimization
    if (analysis['probability_failure'] < 0.2 and 
        analysis['quality_risk'] < 20 and 
        analysis['safety_risk'] < 30):
        recs.append("OPTIMIZE_FOR_EFFICIENCY")
        recs.append("INCREASE_THROUGHPUT_5PCT")
    
    # Sensor maintenance
    if "PH_SENSOR_POSSIBLE_FAULT" in analysis['sensor_health']:
        recs.append("CALIBRATE_PH_SENSOR")
    
    return recs if recs else ["CONTINUE_NORMAL_OPERATIONS"]

# For local testing
if __name__ == "__main__":
    # Test with autonomous sensor data
    test_payload = {
        "Temperature": 79.5,
        "Pressure": 15.2,
        "pH_Level": 6.5,
        "Flow_Rate": 1250,
        "Vibration_X": 2.3,
        "Vibration_Y": 1.8,
        "Vibration_Z": 3.1,
        "Ultrasound_Leak": 45.2,
        "Acoustic_Emission": 0.85,
        "ORP_Redox": 450,
        "Humidity_RH": 65.2,
        "Vision_Defect_Score": 0.02,
        "Vision_Contaminant_Score": 0.001,
        "CO2_ppm": 420,
        "O2_Percent": 20.8,
        "VOC_ppm": 2.1,
        "Differential_Pressure": 0.15,
        "Refrigerant_Pressure": 8.2,
        "Production_Phase": "Filling",
        "Product_Batch": "BRW-20240207-001",
        "Recipe_ID": "IPA_V2"
    }
    
    # Simulate SageMaker endpoint call
    import json
    
    print("🧪 Testing inference.py locally...")
    print("Input payload:", json.dumps(test_payload, indent=2))
    
    # Test input_fn
    df = input_fn(json.dumps(test_payload), 'application/json')
    print(f"\n✅ DataFrame created with {df.shape[1]} features")
    print("Features:", list(df.columns))
    
    # Note: Need actual model.joblib for full test
    print("\n📝 To fully test, you need to:")
    print("1. Train new model with 14+ features")
    print("2. Save as model.joblib")
    print("3. Deploy to SageMaker endpoint")

    