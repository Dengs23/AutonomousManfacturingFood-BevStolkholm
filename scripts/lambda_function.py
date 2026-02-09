
import json
import boto3
import pandas as pd
from datetime import datetime

# Simulated model (replace with SageMaker endpoint call)
def predict_failure(sensor_data):
    """Predict equipment failure based on sensor data"""
    # This would call your SageMaker endpoint
    # For simulation, we'll use a simple rule-based approach
    risk_score = 0
    
    if sensor_data.get('temperature', 72) > 78:
        risk_score += 0.4
    if sensor_data.get('pressure', 3.5) > 4.0:
        risk_score += 0.3
    if sensor_data.get('vibration', 4.0) > 6.0:
        risk_score += 0.3
    
    prediction = 1 if risk_score > 0.6 else 0
    
    return {
        'prediction': prediction,
        'risk_score': risk_score,
        'confidence': 0.95 if prediction else 0.85,
        'timestamp': datetime.now().isoformat(),
        'recommendation': 'Schedule maintenance' if prediction else 'Continue monitoring'
    }

def lambda_handler(event, context):
    """Process incoming sensor data"""
    print(f"Received event: {json.dumps(event)}")
    
    # Extract sensor data
    sensor_data = event.get('sensor_data', {})
    
    # Make prediction
    prediction = predict_failure(sensor_data)
    
    # If high risk, send alert
    if prediction['prediction'] == 1:
        send_alert(prediction, sensor_data)
    
    # Log to CloudWatch
    log_to_cloudwatch(prediction, sensor_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps(prediction)
    }

def send_alert(prediction, sensor_data):
    """Send alert via SNS"""
    sns = boto3.client('sns')
    
    message = f"""
    🚨 PREDICTIVE MAINTENANCE ALERT 🚨
    
    Equipment failure predicted with {prediction['confidence']:.1%} confidence.
    
    Sensor Readings:
    - Temperature: {sensor_data.get('temperature', 'N/A')}°C
    - Pressure: {sensor_data.get('pressure', 'N/A')} bar
    - Vibration: {sensor_data.get('vibration', 'N/A')} mm/s
    
    Risk Score: {prediction['risk_score']:.2f}
    Recommendation: {prediction['recommendation']}
    
    Timestamp: {prediction['timestamp']}
    """
    
    try:
        sns.publish(
            TopicArn='arn:aws:sns:eu-north-1:976792586723:ManufacturingAlerts',
            Subject='Predictive Maintenance Alert',
            Message=message
        )
        print("Alert sent via SNS")
    except Exception as e:
        print(f"Failed to send alert: {e}")

def log_to_cloudwatch(prediction, sensor_data):
    """Log prediction to CloudWatch metrics"""
    cloudwatch = boto3.client('cloudwatch')
    
    cloudwatch.put_metric_data(
        Namespace='Manufacturing',
        MetricData=[
            {
                'MetricName': 'FailureRisk',
                'Value': prediction['risk_score'],
                'Unit': 'None',
                'Dimensions': [
                    {'Name': 'Line', 'Value': 'Line_1'},
                    {'Name': 'Model', 'Value': 'PredictiveMaintenance_v1'}
                ]
            }
        ]
    )
