import joblib
import numpy as np
import pandas as pd
import json
import os

def model_fn(model_dir):
    """Load the autonomous manufacturing model and artifacts"""
    print(f"📦 Loading model from: {model_dir}")
    
    # Load the trained model
    model_path = os.path.join(model_dir, 'autonomous_model.joblib')
    if os.path.exists(model_path):
        model = joblib.load(model_path)
        print(f"✅ Loaded autonomous_model.joblib with {model.n_features_in_} features")
    else:
        # Fallback to original model
        model = joblib.load(os.path.join(model_dir, 'model.joblib'))
        print(f"⚠️  Loaded fallback model.joblib with {model.n_features_in_} features")
    
    # Load scaler (critical for autonomous model)
    scaler_path = os.path.join(model_dir, 'scaler.joblib')
    if os.path.exists(scaler_path):
        scaler = joblib.load(scaler_path)
        print("✅ Loaded feature scaler")
    else:
        scaler = None
        print("⚠️  No scaler found - using raw features")
    
    # Load feature metadata
    features_path = os.path.join(model_dir, 'features.json')
    if os.path.exists(features_path):
        with open(features_path, 'r') as f:
            feature_metadata = json.load(f)
        expected_features = feature_metadata.get('features', [])
        print(f"✅ Loaded feature metadata: {len(expected_features)} features")
    else:
        expected_features = [
            'temperature_c', 'ph_level', 'flow_rate_lph', 'pressure_bar'
        ]
        print("⚠️  Using default features (no metadata found)")
    
    return {
        'model': model,
        'scaler': scaler,
        'expected_features': expected_features,
        'model_metadata': feature_metadata if os.path.exists(features_path) else None
    }

