#!/usr/bin/env python3
"""Simple investigation of Azure DevOps work items using direct API calls"""

import requests
import json
import base64
from pathlib import Path

# Load settings
settings_file = Path('settings.json')
if not settings_file.exists():
    print("❌ No settings.json found")
    exit(1)

with open(settings_file, 'r') as f:
    settings = json.load(f)

org_url = settings.get('orgUrl', '').rstrip('/')
pat = settings.get('patToken')
enabled_projects = settings.get('enabledProjectDetails', [])

if not pat:
    print("❌ No PAT token found")
    exit(1)

# Create auth header
auth_string = f":{pat}"
auth_bytes = auth_string.encode('ascii')
auth_b64 = base64.b64encode(auth_bytes).decode('ascii')

headers = {
    'Authorization': f'Basic {auth_b64}',
    'Content-Type': 'application/json'
}

print(f"🔍 Investigating Azure DevOps Organization: {org_url}")
print(f"📁 Enabled Projects: {[p['projectName'] for p in enabled_projects]}\n")

# Investigate each project
for project in enabled_projects:
    project_name = project['projectName']
    print(f"\n{'='*60}")
    print(f"📋 Project: {project_name}")
    print(f"{'='*60}")
    
    # Query ALL work items
    wiql_url = f"{org_url}/{project_name}/_apis/wit/wiql?api-version=7.1"
    
    query = {
        "query": f"""
        SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], 
               [System.WorkItemType], [System.Tags]
        FROM WorkItems 
        WHERE [System.TeamProject] = '{project_name}'
        ORDER BY [System.Id] DESC
        """
    }
    
    try:
        # Execute WIQL query
        response = requests.post(wiql_url, json=query, headers=headers)
        response.raise_for_status()
        wiql_result = response.json()
        
        work_items = wiql_result.get('workItems', [])
        print(f"\n📊 Total work items found: {len(work_items)}")
        
        if work_items:
            # Get details for first 10 work items
            items_to_check = work_items[:10]
            
            # Get work item details
            wi_ids = [str(wi['id']) for wi in items_to_check]
            
            # Batch get work items
            batch_url = f"{org_url}/_apis/wit/workitemsbatch?api-version=7.1"
            batch_body = {
                "ids": wi_ids,
                "fields": [
                    "System.Id",
                    "System.Title", 
                    "System.State",
                    "System.AssignedTo",
                    "System.WorkItemType",
                    "System.Tags",
                    "System.CreatedDate"
                ]
            }
            
            batch_response = requests.post(batch_url, json=batch_body, headers=headers)
            batch_response.raise_for_status()
            batch_result = batch_response.json()
            
            state_counts = {}
            persona_found = []
            
            print(f"\n🔍 First {len(items_to_check)} work items:")
            print(f"{'ID':<8} {'State':<15} {'Type':<15} {'Assigned To':<25} {'Title':<40}")
            print("-" * 105)
            
            for wi in batch_result.get('value', []):
                wi_id = wi['id']
                fields = wi.get('fields', {})
                state = fields.get('System.State', 'Unknown')
                title = fields.get('System.Title', 'No Title')[:40]
                work_type = fields.get('System.WorkItemType', 'Unknown')
                tags = fields.get('System.Tags', '')
                
                # Count states
                state_counts[state] = state_counts.get(state, 0) + 1
                
                # Check assignment
                assigned_to = fields.get('System.AssignedTo')
                assigned_name = 'Unassigned'
                
                if assigned_to:
                    if isinstance(assigned_to, dict):
                        assigned_name = assigned_to.get('displayName', 'Unknown')
                        unique_name = assigned_to.get('uniqueName', '')
                        
                        # Check if it's a bot
                        if 'bot' in assigned_name.lower() or '.bot' in unique_name.lower():
                            persona_found.append({
                                'id': wi_id,
                                'name': assigned_name,
                                'email': unique_name,
                                'state': state,
                                'title': title
                            })
                    else:
                        assigned_name = str(assigned_to)
                
                print(f"{wi_id:<8} {state:<15} {work_type:<15} {assigned_name:<25} {title}")
            
            # Summary
            print(f"\n📊 Work Item States in first {len(items_to_check)} items:")
            for state, count in sorted(state_counts.items()):
                print(f"  {state}: {count}")
            
            # Check our target states
            target_states = ['New', 'Active', 'Resolved']
            print(f"\n🎯 Target states we're counting (New, Active, Resolved):")
            for state in target_states:
                count = state_counts.get(state, 0)
                print(f"  {state}: {count}")
            
            if persona_found:
                print(f"\n🤖 Bot/Persona Assignments Found:")
                for p in persona_found:
                    print(f"  #{p['id']} - {p['name']} ({p['email']}) - [{p['state']}] {p['title']}")
            else:
                print(f"\n❌ No work items assigned to bot personas")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        if hasattr(e, 'response') and e.response:
            print(f"Response: {e.response.text}")

print("\n" + "="*60)
print("🔍 Investigation Complete!")