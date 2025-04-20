# Smart Supply Chain Analytics

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
