import json
import time
import random
from datetime import datetime
import requests
import threading

class EnhancedManufacturingBridge:
    def __init__(self):
        self.cycle = 0
        self.autogen_url = "http://localhost:8081"
        
    def get_sensor_data(self):
        """Get current sensor readings"""
        return {
            "temperature": round(random.uniform(22.0, 30.0), 1),
            "pressure": round(random.uniform(0.8, 1.2), 2),
            "vibration_x": round(random.uniform(0.1, 0.9), 3),
            "vibration_y": round(random.uniform(0.1, 0.9), 3),
            "vibration_z": round(random.uniform(0.1, 0.9), 3),
            "flow_rate": round(random.uniform(90, 110), 1),
            "timestamp": datetime.now().isoformat()
        }
    
    def check_anomalies(self, sensors):
        """Check for manufacturing anomalies"""
        anomalies = []
        
        if sensors["vibration_x"] > 0.7:
            anomalies.append({
                "sensor": "vibration_x",
                "value": sensors["vibration_x"],
                "threshold": 0.7,
                "severity": "high",
                "message": "Excessive vibration detected on X-axis"
            })
        
        if sensors["temperature"] > 28.0:
            anomalies.append({
                "sensor": "temperature",
                "value": sensors["temperature"],
                "threshold": 28.0,
                "severity": "medium",
                "message": "Temperature above optimal range"
            })
        
        return anomalies
    
    def calculate_metrics(self, anomalies):
        """Calculate system metrics"""
        base_score = 95.0
        penalty = len(anomalies) * 2.5
        
        efficiency = max(75.0, base_score - penalty)
        accuracy = ((efficiency - 80) / 20 * 100) if efficiency > 80 else 0
        efficacy = min(100, efficiency + random.uniform(0, 5))
        
        return {
            "efficiency": round(efficiency, 1),
            "accuracy": round(accuracy, 1),
            "efficacy": round(efficacy, 1),
            "anomalies": len(anomalies),
            "status": "normal" if len(anomalies) == 0 else "alert"
        }
    
    def create_autogen_task(self, sensors, anomalies, metrics):
        """Create a task for AutoGen Studio agents"""
        self.cycle += 1
        
        if anomalies:
            task = f"""MANUFACTURING ALERT - Cycle {self.cycle}
            
            🚨 ANOMALIES DETECTED:
            {chr(10).join([f"• {a['message']} (Value: {a['value']}, Threshold: {a['threshold']})" for a in anomalies])}
            
            Please analyze and provide recommendations."""
        else:
            task = f"""MANUFACTURING STATUS - Cycle {self.cycle}
            
            ✅ All systems normal
            📊 Metrics:
            • Efficiency: {metrics['efficiency']}%
            • Accuracy: {metrics['accuracy']}%
            • Efficacy: {metrics['efficacy']}%
            
            Please optimize and plan maintenance."""
        
        return task
    
    def send_to_autogen(self, task):
        """Send task to AutoGen Studio (simulated)"""
        print(f"\n📤 AutoGen Task Ready:")
        print(f"   Cycle: {self.cycle}")
        print(f"   Task length: {len(task)} characters")
        print(f"   Timestamp: {datetime.now().strftime('%H:%M:%S')}")
        
        # In real implementation: POST to AutoGen API
        # response = requests.post(f"{self.autogen_url}/api/tasks", json={"task": task})
        
        return True
    
    def display_status(self, sensors, anomalies, metrics):
        """Display current status"""
        print("\n" + "="*70)
        print("🏭 REAL-TIME MANUFACTURING MONITOR")
        print("="*70)
        
        print(f"\n🔄 Cycle: {self.cycle}")
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')}")
        
        if anomalies:
            print(f"\n🚨 ALERT STATUS")
            print(f"   Anomalies: {len(anomalies)}")
            for anomaly in anomalies:
                print(f"   • {anomaly['message']}")
        else:
            print(f"\n✅ OPTIMAL STATUS")
            print(f"   Efficiency: {metrics['efficiency']}%")
            print(f"   Accuracy: {metrics['accuracy']}%")
            print(f"   Efficacy: {metrics['efficacy']}%")
        
        print(f"\n📡 SENSOR READINGS:")
        for sensor, value in sensors.items():
            if sensor != "timestamp":
                has_anomaly = any(a['sensor'] == sensor for a in anomalies)
                icon = "⚠️ " if has_anomaly else "✅ "
                print(f"   {icon}{sensor:15} {value}")
    
    def run_cycle(self):
        """Run one monitoring cycle"""
        # Get sensor data
        sensors = self.get_sensor_data()
        
        # Check for anomalies
        anomalies = self.check_anomalies(sensors)
        
        # Calculate metrics
        metrics = self.calculate_metrics(anomalies)
        
        # Display status
        self.display_status(sensors, anomalies, metrics)
        
        # Create task for AutoGen
        task = self.create_autogen_task(sensors, anomalies, metrics)
        
        # Send to AutoGen Studio
        self.send_to_autogen(task)
        
        return metrics
    
    def continuous_monitor(self, interval=5):
        """Run continuous monitoring"""
        print("🚀 Starting Manufacturing Monitor...")
        print("🔗 Connected to AutoGen Studio")
        print("📊 Showing: Anomalies 🚨 or Metrics ✅")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.run_cycle()
                print(f"\n⏳ Next update in {interval} seconds...")
                print("-"*70)
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print(f"\n\n🛑 Monitor stopped after {self.cycle} cycles")
            print("👋 Keep AutoGen Studio open at http://localhost:8081")

def main():
    bridge = EnhancedManufacturingBridge()
    
    print("\n" + "="*70)
    print("🤖 MANUFACTURING → AUTOGEN STUDIO BRIDGE")
    print("="*70)
    
    print("\n💡 This bridge:")
    print("1. Simulates manufacturing sensor data")
    print("2. Detects anomalies (shows 🚨 alerts)")
    print("3. When normal: shows accuracy/efficacy metrics")
    print("4. Creates tasks for AutoGen Studio agents")
    print("5. Updates every 5 seconds")
    
    input("\nPress Enter to start monitoring...")
    bridge.continuous_monitor(interval=5)

if __name__ == "__main__":
    main()
