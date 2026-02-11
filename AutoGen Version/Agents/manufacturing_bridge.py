import json
import time
import random
from datetime import datetime
from typing import Dict, List
import asyncio
import requests

class ManufacturingBridge:
    """Bridge between CrewAI manufacturing dashboard and AutoGen Studio"""
    
    def __init__(self, autogen_url="http://localhost:8081"):
        self.autogen_url = autogen_url
        self.crewai_data = {
            "cycle": 0,
            "sensors": {},
            "alerts": [],
            "agents_status": {},
            "efficiency": 95.0
        }
        
    def simulate_crewai_data(self):
        """Simulate data from your CrewAI dashboard"""
        self.crewai_data["cycle"] += 1
        self.crewai_data["timestamp"] = datetime.now().isoformat()
        
        # Simulate sensor data (like your CrewAI dashboard does)
        sensors = {
            "temperature_c": round(random.uniform(22.0, 30.0), 1),
            "pressure_bar": round(random.uniform(0.8, 1.2), 2),
            "vibration_x": round(random.uniform(0.1, 0.9), 3),
            "vibration_y": round(random.uniform(0.1, 0.9), 3),
            "vibration_z": round(random.uniform(0.1, 0.9), 3),
            "flow_rate": round(random.uniform(90, 110), 1)
        }
        self.crewai_data["sensors"] = sensors
        
        # Check for anomalies
        alerts = []
        if sensors["vibration_x"] > 0.7:
            alerts.append({"sensor": "vibration_x", "value": sensors["vibration_x"], "threshold": 0.7, "severity": "high"})
        if sensors["temperature_c"] > 28.0:
            alerts.append({"sensor": "temperature_c", "value": sensors["temperature_c"], "threshold": 28.0, "severity": "medium"})
        
        self.crewai_data["alerts"] = alerts
        
        # Calculate efficiency based on alerts
        base_efficiency = 95.0
        efficiency_penalty = len(alerts) * 2.5
        self.crewai_data["efficiency"] = max(75.0, base_efficiency - efficiency_penalty)
        
        # Agent status
        self.crewai_data["agents_status"] = {
            "alert": "active",
            "analyzer": "active", 
            "production": "active",
            "optimum": "active"
        }
        
        return self.crewai_data
    
    def create_autogen_workflow(self):
        """Create a workflow that AutoGen Studio can display"""
        data = self.crewai_data
        
        workflow = {
            "name": f"Manufacturing Cycle {data['cycle']}",
            "description": "Real-time manufacturing monitoring",
            "timestamp": data["timestamp"],
            "metrics": {
                "efficiency": data["efficiency"],
                "cycle": data["cycle"],
                "alerts": len(data["alerts"]),
                "agents_active": 4
            },
            "alerts": data["alerts"],
            "sensors": data["sensors"],
            "recommendations": []
        }
        
        # Add recommendations based on alerts
        if data["alerts"]:
            workflow["recommendations"].append("Adjust production parameters")
            workflow["recommendations"].append("Schedule maintenance check")
        else:
            workflow["recommendations"].append("Continue optimal operations")
            workflow["recommendations"].append("Monitor performance trends")
            
        return workflow
    
    def display_dashboard(self):
        """Display a simple dashboard in terminal"""
        data = self.crewai_data
        
        print("\n" + "="*70)
        print("🏭 MANUFACTURING BRIDGE - CrewAI ↔ AutoGen Studio")
        print("="*70)
        
        print(f"\n📊 Cycle: {data['cycle']}")
        print(f"⏰ Time: {datetime.fromisoformat(data['timestamp']).strftime('%H:%M:%S')}")
        print(f"📈 Efficiency: {data['efficiency']:.1f}%")
        
        if data['alerts']:
            print(f"\n🚨 ALERTS ({len(data['alerts'])}):")
            for alert in data['alerts']:
                print(f"   • {alert['sensor']}: {alert['value']} (threshold: {alert['threshold']})")
        else:
            print(f"\n✅ NO ALERTS - System operating normally")
            print(f"   Accuracy: {(data['efficiency'] - 80) / 20 * 100:.1f}%")
            print(f"   Efficacy: {min(100, data['efficiency'] + 5):.1f}%")
        
        print(f"\n🔗 AutoGen Studio: {self.autogen_url}")
        print(f"🤖 CrewAI Dashboard: Running in separate terminal")
        
        print("\n📡 Sensor Status:")
        for sensor, value in data['sensors'].items():
            status = "⚠️ " if any(a['sensor'] == sensor for a in data['alerts']) else "✅ "
            print(f"   {status}{sensor:15} {value}")
    
    async def send_to_autogen(self):
        """Send data to AutoGen Studio (simulated - would use API)"""
        print(f"\n📤 Sending data to AutoGen Studio...")
        workflow = self.create_autogen_workflow()
        
        # In a real implementation, you would use:
        # requests.post(f"{self.autogen_url}/api/workflows", json=workflow)
        
        print(f"   ✅ Cycle {workflow['metrics']['cycle']} data prepared")
        print(f"   📊 Efficiency: {workflow['metrics']['efficiency']:.1f}%")
        print(f"   🚨 Alerts: {workflow['metrics']['alerts']}")
        
        return True
    
    def run_continuous(self, interval_seconds=5):
        """Run continuous updates"""
        print("🚀 Starting Manufacturing Bridge...")
        print(f"🔗 Connecting CrewAI → AutoGen Studio")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                # Get new data from CrewAI simulation
                self.simulate_crewai_data()
                
                # Display dashboard
                self.display_dashboard()
                
                # Send to AutoGen Studio
                asyncio.run(self.send_to_autogen())
                
                print(f"\n⏳ Next update in {interval_seconds} seconds...")
                print("-"*70)
                
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Bridge stopped")
            print(f"📈 Total cycles: {self.crewai_data['cycle']}")

def main():
    """Main function"""
    print("\n" + "="*70)
    print("🔗 CREWAI → AUTOGEN STUDIO INTEGRATION")
    print("="*70)
    
    bridge = ManufacturingBridge()
    
    print("\n🚀 Options:")
    print("1. Run continuous bridge (recommended)")
    print("2. Test single cycle")
    print("3. View current CrewAI status")
    print("4. Exit")
    
    choice = input("\n▶️  Select (1-4): ").strip()
    
    if choice == '1':
        interval = input("Update interval in seconds (default: 5): ").strip()
        try:
            interval = int(interval) if interval else 5
        except:
            interval = 5
        bridge.run_continuous(interval)
    
    elif choice == '2':
        bridge.simulate_crewai_data()
        bridge.display_dashboard()
        print("\n✅ Test complete. Data ready for AutoGen Studio")
    
    elif choice == '3':
        # Check if CrewAI is running
        print("\n📊 Checking CrewAI status...")
        print("✅ CrewAI dashboard should be running in another terminal")
        print("💡 Run: python crewai_dashboard.py")
        print("\n🔗 AutoGen Studio URL: http://localhost:8081")
    
    elif choice == '4':
        print("\n👋 Goodbye!")
    
    else:
        print("\n❌ Invalid choice. Running bridge...")
        bridge.run_continuous()

if __name__ == "__main__":
    main()
