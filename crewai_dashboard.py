import time
import json
import random
from datetime import datetime
import sys

try:
    from crewai import Agent, Task, Crew, Process
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "crewai"])
    from crewai import Agent, Task, Crew, Process

class AutonomousManufacturingDashboard:
    
    def __init__(self):
        self.agents = {}
        self.crew = None
        self.cycle_count = 0
        self.history = []
        
        self.sensor_names = [
            "temperature_c", "pressure_bar", "ph_level", "flow_rate_lph",
            "vibration_x", "vibration_y", "vibration_z", "ultrasound_leak_db",
            "acoustic_emission", "orp_redox_mv", "humidity_rh",
            "vision_defect_score", "vision_contaminant_score", "co2_ppm",
            "o2_percent", "voc_ppm", "differential_pressure_bar"
        ]
        
        self.current_sensors = self._generate_sensor_data()
        self.setup_crew()
    
    def _generate_sensor_data(self):
        sensors = {}
        for sensor in self.sensor_names:
            if "vibration" in sensor:
                sensors[sensor] = round(random.uniform(0.1, 0.8), 3)
            elif "temperature" in sensor:
                sensors[sensor] = round(random.uniform(22.0, 28.0), 1)
            elif "pressure" in sensor:
                sensors[sensor] = round(random.uniform(0.9, 1.1), 2)
            elif "vision" in sensor:
                sensors[sensor] = round(random.uniform(0.0, 0.3), 3)
            else:
                sensors[sensor] = round(random.uniform(0, 100), 2)
        return sensors
    
    def setup_crew(self):
        
        self.agents["alert"] = Agent(
            role="Alert Detection Agent",
            goal="Monitor 17 sensors and detect manufacturing anomalies",
            backstory="Expert in sensor pattern recognition with 10+ years in food manufacturing.",
            verbose=False,
            allow_delegation=False
        )
        
        self.agents["analyzer"] = Agent(
            role="Root Cause Analyzer Agent",
            goal="Analyze alerts to determine root causes and impacts",
            backstory="Diagnostic engineer specializing in manufacturing failure analysis.",
            verbose=False,
            allow_delegation=True
        )
        
        self.agents["production"] = Agent(
            role="Production Line Manager Agent",
            goal="Adjust production parameters to maintain quality and output",
            backstory="Production supervisor with expertise in real-time process optimization.",
            verbose=False,
            allow_delegation=True
        )
        
        self.agents["optimum"] = Agent(
            role="Optimization Solution Agent",
            goal="Provide optimal long-term solutions for manufacturing issues",
            backstory="Optimization algorithm expert focusing on efficiency and reliability.",
            verbose=False,
            allow_delegation=False
        )
        
        alert_task = Task(
            description=f"Monitor these sensor values: {json.dumps(self.current_sensors, indent=2)}. Identify any values outside normal ranges.",
            agent=self.agents["alert"],
            expected_output="Alert report with specific sensor issues and severity"
        )
        
        analyzer_task = Task(
            description="Analyze the alert to determine root cause. What component is failing? What's the failure probability?",
            agent=self.agents["analyzer"],
            expected_output="Root cause analysis with confidence percentage"
        )
        
        production_task = Task(
            description="Based on the analysis, what immediate production adjustments should be made?",
            agent=self.agents["production"],
            expected_output="Immediate action plan with specific parameter changes"
        )
        
        optimum_task = Task(
            description="What is the optimal long-term solution? When should maintenance be scheduled?",
            agent=self.agents["optimum"],
            expected_output="Optimized solution with timeline and expected benefits"
        )
        
        self.crew = Crew(
            agents=[self.agents["alert"], self.agents["analyzer"], 
                   self.agents["production"], self.agents["optimum"]],
            tasks=[alert_task, analyzer_task, production_task, optimum_task],
            process=Process.sequential,
            verbose=False,
            memory=True
        )
    
    def simulate_agent_workflow(self):
        
        self.cycle_count += 1
        self.current_sensors = self._generate_sensor_data()
        
        print(f"\n{'═'*70}")
        print(f"🏭 CYCLE #{self.cycle_count} - {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'═'*70}")
        
        print("\n🤖 [1/4] ALERT AGENT: Monitoring sensors...")
        time.sleep(1)
        
        alert_found = False
        alert_details = []
        
        for sensor, value in self.current_sensors.items():
            if "vibration" in sensor and value > 0.7:
                alert_found = True
                alert_details.append(f"⚠️ {sensor}: {value:.3f} (threshold: 0.5)")
            elif "temperature" in sensor and value > 27.0:
                alert_found = True
                alert_details.append(f"🌡️ {sensor}: {value:.1f}°C (threshold: 26.0°C)")
        
        if alert_found:
            print("   🚨 ALERT DETECTED!")
            for alert in alert_details:
                print(f"   {alert}")
            alert_message = f"Cycle {self.cycle_count}: {len(alert_details)} alerts"
        else:
            print("   ✅ All sensors normal")
            alert_message = "No alerts - system normal"
        
        print("\n🔍 [2/4] ANALYZER AGENT: Investigating root cause...")
        time.sleep(1.5)
        
        if alert_found:
            causes = [
                "Bearing wear in motor assembly",
                "Lubrication deficiency", 
                "Misalignment in drive shaft",
                "Electrical fluctuation",
                "Cooling system inefficiency"
            ]
            cause = random.choice(causes)
            confidence = random.randint(75, 95)
            print(f"   📋 Root Cause: {cause}")
            print(f"   📊 Confidence: {confidence}%")
            analysis_message = f"{cause} ({confidence}% confidence)"
        else:
            print("   ✅ No issues found for analysis")
            analysis_message = "No analysis needed"
        
        print("\n🏭 [3/4] PRODUCTION AGENT: Making adjustments...")
        time.sleep(1)
        
        if alert_found:
            adjustments = [
                "Reduce line speed by 10%",
                "Increase cooling flow by 15%",
                "Adjust pressure settings",
                "Temporary vibration dampening",
                "Increase monitoring frequency"
            ]
            adjustment = random.choice(adjustments)
            print(f"   🔧 Adjustment: {adjustment}")
            production_message = adjustment
        else:
            print("   ✅ Maintaining optimal parameters")
            production_message = "No adjustments needed"
        
        print("\n💡 [4/4] OPTIMUM AGENT: Calculating optimal solution...")
        time.sleep(1.5)
        
        if alert_found:
            solutions = [
                "Schedule maintenance: Thursday 2 PM",
                "Replace bearing assembly next week",
                "Upgrade cooling system in Q2",
                "Implement predictive maintenance algorithm",
                "Order spare parts for preventive replacement"
            ]
            solution = random.choice(solutions)
            benefit = random.randint(30, 80)
            print(f"   ✅ Solution: {solution}")
            print(f"   📈 Expected improvement: {benefit}% failure reduction")
            optimum_message = f"{solution} ({benefit}% improvement)"
        else:
            print("   ✅ System operating at optimum efficiency")
            optimum_message = "Continue current operations"
        
        cycle_data = {
            "cycle": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "alert": alert_message,
            "analysis": analysis_message,
            "production": production_message,
            "optimum": optimum_message,
            "sensors": self.current_sensors
        }
        self.history.append(cycle_data)
        
        return cycle_data
    
    def display_dashboard(self):
        
        print("\n" + "█"*70)
        print("          🏭 AUTONOMOUS MANUFACTURING DASHBOARD")
        print("          📍 Stockholm Food & Beverage System")
        print("█"*70)
        
        print("\n🤖 AGENT WORKFLOW STATUS:")
        print("  ┌─────────────────────────────────────────────────────┐")
        print("  │   Alert → Analyzer → Production → Optimum           │")
        print("  │   🟢 ACTIVE      🟢 ACTIVE      🟢 ACTIVE      🟢 ACTIVE │")
        print("  └─────────────────────────────────────────────────────┘")
        
        if self.history:
            latest = self.history[-1]
            print(f"\n📊 CURRENT CYCLE #{latest['cycle']}:")
            print(f"  🕒 Time: {datetime.fromisoformat(latest['timestamp']).strftime('%H:%M:%S')}")
            print(f"  🚨 Alert: {latest['alert']}")
            print(f"  🔍 Analysis: {latest['analysis']}")
            print(f"  🏭 Production: {latest['production']}")
            print(f"  💡 Optimum: {latest['optimum']}")
        
        print("\n📡 CRITICAL SENSORS:")
        critical = ["vibration_x", "vibration_y", "vibration_z", "temperature_c", "pressure_bar"]
        for sensor in critical:
            value = self.current_sensors.get(sensor, 0)
            if "vibration" in sensor:
                status = "⚠️ " if value > 0.7 else "✅ "
            elif "temperature" in sensor:
                status = "🌡️ " if value > 27.0 else "✅ "
            else:
                status = "📊 "
            print(f"  {status}{sensor:25} {value:.3f}")
        
        print(f"\n📈 SYSTEM HISTORY:")
        print(f"  Total cycles: {self.cycle_count}")
        print(f"  Alerts detected: {sum(1 for h in self.history if 'alert' in h['alert'].lower())}")
        print(f"  Maintenance scheduled: {sum(1 for h in self.history if 'schedule' in h['optimum'].lower())}")
        
        print(f"\n{'═'*70}")
    
    def run_continuous(self, interval_seconds=10):
        
        print("🚀 Starting Autonomous Manufacturing Dashboard...")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                self.simulate_agent_workflow()
                self.display_dashboard()
                print(f"⏳ Next cycle in {interval_seconds} seconds...")
                time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            print("\n\n🛑 Dashboard stopped.")
            print(f"📊 Total cycles run: {self.cycle_count}")
            print("👋 Goodbye!")

if __name__ == "__main__":
    dashboard = AutonomousManufacturingDashboard()
    
    print("\n" + "="*60)
    print("DEMO: Single Cycle Workflow")
    print("="*60)
    dashboard.simulate_agent_workflow()
    dashboard.display_dashboard()
    
    response = input("\n▶️  Run in continuous mode? (y/n): ").strip().lower()
    if response == 'y':
        interval = input("   Enter update interval in seconds (default: 10): ").strip()
        try:
            interval = int(interval) if interval else 10
        except:
            interval = 10
        
        dashboard.run_continuous(interval_seconds=interval)
    else:
        print("\n✅ Demo complete. Run again for more cycles.")
