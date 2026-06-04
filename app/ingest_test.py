import json
import requests
import time

import os
port = os.environ.get("PORT", 8000)
API_URL = f"http://127.0.0.1:{port}/events/ingest"

JSONL_FILE = "../data/generated_events.jsonl"
BATCH_SIZE = 100

def push_data():
    events = []
    
    with open(JSONL_FILE, 'r') as f:
        for line in f:
            if line.strip():
                events.append(json.loads(line))

    # Send in batches
    for i in range(0, len(events), BATCH_SIZE):
        batch = events[i:i + BATCH_SIZE]
        
        response = requests.post(API_URL, json=batch)
        
        if response.status_code == 202:
            print(f"Success! Inserted batch {i // BATCH_SIZE + 1} | Response: {response.json()}")
        else:
            print(f"Failed to insert batch: {response.status_code} - {response.text}")
            
        time.sleep(0.1) # Small pause so we don't overwhelm the local server

if __name__ == "__main__":
    push_data()