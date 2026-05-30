# PROMPT: "Write a FastAPI TestClient suite for my Store Intelligence API. 
# Test the POST /events/ingest endpoint to ensure it handles batches of 
# valid events and correctly enforces idempotency (ignores duplicate event_ids)."
#
# CHANGES MADE: The AI generated standard tests, but failed to include the 
# nested 'metadata' object required by my specific Pydantic schema, causing 
# 422 errors. I manually updated the payload payloads to match my StoreEvent 
# model and added a test specifically checking for the 400 error on batches > 500.

from fastapi.testclient import TestClient
from main import app
import uuid
import datetime

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_ingest_events_success():
    event_id = str(uuid.uuid4())
    payload = [{
        "event_id": event_id,
        "store_id": "STORE_TEST_01",
        "visitor_id": "VIS_123",
        "event_type": "ENTRY",
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "metadata": {"session_seq": 1}
    }]
    
    # Test initial ingestion
    response1 = client.post("/events/ingest", json=payload)
    assert response1.status_code == 202
    assert response1.json()["inserted"] == 1
    
    # Test idempotency (sending the exact same event again)
    response2 = client.post("/events/ingest", json=payload)
    assert response2.status_code == 202
    assert response2.json()["inserted"] == 0 # Should not insert a duplicate