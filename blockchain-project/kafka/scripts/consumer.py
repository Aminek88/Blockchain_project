from kafka import KafkaConsumer
import json
import pandas as pd
import os
from typing import Dict, Any

# Configuration constants
KAFKA_TOPIC = "csv_topic"
KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
SEEDS_DIR = "/home/appuser/seeds"
CSV_FILE = os.path.join(SEEDS_DIR, "data.csv")

def init_kafka_consumer() -> KafkaConsumer:
    """Initialize and return a Kafka consumer."""
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="my-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

def append_to_csv(data: Dict[str, Any], csv_file: str) -> None:
    """Append data to a CSV file."""
    df = pd.DataFrame([data])
    df = df.where(pd.notnull(df), None)  # Replace NaN with None for Snowflake compatibility
    
    mode = "a" if os.path.exists(csv_file) else "w"
    header = not os.path.exists(csv_file)
    
    df.to_csv(csv_file, mode=mode, header=header, index=False)
    print(f"Data appended to {csv_file}")

def main():
    """Main function to consume Kafka messages and save to CSV."""
    print("Starting Kafka consumer...")
    
    # Ensure seeds directory exists
    os.makedirs(SEEDS_DIR, exist_ok=True)
    
    # Initialize consumer
    consumer = init_kafka_consumer()
    
    # Consume messages
    for message in consumer:
        data = message.value
        print(f"Received data: {data}")
        append_to_csv(data, CSV_FILE)

if __name__ == "__main__":
    main()
