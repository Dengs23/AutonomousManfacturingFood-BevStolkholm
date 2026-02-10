import json

class KafkaConfig:
    BOOTSTRAP_SERVERS = ['localhost:9092']
    TOPIC_SENSOR_DATA = 'manufacturing-sensor-data'
    TOPIC_ALERTS = 'manufacturing-alerts'
    TOPIC_AGENT_EVENTS = 'manufacturing-agent-events'
    TOPIC_SYSTEM_STATUS = 'manufacturing-system-status'
    CONSUMER_GROUP = 'dashboard-consumers'
    
    @classmethod
    def get_producer_config(cls):
        return {
            'bootstrap_servers': cls.BOOTSTRAP_SERVERS,
            'value_serializer': lambda x: json.dumps(x).encode('utf-8')
        }
    
    @classmethod
    def get_consumer_config(cls):
        return {
            'bootstrap_servers': cls.BOOTSTRAP_SERVERS,
            'group_id': cls.CONSUMER_GROUP,
            'auto_offset_reset': 'latest',
            'enable_auto_commit': True,
            'value_deserializer': lambda x: json.loads(x.decode('utf-8'))
        }
