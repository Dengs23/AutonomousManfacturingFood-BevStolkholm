# kafka_consumer.py - Kafka Data Consumer
import json
import threading
from collections import deque
from datetime import datetime
from kafka import KafkaConsumer
from kafka_config import KafkaConfig

class ManufacturingDataConsumer:
    def __init__(self, max_history=100):
        self.consumer = KafkaConsumer(
            KafkaConfig.TOPIC_SENSOR_DATA,
            KafkaConfig.TOPIC_ALERTS,
            KafkaConfig.TOPIC_SYSTEM_STATUS,
            KafkaConfig.TOPIC_AGENT_EVENTS,
            **KafkaConfig.get_consumer_config()
        )
        
        # Data storage
        self.sensor_data = {}
        self.alerts = deque(maxlen=max_history)
        self.system_status = deque(maxlen=max_history)
        self.agent_status = {}
        self.latest_cycle = None
        
        # Threading
        self.running = True
        self.consumer_thread = None
        
    def start(self):
        """Start consuming messages"""
        def consume_loop():
            for message in self.consumer:
                if not self.running:
                    break
                
                self.process_message(message)
        
        self.consumer_thread = threading.Thread(target=consume_loop, daemon=True)
        self.consumer_thread.start()
        print("Kafka consumer started")
    
    def process_message(self, message):
        """Process incoming Kafka messages"""
        topic = message.topic
        data = message.value
        
        if topic == KafkaConfig.TOPIC_SENSOR_DATA:
            self.sensor_data = data
            # print(f"Updated sensor data: {len(data)} sensors")
            
        elif topic == KafkaConfig.TOPIC_ALERTS:
            if 'alerts' in data and data['alerts']:
                for alert in data['alerts']:
                    self.alerts.appendleft(alert)  # Newest first
                print(f"Received {len(data['alerts'])} alerts")
                
        elif topic == KafkaConfig.TOPIC_SYSTEM_STATUS:
            self.system_status.appendleft(data)  # Newest first
            self.latest_cycle = data
            # print(f"Updated system status: Cycle #{data.get('cycle_id', 'N/A')}")
            
        elif topic == KafkaConfig.TOPIC_AGENT_EVENTS:
            if 'agents' in data:
                for agent in data['agents']:
                    self.agent_status[agent['id']] = agent
    
    def get_latest_data(self):
        """Get the latest data for the dashboard"""
        return {
            'sensor_data': self.sensor_data,
            'alerts': list(self.alerts)[:10],  # Last 10 alerts
            'system_status': self.latest_cycle,
            'agent_status': list(self.agent_status.values()),
            'history': list(self.system_status)[:20]  # Last 20 cycles
        }
    
    def stop(self):
        """Stop the consumer"""
        self.running = False
        self.consumer.close()

# Global consumer instance
consumer = None

def get_consumer():
    """Get or create a consumer instance"""
    global consumer
    if consumer is None:
        consumer = ManufacturingDataConsumer()
        consumer.start()
    return consumer
