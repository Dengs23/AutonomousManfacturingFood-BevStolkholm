#!/usr/bin/env python3
"""
Simple AutoGen-CrewAI Integration Dashboard
No complex dependencies required
"""

import time
import json
import random
from datetime import datetime
import os

class SimpleDashboard:
    def __init__(self):
        self.sensors = self.generate_sensors()
        self.cycle = 0
        
    def generate_sensors(self):
        """Generate simulated sensor data"""
        sensors = {
            "temperature_c": round(random.uniform(22.0, 28.0), 1),
            "pressure_bar": round(random.uniform(0.9, 1.1), 2),
            "vibration_x": round(random.uniform(0.1, 0.8), 3),
            "vibration_y": round(random.uniform(0.1, 0.8), 3),
            "vibration_z": round(random.uniform(0.1, 0.8), 3),
            "ph_level": round(random.uniform(6.5, 7.5), 2),
            "flow_rate_lph": round(random.uniform(95, 105), 1)
        }
        return sensors
    
    def check_alerts(self):
        """Check for sensor alerts"""
        alerts = []
        for sensor, value in self.sensors.items():
            if "vibration" in sensor and value > 0.7:
                alerts.append(f"⚠️  High {sensor}: {value}")
            elif "temperature" in sensor and value > 27.0:
                alerts.append(f"🌡️  High {sensor}: {value}°C")
        return alerts
    
    def display_dashboard(self):
        """Display the dashboard"""
        print("\n" + "="*60)
        print("🏭 MANUFACTURING DASHBOARD")
        print("="*60)
        
        print(f"\n📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🔄 Cycle: {self.cycle}")
        
        print("\n📡 SENSOR STATUS:")
        for sensor, value in self.sensors.items():
            if "vibration" in sensor and value > 0.7:
                status = "🔴"
            elif "temperature" in sensor and value > 27.0:
                status = "🟡"
            else:
                status = "🟢"
            print(f"  {status} {sensor:15} {value}")
        
        alerts = self.check_alerts()
        if alerts:
            print("\n🚨 ALERTS:")
            for alert in alerts:
                print(f"  • {alert}")
        else:
            print("\n✅ All systems normal")
        
        print("\n🤖 AGENTS:")
        agents = ["Alert", "Analyzer", "Production", "Optimum"]
        for agent in agents:
            print(f"  • {agent} Agent: 🟢 Active")
    
    def simulate_cycle(self):
        """Simulate one manufacturing cycle"""
        self.cycle += 1
        self.sensors = self.generate_sensors()
        
        print(f"\n{'═'*50}")
        print(f"🔄 CYCLE {self.cycle}")
        print(f"{'═'*50}")
        
        print("\n1️⃣  Alert Agent: Scanning sensors...")
        time.sleep(0.5)
        
        alerts = self.check_alerts()
        if alerts:
            print("   🚨 Alerts detected!")
            for alert in alerts:
                print(f"   {alert}")
        else:
            print("   ✅ No alerts")
        
        print("\n2️⃣  Analyzer Agent: Analyzing...")
        time.sleep(0.5)
        print("   📊 Analysis complete")
        
        print("\n3️⃣  Production Agent: Adjusting...")
        time.sleep(0.5)
        print("   ⚙️  Adjustments applied")
        
        print("\n4️⃣  Optimum Agent: Optimizing...")
        time.sleep(0.5)
        print("   💡 Optimization complete")
        
        return True
    
    def run_interactive(self):
        """Run interactive mode"""
        print("🚀 Starting Manufacturing Dashboard...")
        print("Press Ctrl+C to exit\n")
        
        try:
            while True:
                self.simulate_cycle()
                self.display_dashboard()
                
                print("\nOptions:")
                print("  [n] Next cycle")
                print("  [s] Show sensors")
                print("  [q] Quit")
                
                choice = input("\n▶️  Your choice: ").strip().lower()
                
                if choice == 'q':
                    print("\n👋 Goodbye!")
                    break
                elif choice == 's':
                    print("\n📡 Current Sensor Values:")
                    print(json.dumps(self.sensors, indent=2))
                elif choice == 'n':
                    continue
                else:
                    print("Continuing to next cycle...")
                
                # Auto-continue after 2 seconds
                time.sleep(2)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Dashboard stopped")

def check_crewai():
    """Check if CrewAI is available"""
    try:
        import crewai
        return True
    except ImportError:
        return False

def check_autogen():
    """Check if AutoGen is available"""
    try:
        import autogen
        return True
    except ImportError:
        return False

def main():
    """Main function"""
    print("\n" + "="*60)
    print("🔧 DASHBOARD LAUNCHER")
    print("="*60)
    
    # Check what's available
    crewai_available = check_crewai()
    autogen_available = check_autogen()
    
    print(f"\n📦 CrewAI: {'✅ Installed' if crewai_available else '❌ Not installed'}")
    print(f"📦 AutoGen: {'✅ Installed' if autogen_available else '❌ Not installed'}")
    
    print("\n🚀 Options:")
    print("1. Run Simple Dashboard (always works)")
    print("2. Try CrewAI Dashboard")
    print("3. Check installations")
    print("4. Exit")
    
    try:
        choice = input("\n▶️  Select (1-4): ").strip()
        
        if choice == '1':
            dashboard = SimpleDashboard()
            dashboard.run_interactive()
        
        elif choice == '2':
            if crewai_available:
                print("\n🔗 Launching CrewAI Dashboard...")
                # Import your existing dashboard
                try:
                    import crewai_dashboard
                    print("✅ Success! Now run: python crewai_dashboard.py")
                except Exception as e:
                    print(f"❌ Error: {e}")
            else:
                print("\n❌ CrewAI not installed.")
                print("💡 Install with: pip install crewai")
        
        elif choice == '3':
            print("\n🔧 INSTALLATION GUIDE:")
            print("-"*40)
            print("To install CrewAI:")
            print("  pip install crewai")
            print("\nTo install AutoGen:")
            print("  pip install pyautogen")
            print("\nTo install AutoGen Studio:")
            print("  pip install autogenstudio")
            print("\nYour current directory:")
            print(f"  {os.getcwd()}")
            print("\nFiles available:")
            os.system("ls -la | grep -E '\.py$|\.txt$'")
        
        elif choice == '4':
            print("\n👋 Goodbye!")
        
        else:
            print("\n❌ Invalid choice. Running simple dashboard...")
            dashboard = SimpleDashboard()
            dashboard.run_interactive()
    
    except KeyboardInterrupt:
        print("\n\n👋 Exiting...")

if __name__ == "__main__":
    main()
