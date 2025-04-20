from kafka import KafkaProducer
import json

def init_kafka_producer(bootstrap_servers: str) -> KafkaProducer:
    """Initialize and return a Kafka producer."""
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
