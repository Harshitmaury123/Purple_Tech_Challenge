#!/bin/bash
uvicorn main:app --host 0.0.0.0 --port $PORT &

# Wait 10 seconds for the server to fully start
sleep 10

python ingest_test.py

wait