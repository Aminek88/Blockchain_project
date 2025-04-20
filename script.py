import os

# Base project directory (blockchain-project in the same directory as the script)
BASE_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), "blockchain-project")

# Dictionary mapping file paths (relative to BASE_DIR) to their contents
FILES = {
    "docker-compose.yaml": """version: '3.8'

services:
  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    container_name: zookeeper
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181
      ZOOKEEPER_TICK_TIME: 2000
    volumes:
      - zookeeper-data:/var/lib/zookeeper/data
    networks:
      - supply-chain-network

  kafka:
    image: confluentinc/cp-kafka:latest
    container_name: kafka
    depends_on:
      - zookeeper
    ports:
      - "9092:9092"
      - "29092:29092"
    environment:
      KAFKA_BROKER_ID: 1
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
    volumes:
      - kafka-data:/var/lib/kafka/data
      - ./kafka/config:/etc/kafka
      - ./dbt_project/seeds:/home/appuser/seeds
    networks:
      - supply-chain-network

  postgres:
    image: postgres:13
    container_name: postgres
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-data:/var/lib/postgresql/data
    networks:
      - supply-chain-network

  airflow-init:
    image: apache/airflow:2.7.1
    container_name: airflow-init
    environment:
      AIRFLOW__CORE__LOAD_EXAMPLES: False
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/logs:/opt/airflow/logs
      - ./airflow/plugins:/opt/airflow/plugins
    entrypoint: bash -c "airflow db init && airflow users create --username admin --password admin --firstname Admin --lastname User --email admin@example.com --role Admin"
    networks:
      - supply-chain-network

  airflow-webserver:
    image: apache/airflow:2.7.1
    container_name: airflow-webserver
    restart: always
    environment:
      AIRFLOW__CORE__LOAD_EXAMPLES: False
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    ports:
      - "8085:8080"
    depends_on:
      - postgres
      - airflow-init
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/logs:/opt/airflow/logs
      - ./airflow/plugins:/opt/airflow/plugins
    command: webserver
    networks:
      - supply-chain-network

  airflow-scheduler:
    image: apache/airflow:2.7.1
    container_name: airflow-scheduler
    restart: always
    environment:
      AIRFLOW__CORE__LOAD_EXAMPLES: False
      AIRFLOW__CORE__EXECUTOR: LocalExecutor
      AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    volumes:
      - ./airflow/dags:/opt/airflow/dags
      - ./airflow/logs:/opt/airflow/logs
      - ./airflow/plugins:/opt/airflow/plugins
      - ./data:/opt/airflow/data
    command: scheduler
    depends_on:
      - postgres
    networks:
      - supply-chain-network

  cubejs:
    image: cubejs/cube:latest
    container_name: cubejs
    ports:
      - "4000:4000"
    volumes:
      - ./cubejs-app:/cube/conf
    environment:
      CUBEJS_DB_TYPE: snowflake
      SNOWFLAKE_ACCOUNT: ${SNOWFLAKE_ACCOUNT}
      SNOWFLAKE_USER: ${SNOWFLAKE_USER}
      SNOWFLAKE_PASSWORD: ${SNOWFLAKE_PASSWORD}
      SNOWFLAKE_DATABASE: ${SNOWFLAKE_DATABASE}
      SNOWFLAKE_WAREHOUSE: ${SNOWFLAKE_WAREHOUSE}
      SNOWFLAKE_SCHEMA: ${SNOWFLAKE_SCHEMA}
      SNOWFLAKE_ROLE: ${SNOWFLAKE_ROLE}
      CUBEJS_API_SECRET: mysupersecretapikey1234567890
      NODE_ENV: development
    networks:
      - supply-chain-network

  streamlit:
    build:
      context: ./streamlit_app
      dockerfile: Dockerfile
    container_name: streamlit
    ports:
      - "8501:8501"
    volumes:
      - ./streamlit_app:/app
    depends_on:
      - cubejs
    networks:
      - supply-chain-network

  mlflow:
    image: ghcr.io/mlflow/mlflow
    container_name: mlflow
    ports:
      - "5000:5000"
    environment:
      MLFLOW_TRACKING_URI: http://mlflow:5000
    volumes:
      - ./mlruns:/mlruns
    networks:
      - supply-chain-network

  dbt:
    image: ghcr.io/dbt-labs/dbt-snowflake:1.5.0
    container_name: dbt
    volumes:
      - ./dbt_project:/usr/app/dbt_project
    environment:
      SNOWFLAKE_ACCOUNT: ${SNOWFLAKE_ACCOUNT}
      SNOWFLAKE_USER: ${SNOWFLAKE_USER}
      SNOWFLAKE_PASSWORD: ${SNOWFLAKE_PASSWORD}
      SNOWFLAKE_DATABASE: ${SNOWFLAKE_DATABASE}
      SNOWFLAKE_WAREHOUSE: ${SNOWFLAKE_WAREHOUSE}
      SNOWFLAKE_SCHEMA: ${SNOWFLAKE_SCHEMA}
      SNOWFLAKE_ROLE: ${SNOWFLAKE_ROLE}
    working_dir: /usr/app/dbt_project
    entrypoint: ["sh", "-c", "while true; do sleep 30; done;"]
    ports:
      - "8099:8080"
    networks:
      - supply-chain-network

  api:
    build:
      context: ./api
      dockerfile: Dockerfile
    container_name: api
    ports:
      - "8000:8000"
    volumes:
      - ./api:/app
      - ./data:/app/data
    depends_on:
      - kafka
      - mlflow
    networks:
      - supply-chain-network

networks:
  supply-chain-network:
    driver: bridge

volumes:
  zookeeper-data:
  kafka-data:
  postgres-data:
""",
    "README.md": """# Smart Supply Chain Analytics

A data pipeline for ingesting, processing, and analyzing supply chain data using Kafka, FastAPI, dbt, and Snowflake.

## Setup

 peruquisites**:
   - Docker and Docker Compose
   - Python 3.10+
   - Snowflake account credentials

2. **Environment Variables**:
   Create a `.env` file with the following:
   ```
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_PASSWORD=your_password
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_SCHEMA=your_schema
   SNOWFLAKE_ROLE=your_role
   ```

3. **Run the Pipeline**:
   ```bash
   docker-compose up --build
   ```

4. **Ingest Data**:
   Send CSV data to Kafka:
   ```bash
   curl -X POST http://localhost:8000/ingest_csv/
   ```

5. **Run dbt**:
   Execute dbt models:
   ```bash
   docker exec -it dbt dbt run --project-dir /usr/app/dbt_project
   ```

## Services

- **Kafka**: Streams CSV data to `csv_topic`.
- **FastAPI**: Ingests CSV data at `http://localhost:8000/ingest_csv/`.
- **dbt**: Transforms data in Snowflake.
- **Airflow**: Orchestrates workflows (webserver at `http://localhost:8085`).
- **CubeJS**: Serves analytics at `http://localhost:4000`.
- **Streamlit**: Visualizes data at `http://localhost:8501`.
- **MLflow**: Tracks ML experiments at `http://localhost:5000`.

## Kafka Commands

- Create topic:
  ```bash
  docker exec -it kafka kafka-topics --create --topic csv_topic --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
  ```

- Consume messages:
  ```bash
  docker exec -it kafka kafka-console-consumer --bootstrap-server localhost:9092 --topic csv_topic --from-beginning
  ```
""",
    "api/Dockerfile": """FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "api/requirements.txt": """fastapi
uvicorn
pandas
kafka-python
""",
    "api/config.py": """KAFKA_BOOTSTRAP_SERVERS = "kafka:9092"
KAFKA_TOPIC = "csv_topic"
CSV_FILE_PATH = "/app/data/DataCoSupplyChainDataset.csv"
ENCODING = "latin1"
""",
    "api/utils.py": """from kafka import KafkaProducer
import json

def init_kafka_producer(bootstrap_servers: str) -> KafkaProducer:
    \"\"\"Initialize and return a Kafka producer.\"\"\"
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
""",
    "api/main.py": """from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import pandas as pd
import time
from typing import Dict
from config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC, CSV_FILE_PATH, ENCODING
from utils import init_kafka_producer

app = FastAPI(title="Supply Chain Data Ingestion API")

# Initialize Kafka producer
producer = init_kafka_producer(KAFKA_BOOTSTRAP_SERVERS)

@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    \"\"\"Root endpoint for API health check.\"\"\"
    return {"message": "API for CSV Ingestion to Kafka"}

@app.post("/ingest_csv/", response_model=Dict[str, str])
async def ingest_csv() -> Dict[str, str]:
    \"\"\"Ingest CSV data into Kafka topic row by row.\"\"\"
    try:
        # Read CSV file
        df = pd.read_csv(CSV_FILE_PATH, encoding=ENCODING)
        
        # Send each row to Kafka
        for _, row in df.iterrows():
            producer.send(KAFKA_TOPIC, row.to_dict())
            producer.flush()
            time.sleep(0.5)  # Delay to prevent overwhelming Kafka
        
        return {"message": "CSV data sent to Kafka successfully"}
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="CSV file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
""",
    "kafka/scripts/consumer.py": """from kafka import KafkaConsumer
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
    \"\"\"Initialize and return a Kafka consumer.\"\"\"
    return KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        group_id="my-group",
        value_deserializer=lambda x: json.loads(x.decode("utf-8"))
    )

