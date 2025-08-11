#!/bin/bash
echo "Restarting all AI Personas services..."

# Stop all services
echo "Stopping services..."
pkill -f real_factory_api
pkill -f "http.server 3000"
./manage_workflow_api.sh stop

sleep 2

# Start all services in order
echo "Starting Backend API..."
cd /opt/ai-personas/src/api && python3 real_factory_api.py > ../../api.log 2>&1 &
sleep 3

echo "Starting Dashboard..."
cd /opt/ai-personas && python3 -m http.server 3000 > http_server.log 2>&1 &
sleep 2

echo "Starting Workflow API..."
./manage_workflow_api.sh start

echo ""
./check_services.sh