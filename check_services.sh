#\!/bin/bash
echo "=== Service Status Check ==="
echo ""
echo "Backend API (8080):"
if lsof -i :8080 > /dev/null 2>&1; then
    echo "✓ Running"
    curl -s http://localhost:8080/api/status | jq -r '.message' 2>/dev/null || echo "  (API check failed)"
else
    echo "✗ Not running"
    echo "  To start: cd /opt/ai-personas/src/api && python3 real_factory_api.py &"
fi

echo ""
echo "Dashboard (3000):"
if lsof -i :3000 > /dev/null 2>&1; then
    echo "✓ Running"
else
    echo "✗ Not running"
    echo "  To start: python3 -m http.server 3000 &"
fi

echo ""
echo "Workflow API (8081):"
if lsof -i :8081 > /dev/null 2>&1; then
    echo "✓ Running"
    echo "  $(curl -s http://localhost:8081/api/workflows | jq '.count' 2>/dev/null || echo "0") workflows available"
else
    echo "✗ Not running"
    echo "  To start: ./manage_workflow_api.sh start"
fi
