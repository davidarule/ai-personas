#!/bin/bash

# Kill any existing API server
pkill -f real_factory_api.py

# Start the API server
cd /opt/ai-personas
python3 src/api/real_factory_api.py > api.log 2>&1 &

echo "API server started. PID: $!"
echo "Logs are in api.log"