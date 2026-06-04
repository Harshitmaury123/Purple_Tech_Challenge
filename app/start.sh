#!/bin/bash
# Start the FastAPI server in the background
uvicorn main:app --host 0.0.0.0 --port $PORT &

# Wait 5 seconds for the server to fully start
sleep 5

# Run the ingestion script to populate the database with your 5 videos
python ingest_test.py

# Keep the container running
wait