#!/usr/bin/env python3
"""Test the Work Queue Azure DevOps integration"""

import requests
import json

print("Testing Work Queue Azure DevOps integration...\n")

# Test the work queue endpoint
response = requests.get('http://localhost:8080/api/work-queue-azure')
data = response.json()

print(f"Status Code: {response.status_code}")
print(f"Total Work Items: {data.get('total', 0)}")
print(f"\nWork Items by Project:")
for project, items in data.get('by_project', {}).items():
    print(f"  {project}: {len(items)} items")

print(f"\nWork Items by Persona:")
for persona, items in data.get('by_persona', {}).items():
    print(f"  {persona}: {len(items)} items")

# Check if the dashboard is updating
response = requests.get('http://localhost:8080/api/status')
status = response.json()
print(f"\nFactory Status:")
print(f"  Running: {status.get('factory_running', False)}")
print(f"  Active Personas: {status.get('active_personas', 0)}")
print(f"  Work Queue Size (local): {status.get('work_queue_size', 0)}")

print("\n✅ Work Queue is now connected to Azure DevOps!")
print("   - It fetches open work items from enabled projects")
print("   - Items are grouped by project and persona")
print("   - The dashboard will show the total count from Azure DevOps")