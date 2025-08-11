#!/usr/bin/env python3
"""
Extract workflow definitions from index.html for conversion
"""

import re
import sys

def extract_workflow(html_content, workflow_id):
    """Extract a specific workflow definition from HTML"""
    
    # Find the workflow by ID
    pattern = rf"id: '{workflow_id}',\s*name: '([^']+)',\s*description: `([^`]+)`"
    match = re.search(pattern, html_content, re.DOTALL)
    
    if match:
        name = match.group(1)
        description = match.group(2)
        
        return {
            'id': workflow_id,
            'name': name,
            'description': description
        }
    
    return None

# Read index.html
with open('/opt/ai-personas/index.html', 'r') as f:
    html_content = f.read()

# Extract wf7
workflow = extract_workflow(html_content, 'wf7')
if workflow:
    print(f"Found: {workflow['name']}")
    print(f"Description length: {len(workflow['description'])} chars")
    
    # Save to file for processing
    with open(f"/tmp/{workflow['id']}_raw.txt", 'w') as f:
        f.write(workflow['description'])