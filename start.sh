#!/bin/bash

# Start FastAPI backend in the background on port 8000
echo "Starting FastAPI Backend..."
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Wait a moment for the backend to start
sleep 3

# Start Streamlit frontend in the foreground on port 8080 (Cloud Run expected port)
echo "Starting Streamlit Frontend..."
streamlit run frontend/app.py --server.port=8080 --server.address=0.0.0.0
