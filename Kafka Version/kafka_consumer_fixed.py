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
        
        self.sensor_data = {}
        self.alerts = deque(maxlen=max_history)
        self.system_status = deque(maxlen=max_history)
        self.agent_status = {}
        self.latest_cycle = None
        self.running = True
        self.consumer_thread = None
        
    def start(self):
        def consume_loop():
            for message in self.consumer:
                if not self.running:
                    break
                self.process_message(message)
        
        self.consumer_thread = threading.Thread(target=consume_loop, daemon=True)
        self.consumer_thread.start()
        print("✅ Kafka consumer started")
    
    def convert_datetimes(self, obj):
        """Convert datetime objects to ISO format strings"""
        if isinstance(obj, datetime):
            return obj.isoformat()
        elif isinstance(obj, dict):
            return {k: self.convert_datetimes(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.convert_datetimes(item) for item in obj]
        return obj
    
    def process_message(self, message):
        topic = message.topic
        data = message.value
        
        # Convert any datetimes in the data
        data = self.convert_datetimes(data)
        
        if topic == KafkaConfig.TOPIC_SENSOR_DATA:
            self.sensor_data = data
        elif topic == KafkaConfig.TOPIC_ALERTS:
            if 'alerts' in data and data['alerts']:
                for alert in data['alerts']:
                    self.alerts.appendleft(alert)
                print(f"⚠️  Received {len(data['alerts'])} alerts")
        elif topic == KafkaConfig.TOPIC_SYSTEM_STATUS:
            self.system_status.appendleft(data)
            self.latest_cycle = data
        elif topic == KafkaConfig.TOPIC_AGENT_EVENTS:
            if 'agents' in data:
                for agent in data['agents']:
                    self.agent_status[agent['id']] = agent
    
    def get_latest_data(self):
        return {
            'sensor_data': self.sensor_data,
            'alerts': list(self.alerts)[:10],
            'system_status': self.latest_cycle,
            'agent_status': list(self.agent_status.values()),
            'history': list(self.system_status)[:20]
        }
    
    def stop(self):
        self.running = False
        self.consumer.close()

consumer = None

def get_consumer():
    global consumer
    if consumer is None:
        consumer = ManufacturingDataConsumer()
        consumer.start()
    return consumer
