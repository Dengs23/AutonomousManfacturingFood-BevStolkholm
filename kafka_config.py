# kafka_config.py - Kafka Configuration
from dataclasses import dataclass

@dataclass
class KafkaConfig:
    # Kafka broker configuration
    BOOTSTRAP_SERVERS = ['localhost:9092']
    
    # Topic names
    TOPIC_SENSOR_DATA = 'manufacturing-sensor-data'
    TOPIC_ALERTS = 'manufacturing-alerts'
    TOPIC_AGENT_EVENTS = 'manufacturing-agent-events'
    TOPIC_SYSTEM_STATUS = 'manufacturing-system-status'
    
    # Consumer group
    CONSUMER_GROUP = 'dashboard-consumers'
    
    # Serialization format
    VALUE_SERIALIZER = 'json'
    VALUE_DESERIALIZER = 'json'
    
    # Security (if needed)
    SECURITY_PROTOCOL = None  # 'SASL_SSL' for production
    SASL_MECHANISM = None     # 'PLAIN' or 'SCRAM-SHA-256'
    SASL_USERNAME = None
    SASL_PASSWORD = None
    
    @classmethod
    def get_producer_config(cls):
        config = {
            'bootstrap_servers': cls.BOOTSTRAP_SERVERS,
            'value_serializer': lambda x: json.dumps(x).encode('utf-8')
        }
        
        if cls.SECURITY_PROTOCOL:
            config.update({
                'security_protocol': cls.SECURITY_PROTOCOL,
                'sasl_mechanism': cls.SASL_MECHANISM,
                'sasl_plain_username': cls.SASL_USERNAME,
                'sasl_plain_password': cls.SASL_PASSWORD
            })
        
        return config
    
    @classmethod
    def get_consumer_config(cls):
        config = {
            'bootstrap_servers': cls.BOOTSTRAP_SERVERS,
            'group_id': cls.CONSUMER_GROUP,
            'auto_offset_reset': 'latest',
            'enable_auto_commit': True,
            'value_deserializer': lambda x: json.loads(x.decode('utf-8'))
        }
        
        if cls.SECURITY_PROTOCOL:
            config.update({
                'security_protocol': cls.SECURITY_PROTOCOL,
                'sasl_mechanism': cls.SASL_MECHANISM,
                'sasl_plain_username': cls.SASL_USERNAME,
                'sasl_plain_password': cls.SASL_PASSWORD
            })
        
        return config