def append_to_csv(data: Dict[str, Any], csv_file: str) -> None:
    \"\"\"Append data to a CSV file.\"\"\"
    df = pd.DataFrame([data])
    df = df.where(pd.notnull(df), None)  # Replace NaN with None for Snowflake compatibility
    
    mode = "a" if os.path.exists(csv_file) else "w"
    header = not os.path.exists(csv_file)
    
    df.to_csv(csv_file, mode=mode, header=header, index=False)
    print(f"Data appended to {csv_file}")

def main():
    \"\"\"Main function to consume Kafka messages and save to CSV.\"\"\"
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
""",
    "dbt_project/models/schema.yml": """version: 2

sources:
  - name: analytics
    schema: SCHEMA
    tables:
      - name: DATA
        description: "Raw supply chain data with order, customer, and shipping details."

models:
  - name: stg_orders
    description: "Staging model for cleaned and transformed order data."
    columns:
      - name: ORDER_ID
        description: "Unique identifier for the order."
        tests:
          - not_null
          - unique
      - name: CUSTOMER_ID
        description: "Unique identifier for the customer."
        tests:
          - not_null
      - name: FULL_CUSTOMER_NAME
        description: "Customer's full name (first + last)."
      - name: CUSTOMER_CITY
        description: "Customer's city of residence."
      - name: CUSTOMER_COUNTRY
        description: "Customer's country of residence."
      - name: CUSTOMER_SEGMENT
        description: "Customer segment (e.g., Corporate, Consumer)."
      - name: ORDER_DATE
        description: "Date the order was placed."
        tests:
          - not_null
      - name: SHIPPING_DATE
        description: "Date the order was shipped."
      - name: SALES
        description: "Total sales amount for the order."
      - name: BENEFIT_PER_ORDER
        description: "Profit margin for the order."
      - name: LATE_DELIVERY_RISK
        description: "Indicator of late delivery risk (0 or 1)."
      - name: DELIVERY_STATUS
        description: "Current delivery status (e.g., Advance, Late)."
