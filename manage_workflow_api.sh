#!/bin/bash
# Manage Workflow API service

case "$1" in
    start)
        if lsof -i :8081 > /dev/null 2>&1; then
            echo "Workflow API already running on port 8081"
        else
            echo "Starting Workflow API..."
            cd /opt/ai-personas
            python3 start_workflow_api.py > workflow_api.log 2>&1 &
            echo "Workflow API started on http://localhost:8081"
        fi
        ;;
    stop)
        echo "Stopping Workflow API..."
        pkill -f start_workflow_api.py
        echo "Workflow API stopped"
        ;;
    restart)
        $0 stop
        sleep 1
        $0 start
        ;;
    status)
        if lsof -i :8081 > /dev/null 2>&1; then
            echo "Workflow API is running on port 8081"
            echo "PID: $(lsof -t -i :8081)"
        else
            echo "Workflow API is not running"
        fi
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac