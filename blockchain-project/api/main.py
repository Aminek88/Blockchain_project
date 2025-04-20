from fastapi import FastAPI, HTTPException
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
    """Root endpoint for API health check."""
    return {"message": "API for CSV Ingestion to Kafka"}

@app.post("/ingest_csv/", response_model=Dict[str, str])
async def ingest_csv() -> Dict[str, str]:
    """Ingest CSV data into Kafka topic row by row."""
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
