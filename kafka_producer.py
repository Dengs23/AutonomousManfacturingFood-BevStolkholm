# kafka_producer.py - Kafka Data Producer
import json
import random
import time
from datetime import datetime
from kafka import KafkaProducer
from kafka_config import KafkaConfig
import threading

class ManufacturingDataProducer:
    def __init__(self):
        self.producer = KafkaProducer(**KafkaConfig.get_producer_config())
        self.running = True
        self.cycle_count = 0
        
    def generate_sensor_data(self):
        """Generate simulated sensor data"""
        sensors = {}
        sensor_names = [
            "temperature_c", "pressure_bar", "ph_level", "flow_rate_lph",
            "vibration_x", "vibration_y", "vibration_z", "ultrasound_leak_db",
            "acoustic_emission", "orp_redox_mv", "humidity_rh",
            "vision_defect_score", "vision_contaminant_score", "co2_ppm",
            "o2_percent", "voc_ppm", "differential_pressure_bar"
        ]
        
        for sensor in sensor_names:
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
    
    def generate_agent_data(self):
        """Generate agent status data"""
        agents = [
            {"id": "alert_agent", "name": "Alert Agent", "status": "active", 
             "last_heartbeat": datetime.now().isoformat()},
            {"id": "analyzer_agent", "name": "Analyzer Agent", "status": "active",
             "last_heartbeat": datetime.now().isoformat()},
            {"id": "production_agent", "name": "Production Agent", "status": "active",
             "last_heartbeat": datetime.now().isoformat()},
            {"id": "optimum_agent", "name": "Optimum Agent", "status": "active",
             "last_heartbeat": datetime.now().isoformat()}
        ]
        return agents
    
    def produce_cycle(self):
        """Produce a complete manufacturing cycle"""
        self.cycle_count += 1
        sensor_data = self.generate_sensor_data()
        
        # Detect alerts
        alerts = []
        for sensor, value in sensor_data.items():
            if "vibration" in sensor and value > 0.7:
                alerts.append({
                    "sensor": sensor,
                    "value": value,
                    "threshold": 0.7,
                    "message": f"High vibration detected: {sensor} = {value:.3f}",
                    "severity": "high",
                    "timestamp": datetime.now().isoformat()
                })
            elif "temperature" in sensor and value > 27.0:
                alerts.append({
                    "sensor": sensor,
                    "value": value,
                    "threshold": 27.0,
                    "message": f"High temperature: {sensor} = {value:.1f}°C",
                    "severity": "medium",
                    "timestamp": datetime.now().isoformat()
                })
        
        # Prepare cycle data
        cycle_data = {
            "cycle_id": self.cycle_count,
            "timestamp": datetime.now().isoformat(),
            "sensor_data": sensor_data,
            "alerts": alerts,
            "alert_count": len(alerts),
            "status": "ALERT" if alerts else "NORMAL",
            "system_metrics": {
                "uptime": round(random.uniform(99.0, 100.0), 1),
                "efficiency": round(random.uniform(94.0, 98.0), 1),
                "quality": round(random.uniform(97.0, 99.5), 1)
            }
        }
        
        # Send to Kafka topics
        try:
            # Send sensor data
            self.producer.send(
                KafkaConfig.TOPIC_SENSOR_DATA,
                value=sensor_data
            )
            
            # Send alerts if any
            if alerts:
                self.producer.send(
                    KafkaConfig.TOPIC_ALERTS,
                    value={"cycle_id": self.cycle_count, "alerts": alerts}
                )
            
            # Send complete cycle data
            self.producer.send(
                KafkaConfig.TOPIC_SYSTEM_STATUS,
                value=cycle_data
            )
            
            # Send agent status
            agents = self.generate_agent_data()
            self.producer.send(
                KafkaConfig.TOPIC_AGENT_EVENTS,
                value={"agents": agents, "timestamp": datetime.now().isoformat()}
            )
            
            self.producer.flush()
            print(f"Produced cycle #{self.cycle_count} with {len(alerts)} alerts")
            
        except Exception as e:
            print(f"Error producing to Kafka: {e}")
        
        return cycle_data
    
    def start_production(self, interval=5):
        """Start continuous production simulation"""
        def produce_loop():
            while self.running:
                self.produce_cycle()
                time.sleep(interval)
        
        thread = threading.Thread(target=produce_loop, daemon=True)
        thread.start()
        print(f"Started production simulation with {interval}s interval")
    
    def stop(self):
        """Stop the producer"""
        self.running = False
        self.producer.close()

# Standalone producer script
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Manufacturing Kafka Producer')
    parser.add_argument('--interval', type=int, default=5, help='Production interval in seconds')
    parser.add_argument('--cycles', type=int, default=0, help='Number of cycles to produce (0 for infinite)')
    
    args = parser.parse_args()
    
    producer = ManufacturingDataProducer()
    
    try:
        if args.cycles > 0:
            for i in range(args.cycles):
                producer.produce_cycle()
                time.sleep(args.interval)
        else:
            producer.start_production(args.interval)
            # Keep running until interrupted
            while True:
                time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        producer.stop()