""",
    "dbt_project/models/stg_orders.sql": """{{ config(materialized='table') }}

WITH cleaned_data AS (
    SELECT
        ORDER_ID,
        CUSTOMER_ID,
        CONCAT(CUSTOMER_FNAME, ' ', CUSTOMER_LNAME) AS FULL_CUSTOMER_NAME,
        CUSTOMER_CITY,
        CUSTOMER_COUNTRY,
        CUSTOMER_SEGMENT,
        TRY_TO_DATE(ORDER_DATE, 'YYYY-MM-DD') AS ORDER_DATE,
        TRY_TO_DATE(SHIPPING_DATE, 'YYYY-MM-DD') AS SHIPPING_DATE,
        SALES,
        BENEFIT_PER_ORDER,
        LATE_DELIVERY_RISK,
        DELIVERY_STATUS
    FROM {{ source('analytics', 'DATA') }}
    WHERE ORDER_ID IS NOT NULL
      AND CUSTOMER_ID IS NOT NULL
)

SELECT *
FROM cleaned_data
"""
}

def create_directory(path: str) -> None:
    """Create a directory if it doesn't exist."""
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Created directory: {path}")
    except Exception as e:
        print(f"Error creating directory {path}: {e}")

def write_file(filepath: str, content: str) -> None:
    """Write content to a file."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created file: {filepath}")
    except Exception as e:
        print(f"Error writing file {filepath}: {e}")

def setup_project() -> None:
    """Set up the project structure and create files."""
    # Create base directory
    create_directory(BASE_DIR)

    # Create directories
    directories = [
        "api",
        "kafka/scripts",
        "dbt_project/models",
        "dbt_project/seeds",
        "data",
        "cubejs-app",
        "airflow/dags",
        "airflow/logs",
        "airflow/plugins"
    ]
    for dir_path in directories:
        create_directory(os.path.join(BASE_DIR, dir_path))

    # Create files
    for relative_path, content in FILES.items():
        filepath = os.path.join(BASE_DIR, relative_path)
        write_file(filepath, content)

    # Create empty files that were not fully specified
    empty_files = [
        "kafka/scripts/data.csv",
        "dbt_project/seeds/data.csv",
        "data/DataCoSupplyChainDataset.csv",
        "cubejs-app/cube.js"
    ]
    for relative_path in empty_files:
        filepath = os.path.join(BASE_DIR, relative_path)
        write_file(filepath, "")

if __name__ == "__main__":
    print("Setting up project structure in blockchain-project...")
    setup_project()
    print("Project setup complete!")