import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer
from kafka_config import KafkaConfig
import threading

class StockholmManufacturingDataProducer:
    def __init__(self):
        try:
            self.producer = KafkaProducer(**KafkaConfig.get_producer_config())
            print("✅ Kafka producer connected successfully")
        except Exception as e:
            print(f"❌ Kafka connection error: {e}")
            print("⚠️  Make sure Kafka is running: brew services start kafka")
            self.producer = None
        
        self.running = True
        self.cycle_count = 0
        self.base_temperature = 22.0  # Stockholm average
        
        # Swedish manufacturing sites in Stockholm region
        self.swedish_factories = [
            "Stockholm_Brewery_AB",
            "Södermalm_Food_Processing", 
            "Kista_Beverage_Inc",
            "Solna_Dairy_Plant",
            "Hammarby_Canning_Factory"
        ]
        
        # Swedish weather patterns
        self.stockholm_weather = [
            "Clear", "Partly Cloudy", "Cloudy", "Light Rain", 
            "Snow", "Fog", "Windy", "Overcast"
        ]
        
        print(f"🏭 Swedish Manufacturing Simulator Initialized")
        print(f"🏢 Factories: {', '.join(self.swedish_factories)}")
        print(f"🌤️  Weather patterns: {len(self.stockholm_weather)} variations")
    
    def generate_sensor_data(self):
        """Generate realistic Swedish manufacturing sensor data"""
        current_time = datetime.now()
        current_hour = current_time.hour
        
        # Time-based production patterns
        if 6 <= current_hour < 14:   # Morning shift
            production_factor = 1.2
            shift = "Morning"
        elif 14 <= current_hour < 22: # Afternoon shift
            production_factor = 1.0
            shift = "Afternoon"
        else:                         # Night shift
            production_factor = 0.8
            shift = "Night"
        
        sensors = {
            # Core process sensors
            "temperature_c": round(22.0 + random.uniform(-2, 4), 1),
            "pressure_bar": round(1.01 + random.uniform(-0.08, 0.08), 3),
            "ph_level": round(random.uniform(6.5, 7.5), 2),
            "flow_rate_lph": round(random.uniform(800, 3000) * production_factor, 0),
            
            # Vibration monitoring
            "vibration_x": round(random.uniform(0.05, 0.75), 3),
            "vibration_y": round(random.uniform(0.05, 0.75), 3),
            "vibration_z": round(random.uniform(0.05, 0.75), 3),
            
            # Food & beverage quality
            "brix_level": round(random.uniform(8, 22), 1),      # Sugar content
            "alcohol_percent": round(random.uniform(3.5, 6.0), 1),
            "turbidity_ntu": round(random.uniform(0.1, 3.0), 2),  # Clarity
            "color_ebc": round(random.uniform(5, 40), 1),       # Color units
            
            # Environmental sensors
            "co2_ppm": round(random.uniform(350, 850), 0),
            "o2_percent": round(random.uniform(20.5, 21.5), 2),
            "humidity_rh": round(random.uniform(40, 80), 1),
            
            # Efficiency metrics
            "energy_consumption_kwh": round(random.uniform(400, 1200) * production_factor, 0),
            "water_usage_l": round(random.uniform(800, 2500) * production_factor, 0),
            "production_rate_units_h": round(random.uniform(800, 3000) * production_factor, 0),
            "packaging_speed_units_min": round(random.uniform(50, 200) * production_factor, 0),
            
            # Safety sensors
            "ultrasound_leak_db": round(random.uniform(20, 65), 1),
            "acoustic_emission": round(random.uniform(30, 75), 1),
            "differential_pressure": round(random.uniform(-0.1, 0.1), 3),
            
            # Metadata
            "timestamp": current_time.isoformat(),
            "factory_id": random.choice(self.swedish_factories),
            "shift": shift,
            "stockholm_weather": random.choice(self.stockholm_weather),
            "production_factor": round(production_factor, 2),
            "batch_id": f"BATCH-{current_time.strftime('%Y%m%d')}-{random.randint(1000, 9999)}",
            "quality_inspection": random.choice(["PASS", "PASS", "PASS", "PASS", "HOLD"])
        }
        return sensors
    
    def detect_anomalies(self, sensor_data):
        """Detect anomalies based on Swedish manufacturing standards"""
        alerts = []
        
        # Swedish manufacturing thresholds
        thresholds = {
            "temperature_c": {"min": 18, "max": 28, "unit": "°C"},
            "pressure_bar": {"min": 0.95, "max": 1.05, "unit": "bar"},
            "vibration_x": {"min": 0, "max": 0.7, "unit": "g"},
            "vibration_y": {"min": 0, "max": 0.7, "unit": "g"},
            "vibration_z": {"min": 0, "max": 0.7, "unit": "g"},
            "ph_level": {"min": 6.0, "max": 8.0, "unit": "pH"},
            "turbidity_ntu": {"min": 0, "max": 5.0, "unit": "NTU"},
            "co2_ppm": {"min": 0, "max": 1000, "unit": "ppm"}
        }
        
        for sensor, value in sensor_data.items():
            if sensor in thresholds:
                min_val = thresholds[sensor]["min"]
                max_val = thresholds[sensor]["max"]
                unit = thresholds[sensor]["unit"]
                
                if value < min_val:
                    severity = "HIGH" if sensor.startswith("vibration") else "MEDIUM"
                    alerts.append({
                        "sensor": sensor,
                        "value": value,
                        "threshold": f"Min: {min_val}{unit}",
                        "message": f"LOW {sensor.replace('_', ' ').title()}: {value}{unit} < {min_val}{unit}",
                        "severity": severity.lower(),
                        "timestamp": datetime.now().isoformat(),
                        "factory": sensor_data.get("factory_id", "Unknown"),
                        "recommendation": "Increase temperature" if "temperature" in sensor else "Check calibration"
                    })
                elif value > max_val:
                    severity = "HIGH" if sensor.startswith("vibration") else "MEDIUM"
                    alerts.append({
                        "sensor": sensor,
                        "value": value,
                        "threshold": f"Max: {max_val}{unit}",
                        "message": f"HIGH {sensor.replace('_', ' ').title()}: {value}{unit} > {max_val}{unit}",
                        "severity": severity.lower(),
                        "timestamp": datetime.now().isoformat(),
                        "factory": sensor_data.get("factory_id", "Unknown"),
                        "recommendation": "Cool system" if "temperature" in sensor else "Reduce load"
                    })
        
        return alerts
    
    def generate_swedish_agent_data(self):
        """Generate Swedish manufacturing agent data"""
        agents = [
            {
                "id": "alert_agent",
                "name": "Stockholm Safety Agent", 
                "status": random.choice(["active", "active", "active", "monitoring"]),
                "last_heartbeat": datetime.now().isoformat(),
                "language": "Swedish",
                "location": "Stockholm",
                "responsibility": "Safety monitoring & alerts"
            },
            {
                "id": "quality_agent",
                "name": "Swedish Quality Agent",
                "status": random.choice(["active", "active", "active", "inspecting"]),
                "last_heartbeat": datetime.now().isoformat(),
                "language": "Swedish",
                "location": "Gothenburg",
                "responsibility": "Quality control & standards"
            },
            {
                "id": "production_agent",
                "name": "Production Efficiency Agent",
                "status": random.choice(["active", "active", "optimizing", "active"]),
                "last_heartbeat": datetime.now().isoformat(),
                "language": "Swedish/English",
                "location": "Malmo",
                "responsibility": "Production optimization"
            },
            {
                "id": "sustainability_agent",
                "name": "Sustainability Agent",
                "status": random.choice(["active", "active", "active", "analyzing"]),
                "last_heartbeat": datetime.now().isoformat(),
                "language": "Swedish",
                "location": "Uppsala",
                "responsibility": "Energy & resource efficiency"
            }
        ]
        return agents
    
    def produce_cycle(self):
        """Produce a manufacturing cycle with Swedish data"""
        if not self.producer:
            print("⚠️  Kafka producer not available. Skipping cycle.")
            return None
        
        self.cycle_count += 1
        sensor_data = self.generate_sensor_data()
        alerts = self.detect_anomalies(sensor_data)
        
        # Calculate Swedish efficiency metrics
        production_factor = sensor_data.get("production_factor", 1.0)
        quality_status = sensor_data.get("quality_inspection", "PASS")
        
        cycle_data = {
            "cycle_id": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data,
            "alerts": alerts,
            "alert_count": len(alerts),
            "status": "ALERT" if alerts else "NORMAL",
            "quality_status": quality_status,
            "system_metrics": {
                "uptime": round(99.5 + random.uniform(-0.5, 0.5), 1),
                "efficiency": round(94.0 + random.uniform(-3, 3) + (production_factor - 1) * 5, 1),
                "quality_score": round(98.0 + random.uniform(-2, 2), 1),
                "sustainability": round(92.0 + random.uniform(-4, 4), 1),
                "energy_efficiency": round(85.0 + random.uniform(-5, 5), 1),
                "oee": round(82.0 + random.uniform(-8, 8), 1)  # Overall Equipment Effectiveness
            },
            "swedish_context": {
                "factory": sensor_data.get("factory_id"),
                "shift": sensor_data.get("shift"),
                "weather": sensor_data.get("stockholm_weather"),
                "production_factor": production_factor,
                "batch_id": sensor_data.get("batch_id"),
                "region": "Stockholm",
                "country": "Sweden"
            }
        }
        
        # Send to Kafka topics
        try:
            self.producer.send(KafkaConfig.TOPIC_SENSOR_DATA, value=sensor_data)
            
            if alerts:
                self.producer.send(KafkaConfig.TOPIC_ALERTS, 
                                 value={"cycle_id": self.cycle_count, "alerts": alerts})
            
            self.producer.send(KafkaConfig.TOPIC_SYSTEM_STATUS, value=cycle_data)
            
            agents = self.generate_swedish_agent_data()
            self.producer.send(KafkaConfig.TOPIC_AGENT_EVENTS,
                             value={"agents": agents, "timestamp": datetime.now().isoformat()})
            
            self.producer.flush()
            
            # Color-coded console output
            if alerts:
                print(f"\033[91m⚠️  Cycle #{self.cycle_count} | {sensor_data['factory_id']} | {len(alerts)} alerts | {sensor_data['stockholm_weather']}\033[0m")
            else:
                print(f"\033[92m✓ Cycle #{self.cycle_count} | {sensor_data['factory_id']} | Normal | {sensor_data['stockholm_weather']}\033[0m")
            
        except Exception as e:
            print(f"\033[93m⚠️ Kafka Error: {e}\033[0m")
        
        return cycle_data
    
    def start_production(self, interval=5):
        """Start continuous Swedish manufacturing simulation"""
        if not self.producer:
            print("\033[93m❌ Cannot start production: Kafka not connected\033[0m")
            print("\033[93m💡 Start Kafka: brew services start kafka\033[0m")
            return
        
        def produce_loop():
            while self.running:
                self.produce_cycle()
                time.sleep(interval)
        
        thread = threading.Thread(target=produce_loop, daemon=True)
        thread.start()
        print(f"\033[94m🏭 Started Swedish Manufacturing Simulation ({interval}s interval)\033[0m")
        print("\033[94m📊 Real-time data streaming to Kafka...\033[0m")
    
    def stop(self):
        """Stop the producer"""
        self.running = False
        if self.producer:
            self.producer.close()
        print("\033[93m🛑 Swedish manufacturing simulation stopped\033[0m")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Swedish Manufacturing Kafka Producer')
    parser.add_argument('--interval', type=int, default=5, help='Production interval in seconds (default: 5)')
    parser.add_argument('--cycles', type=int, default=0, help='Number of cycles to produce (0 = infinite)')
    parser.add_argument('--factory', type=str, help='Specific factory to simulate')
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🏭 SWEDISH MANUFACTURING KAFKA PRODUCER")
    print("="*60)
    
    producer = StockholmManufacturingDataProducer()
    
    if args.factory:
        producer.swedish_factories = [args.factory]
        print(f"🏢 Simulating single factory: {args.factory}")
    
    try:
        if args.cycles > 0:
            print(f"🔄 Producing {args.cycles} cycles...")
            for i in range(args.cycles):
                producer.produce_cycle()
                time.sleep(args.interval)
        else:
            producer.start_production(args.interval)
            print("🔄 Press Ctrl+C to stop simulation")
            # Keep running until interrupted
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\n\033[93m🛑 Stopping producer...\033[0m")
    finally:
        producer.stop()
        print("="*60 + "\n")