def input_fn(request_body, request_content_type):
    """Parse autonomous manufacturing sensor input"""
    print(f"📥 Received request with content type: {request_content_type}")
    
    if request_content_type == 'application/json':
        try:
            data = json.loads(request_body)
            print(f"✅ Parsed JSON data with {len(data)} keys")
            
            # Store raw data for debugging
            input_data = {
                'raw_data': data,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
            return input_data
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON decode error: {e}")
            raise ValueError(f"Invalid JSON: {str(e)}")
    
    else:
        raise ValueError(f"Unsupported content type: {request_content_type}. Expected 'application/json'")

def predict_fn(input_data, artifacts):
    """Make autonomous manufacturing predictions with enhanced analysis"""
    
    model = artifacts['model']
    scaler = artifacts['scaler']
    expected_features = artifacts['expected_features']
    raw_data = input_data['raw_data']
    
    print(f"🎯 Making prediction with {len(expected_features)} expected features")
    
    try:
        # ===== 1. PREPARE FEATURES =====
        # Extract features in correct order with defaults
        feature_values = []
        missing_features = []
        
        for feature in expected_features:
            if feature in raw_data:
                value = float(raw_data[feature])
                feature_values.append(value)
            else:
                # Use intelligent defaults based on feature type
                default_value = get_intelligent_default(feature, raw_data)
                feature_values.append(default_value)
                missing_features.append((feature, default_value))
        
        if missing_features:
            print(f"⚠️  Using defaults for missing features: {missing_features}")
        
        X = np.array([feature_values])
        
        # ===== 2. SCALE FEATURES IF SCALER EXISTS =====
        if scaler is not None:
            X_scaled = scaler.transform(X)
            print(f"✅ Features scaled using trained scaler")
        else:
            X_scaled = X
            print(f"⚠️  Using unscaled features (no scaler)")
        
        # ===== 3. MAKE PREDICTION =====
        prediction = model.predict(X_scaled)[0]
        probability = model.predict_proba(X_scaled)[0]
        
        failure_prob = float(probability[1]) if len(probability) > 1 else 0.0
        confidence = float(np.max(probability))
        
        # ===== 4. ENHANCED ANALYSIS =====
        print("🔬 Performing enhanced analysis...")
        
        # Sensor health analysis
        sensor_health = analyze_sensor_health(raw_data, expected_features)
        
        # Quality risk analysis
        quality_risk = calculate_quality_risk(raw_data)
        
        # Safety risk analysis
        safety_risk = calculate_safety_risk(raw_data)
        
        # Maintenance urgency
        maintenance_urgency = calculate_maintenance_urgency(failure_prob, raw_data)
        
        # Process stability
        process_stability = calculate_process_stability(raw_data)
        
        # ===== 5. GENERATE RECOMMENDATIONS =====
        recommendations = generate_autonomous_recommendations(
            failure_prob, quality_risk, safety_risk, raw_data
        )
        
        # ===== 6. BUILD COMPREHENSIVE RESPONSE =====
        result = {
            # Core prediction
            'prediction': int(prediction),
            'probability_failure': failure_prob,
            'confidence': confidence,
            
            # Enhanced analysis
            'sensor_health': sensor_health,
            'quality_risk_score': quality_risk,
            'safety_risk_score': safety_risk,
            'maintenance_urgency_score': maintenance_urgency,
            'process_stability_score': process_stability,
            
            # Autonomous recommendations
            'recommendations': recommendations,
            'autonomous_actions': generate_autonomous_actions(
                failure_prob, quality_risk, safety_risk
            ),
            
            # Metadata
            'model_version': 'autonomous_v1',
            'features_used': len(expected_features),
            'missing_features_defaulted': len(missing_features),
            'timestamp': input_data['timestamp'],
            'raw_features_used': dict(zip(expected_features, feature_values))
        }
        
        # Add context if provided
        context_keys = ['line_id', 'batch_id', 'production_phase', 'equipment_id']
        for key in context_keys:
            if key in raw_data:
                result[key] = raw_data[key]
        
        print(f"✅ Prediction complete: failure_prob={failure_prob:.3f}, confidence={confidence:.3f}")
        
        return result
        
    except Exception as e:
        print(f"❌ Prediction error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Return error response
        return {
            'error': str(e),
            'prediction': -1,
            'probability_failure': 0.0,
            'confidence': 0.0,
            'timestamp': input_data['timestamp'],
            'emergency_recommendation': 'CHECK_SYSTEM_IMMEDIATELY'
        }

def output_fn(prediction, response_content_type):
    """Format output for SageMaker endpoint"""
    if response_content_type == 'application/json':
        response = json.dumps(prediction, default=str, indent=2)
        print(f"📤 Returning response with {len(response)} characters")
        return response
    else:
        raise ValueError(f"Unsupported content type: {response_content_type}. Expected 'application/json'")

# ===== ENHANCED ANALYSIS FUNCTIONS =====

def get_intelligent_default(feature_name, available_data):
    """Get intelligent default values based on feature type and available data"""
    
    # Default values for autonomous manufacturing sensors
    defaults = {
        # Core maintenance
        'temperature_c': 75.0,
        'pressure_bar': 15.0,
        'ph_level': 6.8,
        'flow_rate_lph': 1200.0,
        
        # Equipment health
        'vibration_x': 0.0,
        'vibration_y': 0.0,
        'vibration_z': 0.0,
        'vibration_magnitude': 0.0,
        'ultrasound_leak_db': 0.0,
        'acoustic_emission': 0.0,
        
        # Quality & process
        'orp_redox_mv': 400.0,
        'humidity_rh': 55.0,
        'vision_defect_score': 0.0,
        'vision_contaminant_score': 0.0,
        
        # Safety & environment
        'co2_ppm': 420.0,
        'o2_percent': 20.8,
        'voc_ppm': 0.0,
        'differential_pressure_bar': 0.1,
        'refrigerant_pressure_bar': 8.5,
        
        # Derived features
        'flow_rate_normalized': 1.0,
        'temperature_deviation': 0.0,
        'safety_risk_score': 0.0,
        'quality_risk_score': 0.0
    }
    
    # Try to infer from similar features
    if feature_name in defaults:
        return defaults[feature_name]
    
    # If it's a derived feature, calculate from available data
    if 'normalized' in feature_name:
        base_feature = feature_name.replace('_normalized', '')
        if base_feature in available_data:
            return float(available_data[base_feature]) / 1000.0  # Rough normalization
    
    if 'deviation' in feature_name:
        base_feature = feature_name.replace('_deviation', '')
        if base_feature in available_data:
            return abs(float(available_data[base_feature]) - defaults.get(base_feature, 0))
    
    return 0.0

def analyze_sensor_health(sensor_data, expected_features):
    """Analyze sensor health and data quality"""
    issues = []
    
    # Check for unrealistic values
    if 'ph_level' in sensor_data:
        ph = float(sensor_data['ph_level'])
        if ph < 0 or ph > 14:
            issues.append(f"PH_SENSOR_FAULT: {ph}")
    
    if 'temperature_c' in sensor_data:
        temp = float(sensor_data['temperature_c'])
        if temp < -50 or temp > 200:
            issues.append(f"TEMPERATURE_SENSOR_FAULT: {temp}")
    
    # Check for stale data (all zeros or same values)
    numeric_values = [float(v) for k, v in sensor_data.items() 
                     if isinstance(v, (int, float)) and not k.startswith('vision_')]
    if len(numeric_values) > 5:
        if np.std(numeric_values) < 0.1:
            issues.append("LOW_VARIANCE_POSSIBLE_STALE_DATA")
    
    # Check for missing critical sensors
    critical_sensors = ['temperature_c', 'pressure_bar', 'ph_level']
    missing_critical = [s for s in critical_sensors if s not in sensor_data]
    if missing_critical:
        issues.append(f"MISSING_CRITICAL_SENSORS: {missing_critical}")
    
    return issues if issues else ["ALL_SENSORS_NORMAL"]

def calculate_quality_risk(sensor_data):
    """Calculate product quality risk (0-100%)"""
    risk = 0.0
    
    # pH deviation (critical for food/beverage)
    if 'ph_level' in sensor_data:
        ph = float(sensor_data['ph_level'])
        ph_deviation = abs(ph - 6.75)
        risk += min(ph_deviation * 20, 40)  # Up to 40% risk
    
    # Vision system defects
    if 'vision_defect_score' in sensor_data:
        risk += float(sensor_data['vision_defect_score']) * 40
    
    if 'vision_contaminant_score' in sensor_data:
        risk += float(sensor_data['vision_contaminant_score']) * 100
    
    # Humidity control
    if 'humidity_rh' in sensor_data:
        humidity = float(sensor_data['humidity_rh'])
        if humidity > 70 or humidity < 40:
            risk += 20
    
    # Oxidation risk
    if 'orp_redox_mv' in sensor_data:
        orp = float(sensor_data['orp_redox_mv'])
        if orp < 300:
            risk += 15
    
    return min(risk, 100.0)

def calculate_safety_risk(sensor_data):
    """Calculate safety risk (0-100%)"""
    risk = 0.0
    
    # Explosive atmosphere
    if 'co2_ppm' in sensor_data:
        co2 = float(sensor_data['co2_ppm'])
        if co2 > 800:
            risk += min((co2 - 800) / 10, 40)  # Up to 40% risk
    
    if 'voc_ppm' in sensor_data:
        voc = float(sensor_data['voc_ppm'])
        if voc > 5:
            risk += min(voc * 5, 30)  # Up to 30% risk
    
    # Pressure hazards
    if 'pressure_bar' in sensor_data:
        pressure = float(sensor_data['pressure_bar'])
        if pressure > 18:
            risk += min((pressure - 18) * 5, 25)
    
    # Refrigerant pressure
    if 'refrigerant_pressure_bar' in sensor_data:
        ref_pressure = float(sensor_data['refrigerant_pressure_bar'])
        if abs(ref_pressure - 8.5) > 2:
            risk += 15
    
    return min(risk, 100.0)

def calculate_maintenance_urgency(failure_prob, sensor_data):
    """Calculate maintenance urgency (0-100%)"""
    urgency = failure_prob * 100  # Base urgency
    
    # Vibration adds urgency
    vibration_keys = ['vibration_x', 'vibration_y', 'vibration_z', 'vibration_magnitude']
    vib_values = [float(sensor_data.get(k, 0)) for k in vibration_keys if k in sensor_data]
    
    if vib_values:
        max_vibration = max(vib_values)
        if max_vibration > 3.0:
            urgency += min((max_vibration - 3.0) * 10, 30)
    
    # Ultrasound leak detection
    if 'ultrasound_leak_db' in sensor_data:
        ultrasound = float(sensor_data['ultrasound_leak_db'])
        if ultrasound > 40:
            urgency += min((ultrasound - 40) / 2, 25)
    
    # Acoustic emission
    if 'acoustic_emission' in sensor_data:
        acoustic = float(sensor_data['acoustic_emission'])
        if acoustic > 0.6:
            urgency += min((acoustic - 0.6) * 50, 20)
    
    return min(urgency, 100.0)

def calculate_process_stability(sensor_data):
    """Calculate process stability score (0-100%, higher is better)"""
    stability = 100.0
    
    # Flow rate stability
    if 'flow_rate_lph' in sensor_data:
        flow = float(sensor_data['flow_rate_lph'])
        flow_deviation = abs(flow - 1200) / 1200
        stability -= min(flow_deviation * 50, 30)
    
    # Temperature stability
    if 'temperature_c' in sensor_data:
        temp = float(sensor_data['temperature_c'])
        temp_deviation = abs(temp - 75)
        stability -= min(temp_deviation * 4, 25)
    
    # Pressure stability
    if 'pressure_bar' in sensor_data:
        pressure = float(sensor_data['pressure_bar'])
        pressure_deviation = abs(pressure - 15)
        stability -= min(pressure_deviation * 6, 20)
    
    return max(stability, 0.0)

def generate_autonomous_recommendations(failure_prob, quality_risk, safety_risk, sensor_data):
    """Generate autonomous manufacturing recommendations"""
    recommendations = []
    
    # Safety first
    if safety_risk > 60:
        recommendations.append("ACTIVATE_EMERGENCY_VENTILATION")
    if safety_risk > 80:
        recommendations.append("SHUTDOWN_HEAT_SOURCES")
        recommendations.append("EVACUATE_AREA_IMMEDIATELY")
    
    # Quality control
    if quality_risk > 40:
        recommendations.append("ISOLATE_CURRENT_BATCH")
    if quality_risk > 70:
        recommendations.append("AUTO_REJECT_BATCH")
        recommendations.append("INITIATE_CLEANING_CYCLE")
    
    # Maintenance scheduling
    if failure_prob > 0.8:
        recommendations.append("IMMEDIATE_SHUTDOWN_MAINTENANCE")
    elif failure_prob > 0.6:
        recommendations.append("SCHEDULE_MAINTENANCE_NEXT_SHIFT")
    elif failure_prob > 0.4:
        recommendations.append("PLANNED_MAINTENANCE_72H")
    
    # Process optimization
    if failure_prob < 0.2 and quality_risk < 20 and safety_risk < 30:
        recommendations.append("OPTIMIZE_FOR_EFFICIENCY")
        
        # Specific optimizations based on sensors
        if 'flow_rate_lph' in sensor_data and float(sensor_data['flow_rate_lph']) < 1100:
            recommendations.append("INCREASE_FLOW_RATE_5PCT")
        
        if 'temperature_c' in sensor_data and float(sensor_data['temperature_c']) < 73:
            recommendations.append("OPTIMIZE_HEATING_CYCLE")
    
    # Sensor maintenance
    if 'ph_level' in sensor_data:
        ph = float(sensor_data['ph_level'])
        if ph < 5.0 or ph > 8.0:
            recommendations.append("CALIBRATE_PH_SENSOR")
    
    return recommendations if recommendations else ["CONTINUE_NORMAL_OPERATIONS"]

def generate_autonomous_actions(failure_prob, quality_risk, safety_risk):
    """Generate immediate autonomous actions"""
    actions = []
    
    if safety_risk > 80:
        actions.append("AUTO_SHUTDOWN")
        actions.append("ACTIVATE_ALARM")
    
    elif failure_prob > 0.8:
        actions.append("SCHEDULE_IMMEDIATE_MAINTENANCE")
        actions.append("REDUCE_PRODUCTION_SPEED_50PCT")
    
    elif quality_risk > 70:
        actions.append("DIVERT_BATCH_TO_QUALITY_CHECK")
        actions.append("INCREASE_SAMPLING_RATE")
    
    return actions

# Local testing function
if __name__ == "__main__":
    """Test the inference script locally"""
    print("🧪 Testing production_inference.py locally...")
    
    # Create mock artifacts
    class MockModel:
        def __init__(self):
            self.n_features_in_ = 17
        
        def predict(self, X):
            return np.array([0])
        
        def predict_proba(self, X):
            return np.array([[0.85, 0.15]])
    
    class MockScaler:
        def transform(self, X):
            return X
    
    artifacts = {
        'model': MockModel(),
        'scaler': MockScaler(),
        'expected_features': [
            'temperature_c', 'pressure_bar', 'ph_level', 'flow_rate_lph',
            'vibration_x', 'vibration_y', 'vibration_z',
            'ultrasound_leak_db', 'acoustic_emission',
            'orp_redox_mv', 'humidity_rh',
            'vision_defect_score', 'vision_contaminant_score',
            'co2_ppm', 'o2_percent', 'voc_ppm',
            'differential_pressure_bar', 'refrigerant_pressure_bar'
        ]
    }
    
    # Test input
    test_input = {
        'raw_data': {
            'temperature_c': 79.5,
            'pressure_bar': 15.2,
            'ph_level': 6.5,
            'flow_rate_lph': 1250,
            'line_id': 'Line_1',
            'batch_id': 'TEST_001'
        },
        'timestamp': '2024-02-07T14:30:00'
    }
    
    # Test prediction
    result = predict_fn(test_input, artifacts)
    print("\n" + "="*60)
    print("TEST RESULT:")
    print("="*60)
    print(json.dumps(result, indent=2))

    