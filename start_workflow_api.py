#!/usr/bin/env python3
"""
Start the workflow API server.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from api.workflow_api import app

if __name__ == '__main__':
    print("🚀 Starting Workflow API on http://localhost:8081")
    print("📍 Endpoints:")
    print("   GET /api/workflows     - Get all workflows")
    print("   GET /api/workflows/ID  - Get specific workflow")
    print()
    app.run(host='0.0.0.0', port=8081, debug=False)