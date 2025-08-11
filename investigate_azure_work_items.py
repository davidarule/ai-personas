#!/usr/bin/env python3
"""Investigate Azure DevOps work items in the enabled projects"""

import asyncio
import json
from pathlib import Path
import sys
import os

# Add parent directory for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.orchestration.azure_devops_api_client import AzureDevOpsClient

async def investigate_work_items():
    # Load settings
    settings_file = Path('settings.json')
    if not settings_file.exists():
        print("❌ No settings.json found")
        return
        
    with open(settings_file, 'r') as f:
        settings = json.load(f)
    
    org_url = settings.get('orgUrl')
    pat = settings.get('patToken')
    enabled_projects = settings.get('enabledProjectDetails', [])
    
    if not org_url or not pat:
        print("❌ Missing Azure DevOps credentials")
        return
        
    print(f"🔍 Investigating Azure DevOps Organization: {org_url}")
    print(f"📁 Enabled Projects: {[p['projectName'] for p in enabled_projects]}\n")
    
    # Create client
    client = AzureDevOpsClient(org_url, pat)
    
    # For each project, get ALL work items regardless of state
    for project in enabled_projects:
        project_name = project['projectName']
        print(f"\n{'='*60}")
        print(f"📋 Project: {project_name}")
        print(f"{'='*60}")
        
        try:
            # Query ALL work items in the project
            wiql = {
                "query": f"""
                SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], 
                       [System.WorkItemType], [System.Tags], [System.CreatedDate],
                       [System.ChangedDate]
                FROM WorkItems 
                WHERE [System.TeamProject] = '{project_name}'
                ORDER BY [System.Id] DESC
                """
            }
            
            result = await client.query_work_items_by_wiql(project_name, wiql)
            
            if result and 'workItems' in result:
                print(f"\n📊 Total work items found: {len(result['workItems'])}")
                
                # Get details for first 20 work items
                work_items_to_check = result['workItems'][:20]
                
                # Categorize by state
                state_counts = {}
                persona_assignments = {
                    'Steve Bot': [],
                    'Kav Bot': [],
                    'Lachlan Bot': [],
                    'Dave Bot': [],
                    'Jordan Bot': [],
                    'Puck Bot': [],
                    'Matt Bot': [],
                    'Shaun Bot': [],
                    'Moby Bot': [],
                    'Claude Bot': [],
                    'Laureen Bot': [],
                    'Brumbie Bot': [],
                    'Ruley Bot': [],
                    'Unassigned': []
                }
                
                print(f"\n🔍 Analyzing first {len(work_items_to_check)} work items...")
                
                for wi_ref in work_items_to_check:
                    wi_id = wi_ref['id']
                    work_item = await client.get_work_item(project_name, wi_id)
                    
                    if work_item:
                        fields = work_item.get('fields', {})
                        state = fields.get('System.State', 'Unknown')
                        title = fields.get('System.Title', 'No Title')
                        work_type = fields.get('System.WorkItemType', 'Unknown')
                        tags = fields.get('System.Tags', '')
                        
                        # Count states
                        state_counts[state] = state_counts.get(state, 0) + 1
                        
                        # Check assignment
                        assigned_to = fields.get('System.AssignedTo', {})
                        assigned_name = 'Unassigned'
                        
                        if isinstance(assigned_to, dict):
                            display_name = assigned_to.get('displayName', '')
                            unique_name = assigned_to.get('uniqueName', '')
                            
                            # Check if assigned to any persona
                            assigned_to_persona = False
                            for persona in persona_assignments.keys():
                                if persona != 'Unassigned' and (
                                    persona.lower() in display_name.lower() or 
                                    persona.lower().replace(' bot', '.bot') in unique_name.lower()
                                ):
                                    persona_assignments[persona].append({
                                        'id': wi_id,
                                        'title': title[:50] + '...' if len(title) > 50 else title,
                                        'state': state,
                                        'type': work_type
                                    })
                                    assigned_to_persona = True
                                    assigned_name = persona
                                    break
                            
                            if not assigned_to_persona and display_name:
                                assigned_name = display_name
                        
                        if assigned_name == 'Unassigned' or assigned_name not in persona_assignments:
                            persona_assignments['Unassigned'].append({
                                'id': wi_id,
                                'title': title[:50] + '...' if len(title) > 50 else title,
                                'state': state,
                                'type': work_type,
                                'assigned_to': assigned_name if assigned_name != 'Unassigned' else None
                            })
                        
                        print(f"  #{wi_id}: {state.ljust(15)} | {work_type.ljust(15)} | {assigned_name.ljust(20)} | {title[:40]}...")
                
                # Show state summary
                print(f"\n📊 Work Item States:")
                for state, count in sorted(state_counts.items()):
                    print(f"  {state}: {count}")
                
                # Show persona assignments
                print(f"\n👥 Persona Assignments:")
                for persona, items in persona_assignments.items():
                    if items:
                        print(f"\n  {persona}: {len(items)} items")
                        for item in items[:3]:  # Show first 3
                            print(f"    - #{item['id']} [{item['state']}] {item['title']}")
                            if 'assigned_to' in item and item['assigned_to']:
                                print(f"      (Actually assigned to: {item['assigned_to']})")
                
                # Check states we're counting
                target_states = ['New', 'Active', 'Resolved']
                target_count = sum(state_counts.get(state, 0) for state in target_states)
                print(f"\n✅ Work items in target states (New, Active, Resolved): {target_count}")
                
            else:
                print("❌ No work items found or query failed")
                
        except Exception as e:
            print(f"❌ Error querying project {project_name}: {str(e)}")
            import traceback
            traceback.print_exc()

# Run the investigation
if __name__ == "__main__":
    asyncio.run(investigate_work_items())