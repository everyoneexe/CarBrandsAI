#!/bin/bash
# CarBrandsAI Quick Start

echo "CarBrandsAI Starting..."

# Start backend
python3 backend.py &
BACKEND_PID=$!

sleep 2

echo "API: http://localhost:5000"
echo "Site: http://localhost:8080"

# Start frontend
python3 -m http.server 8080

# Cleanup
trap 'kill $BACKEND_PID 2>/dev/null' EXIT