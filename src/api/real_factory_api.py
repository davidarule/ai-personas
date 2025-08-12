#!/usr/bin/env python3
"""
Real AI Factory API Service
Uses actual persona processors instead of mock data
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from aiohttp import web
import aiohttp
import uuid
import sys
import os
from pathlib import Path
import yaml

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personas.processor_factory_new import ProcessorFactory
from work_queue.work_queue import WorkQueue
from orchestration.azure_devops_api_client import AzureDevOpsClient
from database import get_log_database, get_tools_database, get_prompts_database, get_workflows_database, get_workflow_categories_database, get_workflow_diagrams_database, get_repository_database, get_workflow_history_database, get_agents_database, get_settings_database
from persona_api_integration import register_persona_routes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RealFactoryAPI:
    """Real API service using actual persona processors"""
    
    def __init__(self):
        self.factory_state = {
            "running": False,
            "start_time": None,
            "work_queue": WorkQueue(),
            "processor_factory": ProcessorFactory(),
            "active_processors": {},
            "completed_items": [],
            "azure_client": None,
            "last_azure_poll": None
        }
        self.system_logs = []
        self.log_db = get_log_database()  # Initialize log database
        self.tools_db = get_tools_database()  # Initialize tools database
        self.prompts_db = get_prompts_database()  # Initialize prompts database
        self.workflows_db = get_workflows_database()  # Initialize workflows database
        self.workflow_categories_db = get_workflow_categories_database()  # Initialize workflow categories database
        self.workflow_diagrams_db = get_workflow_diagrams_database()  # Initialize workflow diagrams database
        self.workflow_history_db = get_workflow_history_database()  # Initialize workflow history database
        self.repository_db = get_repository_database()  # Initialize repository database
        self.agents_db = get_agents_database()  # Initialize agents database
        self.settings_db = get_settings_database()  # Initialize settings database
        self._initialize_factory()
        self._initialize_azure_client()
        self._migrate_tools_if_needed()

        self._start_log_cleanup_task()
        
    def _start_log_cleanup_task(self):
        """Start background task to clean up old logs"""
        asyncio.create_task(self._log_cleanup_loop())
        
    def _initialize_factory(self):
        """Initialize the factory with real processors"""
        self.log_event("info", "Initializing AI Factory with real processors")
        
        # Initialize with new persona system
        try:
            # Create default persona instances for Steve and Kav (legacy compatibility)
            steve_instance = self.factory_state["processor_factory"].create_persona_instance(
                persona_type="software-architect",
                instance_id="steve-legacy",
                first_name="Steve",
                last_name="Bot"
            )
            if steve_instance:
                self.log_event("success", "Created Steve (Software Architect) persona instance")
            
            kav_instance = self.factory_state["processor_factory"].create_persona_instance(
                persona_type="qa-test-engineer",
                instance_id="kav-legacy",
                first_name="Kav",
                last_name="Bot"
            )
            if kav_instance:
                self.log_event("success", "Created Kav (QA/Test Engineer) persona instance")
                
            # Load any saved state
            self.factory_state["processor_factory"].load_state()
            
            # Get all instances for tracking
            instances = self.factory_state["processor_factory"].get_all_instances()
            self.log_event("info", f"Factory initialized with {len(instances)} persona instances")
            
        except Exception as e:
            self.log_event("error", f"Failed to initialize personas: {str(e)}")
            import traceback
            self.log_event("error", f"Traceback: {traceback.format_exc()}")
        
    def _initialize_azure_client(self):
        """Initialize Azure DevOps client"""
        try:
            # First try to get PAT from database
            pat = self.settings_db.get_decrypted_credential("azure_devops_pat")
            
            # Fallback to environment variable if not in database
            if not pat:
                pat = os.getenv("AZURE_DEVOPS_PAT")
            
            # Get org URL from settings database
            org_url = self.settings_db.get_setting('orgUrl')
            
            # Fallback to settings.json for backward compatibility
            if not org_url:
                settings_file = Path(__file__).parent.parent.parent / "settings.json"
                if settings_file.exists():
                    try:
                        with open(settings_file, 'r') as f:
                            settings = json.load(f)
                            org_url = settings.get('orgUrl')
                    except Exception as e:
                        self.log_event("error", f"Failed to load settings: {str(e)}")
            
            # Final fallback to environment variable
            if not org_url:
                org_url = os.getenv("AZURE_DEVOPS_ORG")
                        
            if org_url and pat:
                # Extract organization from URL
                # Handle both https://dev.azure.com/org and org formats
                if org_url.startswith('https://'):
                    org = org_url.split('/')[-1]
                else:
                    org = org_url
                    
                # Create client with proper async support
                self.factory_state["azure_client"] = AzureDevOpsClient(org_url, pat)
                # Force initialization of the APIs with sync session
                if hasattr(self.factory_state["azure_client"], '_init_apis'):
                    self.factory_state["azure_client"]._init_apis()
                self.log_event("success", f"Connected to Azure DevOps organization: {org}")
            else:
                if not pat:
                    self.log_event("error", "AZURE_DEVOPS_PAT environment variable not set")
                if not org_url:
                    self.log_event("error", "Azure DevOps organization URL not configured")
                self.log_event("warning", "Azure DevOps credentials not configured")
        except Exception as e:
            self.log_event("error", f"Failed to initialize Azure DevOps client: {str(e)}")
    
    def _migrate_tools_if_needed(self):
        """Run tools migration from settings.json to database if needed"""
        try:
            # Check if tools already exist in database
            categories = self.tools_db.get_all_categories()
            if categories:
                self.log_event("info", f"Tools database already populated with {len(categories)} categories")
                return
            
            # Load settings file
            settings_path = Path(__file__).parent.parent.parent / 'settings_extended.json'
            if settings_path.exists():
                with open(settings_path, 'r') as f:
                    settings = json.load(f)
                
                # Import tools if they exist in settings
                if 'tools' in settings:
                    result = self.tools_db.import_from_json(settings)
                    self.log_event("success", f"Migrated {result['categories']} categories and {result['tools']} tools to database")
        except Exception as e:
            self.log_event("error", f"Failed to migrate tools: {str(e)}")
        
    def log_event(self, level: str, message: str, persona_name: str = None, 
                 work_item_id: int = None, project_name: str = None):
        """Log system events to both memory and database"""
        # Save to database
        if persona_name:
            self.log_db.add_persona_log(
                persona_name=persona_name,
                level=level,
                message=message,
                work_item_id=work_item_id,
                project_name=project_name
            )
        else:
            self.log_db.add_system_log(level=level, message=message)
        
        # Also keep in memory for backwards compatibility
        timestamp = self.log_db._get_aest_timestamp()
        self.system_logs.append({
            "timestamp": timestamp,
            "level": level,
            "message": message
        })
        if len(self.system_logs) > 1000:
            self.system_logs.pop(0)
            
        logger.info(f"[{level}] {message}")
            
    async def get_status(self, request):
        """GET /api/status"""
        uptime = None
        if self.factory_state["running"] and self.factory_state["start_time"]:
            delta = datetime.now() - self.factory_state["start_time"]
            uptime = str(delta).split('.')[0]
            
        # Count active personas (those with processors)
        instances = self.factory_state["processor_factory"].get_all_instances()
        active_count = sum(1 for instance_id in instances.keys() 
                          if self.factory_state["processor_factory"].get_processor(instance_id) is not None)
        
        # Check Azure DevOps connection
        azure_connected = self.factory_state["azure_client"] is not None
        
        data = {
            "factory_running": self.factory_state["running"],
            "personas_count": len(instances),
            "active_personas": active_count,
            "work_queue_size": self.factory_state["work_queue"].size(),
            "completed_items": len(self.factory_state["completed_items"]),
            "uptime": uptime,
            "system_time": datetime.now().isoformat(),
            "azure_connected": azure_connected
        }
        return web.json_response(data)
        
    async def get_personas(self, request):
        """GET /api/personas - Get all persona instances"""
        personas_data = {}
        
        # Get all instances from new factory
        instances = self.factory_state["processor_factory"].get_all_instances()
        
        for instance_id, instance in instances.items():
            # Create state data for compatibility
            state = {
                "status": "idle" if instance.is_active else "stopped",
                "current_work_item": None,
                "work_items_completed": instance.work_items_processed,
                "last_activity": instance.last_activity.isoformat() if instance.last_activity else None,
                "outputs_generated": []
            }
            
            # If factory is not running, all personas should show as stopped
            if not self.factory_state["running"]:
                state["status"] = "stopped"
            
            # Get persona config for display info
            persona_config = self.factory_state["processor_factory"].registry.get(instance.persona_type)
            
            # Create info data
            info = {
                "name": instance.full_name,
                "display_name": persona_config.display_name if persona_config else instance.persona_type,
                "description": persona_config.description if persona_config else "",
                "type": instance.persona_type,
                "skills": instance.skills,
                "mcp_servers": instance.mcp_servers,
                "tools": instance.tools
            }
            
            personas_data[instance_id] = {
                "info": info,
                "state": state
            }
            
        return web.json_response(personas_data)
        
    async def get_work_queue(self, request):
        """GET /api/work-queue"""
        items = self.factory_state["work_queue"].get_all_items()
        data = {
            "size": self.factory_state["work_queue"].size(),
            "total_items": len(items),
            "items": items
        }
        return web.json_response(data)
        
    async def add_work_item(self, request):
        """POST /api/work-queue"""
        try:
            data = await request.json()
            
            # Create work item that matches what processors expect
            work_item = {
                "id": str(uuid.uuid4()),
                "title": data.get("title", "Untitled Work Item"),
                "description": data.get("description", ""),
                "type": data.get("type", "feature"),
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }
            
            item_id = await self.factory_state["work_queue"].add_item(work_item)
            self.log_event("info", f"Added work item {item_id}: {work_item['title']}")
            return web.json_response({"id": item_id, "status": "added"})
        except Exception as e:
            self.log_event("error", f"Failed to add work item: {str(e)}")
            return web.json_response({"error": str(e)}, status=400)
            
    async def get_logs(self, request):
        """GET /api/logs - Get logs from database"""
        limit = int(request.query.get('limit', 100))
        log_type = request.query.get('type', 'all')  # all, system, persona
        persona_name = request.query.get('persona', None)
        format_type = request.query.get('format', 'json')  # json or formatted
        
        if log_type == 'system':
            logs = self.log_db.get_system_logs(limit=limit)
        elif log_type == 'persona' and persona_name:
            logs = self.log_db.get_persona_logs(persona_name=persona_name, limit=limit)
        else:
            # Get combined latest logs
            logs = self.log_db.get_latest_logs(count=limit)
        
        # Format logs if requested
        if format_type == 'formatted':
            formatted_logs = []
            for log in logs:
                formatted_logs.append({
                    'original': log,
                    'formatted': self.log_db.format_log_entry(log)
                })
            return web.json_response(formatted_logs)
            
        return web.json_response(logs)
        
    async def start_factory(self, request):
        """POST /api/factory/start"""
        if not self.factory_state["running"]:
            self.factory_state["running"] = True
            self.factory_state["start_time"] = datetime.now()
            self.log_event("success", "AI Factory started with real processors")
            
            # Update status of all active persona instances
            instances = self.factory_state["processor_factory"].get_all_instances()
            for instance in instances.values():
                if instance.is_active:
                    # Mark instance as ready for work
                    instance.last_activity = datetime.now()
            
            # Start processing loop
            asyncio.create_task(self.processing_loop())
            
            # Do initial Azure DevOps poll
            asyncio.create_task(self.poll_azure_devops())
            
            return web.json_response({"status": "started", "message": "Factory is now running with real processors"})
        return web.json_response({"status": "already_running", "message": "Factory is already running"})
        
    async def stop_factory(self, request):
        """POST /api/factory/stop"""
        self.factory_state["running"] = False
        self.log_event("warning", "AI Factory stopped")
        
        # Deactivate all persona instances
        instances = self.factory_state["processor_factory"].get_all_instances()
        for instance in instances.values():
            instance.is_active = False
            
        return web.json_response({"status": "stopped", "message": "Factory has been stopped"})
        
    async def poll_azure_devops(self):
        """Poll Azure DevOps for new work items"""
        if not self.factory_state["azure_client"]:
            return
            
        try:
            # Get enabled projects from settings
            settings_file = Path(__file__).parent.parent.parent / 'settings.json'
            enabled_projects = []
            
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    enabled_project_details = settings.get('enabledProjectDetails', [])
                    enabled_projects = [p['projectName'] for p in enabled_project_details]
            
            if not enabled_projects:
                self.log_event("warning", "No projects enabled for AI Personas")
                return
            
            # Poll each enabled project
            for project in enabled_projects:
                try:
                    # Query for open work items assigned to the team or unassigned
                    wiql = {
                        "query": f"""
                        SELECT [System.Id], [System.Title], [System.Description], [System.WorkItemType], 
                               [System.State], [System.AssignedTo], [System.Tags]
                        FROM workitems
                        WHERE [System.TeamProject] = '{project}'
                          AND [System.State] IN ('New', 'Active', 'To Do')
                          AND ([System.AssignedTo] = '' OR [System.Tags] CONTAINS 'ai-personas')
                        ORDER BY [System.Priority] ASC, [System.CreatedDate] DESC
                        """
                    }
            
                    # Get work items from Azure DevOps
                    result = await self.factory_state["azure_client"].query_work_items_by_wiql(project, wiql)
                    
                    if result and "workItems" in result:
                        for wi_ref in result["workItems"]:
                            wi_id = wi_ref["id"]
                            
                            # Get full work item details
                            work_item = await self.factory_state["azure_client"].get_work_item(project, wi_id)
                            
                            if work_item:
                                # Convert to our work item format
                                queue_item = {
                                    "id": str(wi_id),
                                    "title": work_item.get("fields", {}).get("System.Title", ""),
                                    "description": work_item.get("fields", {}).get("System.Description", ""),
                                    "type": work_item.get("fields", {}).get("System.WorkItemType", "Task").lower(),
                                    "created_at": datetime.now().isoformat(),
                                    "status": "pending",
                                    "azure_id": wi_id,
                                    "azure_url": work_item.get("url", ""),
                                    "project": project
                                }
                                
                                # Add to queue if not already processed
                                if not any(item.get("azure_id") == wi_id for item in self.factory_state["completed_items"]):
                                    await self.factory_state["work_queue"].add_item(queue_item)
                                    self.log_event("info", f"Added Azure DevOps work item #{wi_id} from {project}: {queue_item['title']}")
                                    
                except Exception as e:
                    self.log_event("error", f"Failed to poll Azure DevOps project {project}: {str(e)}")
                    
            self.factory_state["last_azure_poll"] = datetime.now()
            
        except Exception as e:
            self.log_event("error", f"Failed to poll Azure DevOps: {str(e)}")

    async def processing_loop(self):
        """Process work items with real processors"""
        poll_interval = 0
        
        while self.factory_state["running"]:
            try:
                # Poll Azure DevOps every 30 seconds
                if poll_interval % 15 == 0:  # 30 seconds (15 * 2 second sleep)
                    await self.poll_azure_devops()
                    poll_interval = 0
                    
                # Get next work item
                work_item = await self.factory_state["work_queue"].get_next_item()
                
                if work_item:
                    # Find suitable persona based on work item type/title
                    assigned_persona = self._find_suitable_persona(work_item)
                    
                    if assigned_persona:
                        instance_id, instance = assigned_persona
                        
                        # Update instance activity
                        instance.last_activity = datetime.now()
                        
                        self.log_event("info", 
                            f"{instance.full_name} started working on: {work_item.get('title', work_item['id'])}", 
                            persona_name=instance.full_name,
                            work_item_id=work_item.get('azure_id') or work_item.get('id'),
                            project_name=work_item.get('project'))
                        
                        # Process work with real processor
                        asyncio.create_task(self.process_work_item_real(instance_id, instance, work_item))
                    else:
                        self.log_event("warning", f"No suitable persona found for work item: {work_item.get('title')}")
                        # Put back in queue
                        await self.factory_state["work_queue"].add_item(work_item)
                        
                await asyncio.sleep(2)
                poll_interval += 1
                
            except Exception as e:
                self.log_event("error", f"Processing loop error: {str(e)}")
                await asyncio.sleep(5)

    async def _log_cleanup_loop(self):
        """Periodically clean up old logs based on settings"""
        while True:
            try:
                # Wait 24 hours between cleanups
                await asyncio.sleep(86400)  # 24 hours in seconds
                
                # Get log retention days from settings
                settings_file = Path(__file__).parent.parent.parent / 'settings.json'
                system_retention_days = 7  # Default
                persona_retention_days = 7  # Default
                
                if settings_file.exists():
                    try:
                        with open(settings_file, 'r') as f:
                            settings = json.load(f)
                            # Support both old and new settings
                            system_retention_days = settings.get('systemLogRetentionDays', settings.get('logRetentionDays', 7))
                            persona_retention_days = settings.get('personaLogRetentionDays', settings.get('logRetentionDays', 7))
                    except Exception as e:
                        self.log_event("error", f"Failed to read log retention settings: {str(e)}")
                
                # Delete old logs with separate retention
                system_deleted, persona_deleted = self.log_db.delete_old_logs_separate(
                    system_retention_days, persona_retention_days)
                
                if system_deleted > 0 or persona_deleted > 0:
                    self.log_event("info", 
                        f"Automatic log cleanup: Deleted {system_deleted} system logs older than "
                        f"{system_retention_days} days and {persona_deleted} persona logs older than "
                        f"{persona_retention_days} days")
                
            except Exception as e:
                self.log_event("error", f"Log cleanup error: {str(e)}")
                # Continue running even if there's an error
                await asyncio.sleep(3600)  # Wait 1 hour before retry
                
    def _find_suitable_persona(self, work_item: Dict) -> Optional[tuple]:
        """Find a suitable persona instance for the work item"""
        title = work_item.get("title", "").lower()
        description = work_item.get("description", "").lower()
        work_type = work_item.get("type", "").lower()
        
        # Get all active instances
        instances = self.factory_state["processor_factory"].get_all_instances()
        
        # Priority mapping based on keywords
        if any(keyword in title + description for keyword in ["security", "threat", "vulnerability", "risk"]):
            # Try Software Architect first for security architecture
            if "architecture" in title + description:
                for instance_id, instance in instances.items():
                    if instance.persona_type == "software-architect" and self._is_instance_available(instance_id):
                        return (instance_id, instance)
            # Then QA/Test Engineer for security testing
            for instance_id, instance in instances.items():
                if instance.persona_type == "qa-test-engineer" and self._is_instance_available(instance_id):
                    return (instance_id, instance)
                    
        # Find any available persona with a processor
        for instance_id, instance in instances.items():
            if self._is_instance_available(instance_id):
                return (instance_id, instance)
                
        return None
        
    def _is_instance_available(self, instance_id: str) -> bool:
        """Check if a persona instance is available for work"""
        instance = self.factory_state["processor_factory"].get_persona_instance(instance_id)
        processor = self.factory_state["processor_factory"].get_processor(instance_id)
        return (instance and instance.is_active and processor is not None)
                
    async def process_work_item_real(self, instance_id: str, instance: Any, work_item: Dict):
        """Process work item with real processor"""
        result = self.factory_state["processor_factory"].process_work_item(instance_id, work_item)
        
        if result.get('status') == 'success':
            # Update work item status
            work_item["status"] = "completed"
            work_item["completed_at"] = datetime.now().isoformat()
            work_item["completed_by"] = instance.full_name
            work_item["result"] = result
            
            self.factory_state["completed_items"].append(work_item)
            
            self.log_event("success", 
                f"{instance.full_name} completed: {work_item.get('title')} - Success",
                persona_name=instance.full_name,
                work_item_id=work_item.get('azure_id') or work_item.get('id'),
                project_name=work_item.get('project'))
        else:
            work_item["status"] = "failed"
            work_item["error"] = result.get('message', 'Unknown error')
            self.log_event("error", f"{instance.full_name} failed on work item: {result.get('message')}",
                           persona_name=instance.full_name,
                           work_item_id=work_item.get('azure_id') or work_item.get('id'),
                           project_name=work_item.get('project'))
            
    async def get_settings(self, request):
        """GET /api/settings - Get current Azure DevOps settings"""
        # Get settings from database first
        db_settings = self.settings_db.get_all_settings()
        
        # Get PAT status
        pat_info = self.settings_db.get_credential('azure_devops_pat')
        
        # Merge with settings.json for backward compatibility
        settings_file = Path(__file__).parent.parent.parent / "settings.json"
        if settings_file.exists():
            try:
                with open(settings_file, 'r') as f:
                    file_settings = json.load(f)
                    # Merge settings, database takes precedence
                    for key, value in file_settings.items():
                        if key not in db_settings and key != 'patToken':
                            db_settings[key] = value
            except Exception as e:
                self.log_event("error", f"Failed to load settings file: {str(e)}")
        
        # Add PAT status
        if pat_info:
            db_settings['hasPatToken'] = True
            db_settings['patTokenHint'] = pat_info.get('hint', '')
            db_settings['patTokenUpdated'] = pat_info.get('updated_at', '')
        else:
            # Check environment variable as fallback
            db_settings['hasPatToken'] = bool(os.getenv('AZURE_DEVOPS_PAT'))
            db_settings['patTokenHint'] = '****' if db_settings['hasPatToken'] else ''
        
        return web.json_response(db_settings)
        
    async def save_settings(self, request):
        """POST /api/settings - Save Azure DevOps settings"""
        try:
            data = await request.json()
            org_url = data.get('orgUrl', '').strip()
            pat_token = data.get('patToken', '').strip()
            
            if not org_url:
                return web.json_response({'error': 'Organization URL is required'}, status=400)
            
            # Save org URL to settings database
            self.settings_db.set_setting('orgUrl', org_url)
            
            # Handle PAT token if provided
            if pat_token:
                # Store encrypted PAT in database
                success = self.settings_db.set_credential(
                    'azure_devops_pat', 
                    pat_token, 
                    'Azure DevOps Personal Access Token'
                )
                if not success:
                    return web.json_response({'error': 'Failed to save PAT token securely'}, status=500)
            else:
                # Check if we have a PAT available (either in DB or env var)
                existing_pat = self.settings_db.get_decrypted_credential("azure_devops_pat")
                if not existing_pat and not os.getenv('AZURE_DEVOPS_PAT'):
                    return web.json_response({'error': 'No PAT token available. Please provide one.'}, status=400)
            
            # Load existing settings if they exist
            existing_settings = {}
            settings_file = Path(__file__).parent.parent.parent / 'settings.json'
            if settings_file.exists():
                try:
                    with open(settings_file, 'r') as f:
                        existing_settings = json.load(f)
                except:
                    pass
            
            # Save other settings to database
            system_log_retention = data.get('systemLogRetentionDays', existing_settings.get('systemLogRetentionDays', 7))
            persona_log_retention = data.get('personaLogRetentionDays', existing_settings.get('personaLogRetentionDays', 7))
            
            self.settings_db.set_setting('systemLogRetentionDays', system_log_retention)
            self.settings_db.set_setting('personaLogRetentionDays', persona_log_retention)
            
            # Also save to settings.json for backward compatibility (without PAT)
            settings = existing_settings.copy()
            settings.update({
                'orgUrl': org_url,
                'systemLogRetentionDays': system_log_retention,
                'personaLogRetentionDays': persona_log_retention,
                'savedAt': datetime.now().isoformat()
            })
            
            # Remove any PAT token that might be in existing settings
            if 'patToken' in settings:
                del settings['patToken']
            
            with open('settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
            
            # Re-initialize Azure client with new settings
            os.environ['AZURE_DEVOPS_ORG'] = org_url
            self._initialize_azure_client()
            
            self.log_event("success", "Azure DevOps settings updated")
            return web.json_response({'status': 'success', 'message': 'Settings saved successfully'})
            
        except Exception as e:
            self.log_event("error", f"Failed to save settings: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def test_connection(self, request):
        """POST /api/test-connection - Test Azure DevOps connection"""
        try:
            data = await request.json()
            org_url = data.get('orgUrl', '').strip()
            
            if not org_url:
                return web.json_response({'error': 'Organization URL is required'}, status=400)
            
            # First try to get PAT from database
            pat_token = self.settings_db.get_decrypted_credential("azure_devops_pat")
            
            # Fallback to environment variable if not in database
            if not pat_token:
                pat_token = os.getenv('AZURE_DEVOPS_PAT')
            
            if not pat_token:
                return web.json_response({'error': 'No PAT token available. Please configure one in settings.'}, status=400)
                
            # Create temporary client to test connection
            test_client = AzureDevOpsClient(org_url, pat_token)
            
            # Try to get projects list as connection test
            projects = await test_client.get_projects()
            
            if projects and 'value' in projects:
                project_list = [{'id': p['id'], 'name': p['name']} for p in projects['value']]
                return web.json_response({
                    'status': 'success',
                    'message': f'Connected successfully! Found {len(project_list)} projects.',
                    'projects': project_list
                })
            else:
                return web.json_response({
                    'status': 'error',
                    'message': 'Connection failed - no projects found'
                }, status=400)
                
        except Exception as e:
            self.log_event("error", f"Connection test failed: {str(e)}")
            return web.json_response({
                'status': 'error',
                'message': f'Connection failed: {str(e)}'
            }, status=400)
            
    async def save_project_configuration(self, request):
        """POST /api/project-configuration - Save project/persona configuration"""
        try:
            data = await request.json()
            enabled_projects = data.get('enabledProjects', [])
            
            # Load existing settings
            settings_file = Path(__file__).parent.parent.parent / 'settings.json'
            settings = {}
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
            
            # Store just the enabled project IDs
            settings['enabledProjects'] = [p['projectId'] for p in enabled_projects]
            settings['enabledProjectDetails'] = enabled_projects  # Store full details too
            settings['configUpdatedAt'] = datetime.now().isoformat()
            
            # Save updated settings
            with open(settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            
            self.log_event("success", f"Saved configuration for {len(enabled_projects)} enabled projects")
            
            return web.json_response({
                'status': 'success',
                'message': f'Configuration saved for {len(enabled_projects)} enabled projects'
            })
            
        except Exception as e:
            self.log_event("error", f"Failed to save project configuration: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def get_project_configuration(self, request):
        """GET /api/project-configuration - Get saved project/persona configuration"""
        try:
            settings_file = Path(__file__).parent.parent.parent / 'settings.json'
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    settings = json.load(f)
                    enabled_projects = settings.get('enabledProjects', [])
                    return web.json_response({
                        'status': 'success',
                        'enabledProjects': enabled_projects
                    })
            
            return web.json_response({
                'status': 'success',
                'enabledProjects': []
            })
            
        except Exception as e:
            self.log_event("error", f"Failed to get project configuration: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def check_team_membership(self, request):
        """POST /api/check-team-membership - Check if personas are team members in a project"""
        try:
            data = await request.json()
            project_id = data.get('projectId')
            project_name = data.get('projectName')
            
            if not project_id or not project_name:
                return web.json_response({'error': 'Project ID and name are required'}, status=400)
            
            # Check if we have Azure client
            if not self.factory_state["azure_client"]:
                return web.json_response({
                    'error': 'Azure DevOps not configured',
                    'needsConfiguration': True
                }, status=400)
            
            try:
                # Get all teams in the project
                teams_url = f"{self.factory_state['azure_client'].base_url}/_apis/projects/{project_id}/teams?api-version=7.1"
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(teams_url, headers=self.factory_state['azure_client'].headers) as response:
                        response.raise_for_status()
                        teams_response = await response.json()
                    
                    membership_status = {}
                    
                    # Get all persona names from instances
                    instances = self.factory_state["processor_factory"].get_all_instances()
                    persona_names = [instance.full_name for instance in instances.values()]
                    
                    # For each team, check members
                    for team in teams_response.get('value', []):
                        team_id = team['id']
                        team_name = team['name']
                        
                        # Get team members
                        members_url = f"{self.factory_state['azure_client'].base_url}/_apis/projects/{project_id}/teams/{team_id}/members?api-version=7.1"
                        
                        async with session.get(members_url, headers=self.factory_state['azure_client'].headers) as response:
                            response.raise_for_status()
                            members_response = await response.json()
                    
                        # Check if any personas are members
                        for member in members_response.get('value', []):
                            display_name = member.get('identity', {}).get('displayName', '')
                            unique_name = member.get('identity', {}).get('uniqueName', '')
                            
                            # Check against persona names
                            for persona_name in persona_names:
                                if persona_name.lower() in display_name.lower() or persona_name.lower() in unique_name.lower():
                                    if persona_name not in membership_status:
                                        membership_status[persona_name] = []
                                    membership_status[persona_name].append({
                                        'teamId': team_id,
                                        'teamName': team_name,
                                        'memberDisplayName': display_name
                                    })
                
                self.log_event("info", f"Checked team membership for project {project_name}")
                
                return web.json_response({
                    'status': 'success',
                    'projectId': project_id,
                    'projectName': project_name,
                    'personaMembership': membership_status
                })
                
            except Exception as e:
                self.log_event("error", f"Failed to check team membership: {str(e)}")
                return web.json_response({
                    'error': f'Failed to check team membership: {str(e)}'
                }, status=500)
                
        except Exception as e:
            self.log_event("error", f"Team membership check error: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def get_completed_items(self, request):
        """GET /api/completed-items - Get list of completed work items"""
        try:
            # Get last N completed items
            limit = int(request.query.get('limit', 50))
            items = self.factory_state["completed_items"][-limit:] if self.factory_state["completed_items"] else []
            
            # Reverse to show newest first
            items = list(reversed(items))
            
            return web.json_response({
                'status': 'success',
                'total': len(self.factory_state["completed_items"]),
                'items': items
            })
        except Exception as e:
            self.log_event("error", f"Failed to get completed items: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)

    async def get_work_queue_from_azure(self, request):
        """GET /api/work-queue-azure - Get work items from Azure DevOps for enabled projects"""
        try:
            if not self.factory_state.get("azure_client"):
                return web.json_response({'error': 'Azure DevOps not configured'}, status=400)
            
            # Check cache first - only refresh every 30 seconds
            cache_key = "azure_work_queue_cache"
            cache_timestamp_key = "azure_work_queue_cache_timestamp"
            
            now = datetime.now()
            cache_timestamp = self.factory_state.get(cache_timestamp_key)
            cached_data = self.factory_state.get(cache_key)
            
            if cached_data and cache_timestamp:
                # If cache is less than 30 seconds old, return cached data
                if (now - cache_timestamp).total_seconds() < 30:
                    return web.json_response(cached_data)
            
            # Cache is expired or doesn't exist, fetch fresh data
            
            azure_client = self.factory_state["azure_client"]
            
            # Load project configuration
            settings_file = Path(__file__).parent.parent.parent / 'settings.json'
            if not settings_file.exists():
                return web.json_response({'work_items': [], 'total': 0})
            
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            enabled_projects = settings.get('enabledProjectDetails', [])
            if not enabled_projects:
                return web.json_response({'work_items': [], 'total': 0})
            
            # Fetch work items for each enabled project
            all_work_items = []
            work_items_by_project = {}
            
            for project in enabled_projects:
                project_id = project['projectId']
                project_name = project['projectName']
                
                try:
                    # Query for open work items in this project (New, Active, Resolved)
                    wiql = f"""
                    SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], 
                           [System.CreatedDate], [System.WorkItemType], [System.ChangedDate]
                    FROM WorkItems 
                    WHERE [System.TeamProject] = '{project_name}'
                      AND [System.State] IN ('New', 'Active', 'Resolved')
                    ORDER BY [System.CreatedDate] DESC
                    """
                    
                    # Execute query - need to use the async method
                    wiql_result = await azure_client.query_work_items_by_wiql(project_name, {'query': wiql})
                    
                    if wiql_result.get('workItems'):
                        # Get full work item details
                        ids = [wi['id'] for wi in wiql_result['workItems'][:50]]  # Limit to 50 items per project
                        work_items = []
                        for wi_id in ids:
                            wi = await azure_client.get_work_item(project_name, wi_id)
                            work_items.append(wi)
                        
                        project_items = []
                        for wi in work_items:
                            fields = wi.get('fields', {})
                            item_data = {
                                'id': wi.get('id'),
                                'title': fields.get('System.Title', 'No Title'),
                                'state': fields.get('System.State', 'Unknown'),
                                'assignedTo': fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned') if isinstance(fields.get('System.AssignedTo'), dict) else 'Unassigned',
                                'createdDate': fields.get('System.CreatedDate', ''),
                                'changedDate': fields.get('System.ChangedDate', ''),
                                'workItemType': fields.get('System.WorkItemType', 'Unknown'),
                                'project': project_name,
                                'projectId': project_id
                            }
                            project_items.append(item_data)
                            all_work_items.append(item_data)
                        
                        work_items_by_project[project_name] = project_items
                        
                        # Only log if count changed from last check
                        last_count_key = f"last_wi_count_{project_name}"
                        last_count = self.factory_state.get(last_count_key, -1)
                        if len(project_items) != last_count:
                            self.log_event("info", f"Found {len(project_items)} work items in {project_name}")
                            self.factory_state[last_count_key] = len(project_items)
                    
                except Exception as e:
                    import traceback
                    self.log_event("error", f"Failed to fetch work items from {project_name}: {str(e)}")
                    self.log_event("error", f"Traceback: {traceback.format_exc()}")
                    work_items_by_project[project_name] = []
            
            # Group by persona assignment (for now, we'll use a simple assignment logic)
            # In a real implementation, this would check actual Azure DevOps assignments
            work_items_by_persona = {
                'Steve': [],
                'Kav': [],
                'Unassigned': []
            }
            
            for item in all_work_items:
                assigned = False
                # Simple assignment logic - can be enhanced based on actual Azure DevOps data
                if 'security' in item['title'].lower() or 'threat' in item['title'].lower():
                    work_items_by_persona['Steve'].append(item)
                    assigned = True
                elif 'test' in item['title'].lower() or 'bug' in item['title'].lower():
                    work_items_by_persona['Kav'].append(item)
                    assigned = True
                
                if not assigned:
                    work_items_by_persona['Unassigned'].append(item)
            
            result = {
                'work_items': all_work_items,
                'total': len(all_work_items),
                'by_project': work_items_by_project,
                'by_persona': work_items_by_persona
            }
            
            # Cache the result
            self.factory_state[cache_key] = result
            self.factory_state[cache_timestamp_key] = now
            
            return web.json_response(result)
            
        except Exception as e:
            self.log_event("error", f"Failed to get work queue from Azure: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)

    async def get_completed_items_from_azure(self, request):
        """GET /api/completed-items-azure - Get completed work items from Azure DevOps for enabled projects"""
        try:
            if not self.factory_state.get("azure_client"):
                return web.json_response({'error': 'Azure DevOps not configured'}, status=400)
            
            # Check cache first - only refresh every 30 seconds
            cache_key = "azure_completed_items_cache"
            cache_timestamp_key = "azure_completed_items_cache_timestamp"
            
            now = datetime.now()
            cache_timestamp = self.factory_state.get(cache_timestamp_key)
            cached_data = self.factory_state.get(cache_key)
            
            if cached_data and cache_timestamp:
                # If cache is less than 30 seconds old, return cached data
                if (now - cache_timestamp).total_seconds() < 30:
                    return web.json_response(cached_data)
            
            # Cache is expired or doesn't exist, fetch fresh data
            
            azure_client = self.factory_state["azure_client"]
            
            # Load project configuration
            settings_file = Path(__file__).parent.parent.parent / 'settings.json'
            if not settings_file.exists():
                return web.json_response({'completed_items': [], 'total': 0})
            
            with open(settings_file, 'r') as f:
                settings = json.load(f)
            
            enabled_projects = settings.get('enabledProjectDetails', [])
            if not enabled_projects:
                return web.json_response({'completed_items': [], 'total': 0})
            
            # Fetch completed work items for each enabled project
            all_completed_items = []
            completed_items_by_project = {}
            
            for project in enabled_projects:
                project_id = project['projectId']
                project_name = project['projectName']
                
                try:
                    # Query for completed work items in this project (Closed, Done, Resolved)
                    wiql = f"""
                    SELECT [System.Id], [System.Title], [System.State], [System.AssignedTo], 
                           [System.CreatedDate], [System.WorkItemType], [System.ChangedDate]
                    FROM WorkItems 
                    WHERE [System.TeamProject] = '{project_name}'
                      AND [System.State] IN ('Closed', 'Done', 'Resolved')
                    ORDER BY [System.ChangedDate] DESC
                    """
                    
                    # Execute query - need to use the async method
                    wiql_result = await azure_client.query_work_items_by_wiql(project_name, {'query': wiql})
                    
                    if wiql_result.get('workItems'):
                        # Get full work item details
                        ids = [wi['id'] for wi in wiql_result['workItems'][:50]]  # Limit to 50 items per project
                        work_items = []
                        for wi_id in ids:
                            wi = await azure_client.get_work_item(project_name, wi_id)
                            work_items.append(wi)
                        
                        project_items = []
                        for wi in work_items:
                            fields = wi.get('fields', {})
                            # Use ChangedDate as the completion date
                            completed_date = fields.get('System.ChangedDate', '')
                            
                            item_data = {
                                'id': wi.get('id'),
                                'title': fields.get('System.Title', 'No Title'),
                                'state': fields.get('System.State', 'Unknown'),
                                'assignedTo': fields.get('System.AssignedTo', {}).get('displayName', 'Unassigned') if isinstance(fields.get('System.AssignedTo'), dict) else 'Unassigned',
                                'createdDate': fields.get('System.CreatedDate', ''),
                                'completedDate': completed_date,
                                'workItemType': fields.get('System.WorkItemType', 'Unknown'),
                                'project': project_name,
                                'projectId': project_id
                            }
                            project_items.append(item_data)
                            all_completed_items.append(item_data)
                        
                        completed_items_by_project[project_name] = project_items
                        
                        # Only log if count changed from last check
                        last_count_key = f"last_completed_count_{project_name}"
                        last_count = self.factory_state.get(last_count_key, -1)
                        if len(project_items) != last_count:
                            self.log_event("info", f"Found {len(project_items)} completed items in {project_name}")
                            self.factory_state[last_count_key] = len(project_items)
                    
                except Exception as e:
                    import traceback
                    self.log_event("error", f"Failed to fetch completed items from {project_name}: {str(e)}")
                    self.log_event("error", f"Traceback: {traceback.format_exc()}")
                    completed_items_by_project[project_name] = []
            
            # Group by persona assignment
            completed_items_by_persona = {
                'Steve': [],
                'Kav': [],
                'Unassigned': []
            }
            
            for item in all_completed_items:
                assigned = False
                # Simple assignment logic - can be enhanced based on actual Azure DevOps data
                if 'security' in item['title'].lower() or 'threat' in item['title'].lower():
                    completed_items_by_persona['Steve'].append(item)
                    assigned = True
                elif 'test' in item['title'].lower() or 'bug' in item['title'].lower():
                    completed_items_by_persona['Kav'].append(item)
                    assigned = True
                
                if not assigned:
                    completed_items_by_persona['Unassigned'].append(item)
            
            result = {
                'completed_items': all_completed_items,
                'total': len(all_completed_items),
                'by_project': completed_items_by_project,
                'by_persona': completed_items_by_persona
            }
            
            # Cache the result
            self.factory_state[cache_key] = result
            self.factory_state[cache_timestamp_key] = now
            
            return web.json_response(result)
            
        except Exception as e:
            self.log_event("error", f"Failed to get completed items from Azure: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)

    async def get_persona_logs(self, request, persona_name: str):
        """GET /api/personas/{persona_name}/logs - Get logs for specific persona"""
        try:
            limit = int(request.query.get('limit', 100))
            
            # Try to find an instance with this name
            instances = self.factory_state["processor_factory"].get_all_instances()
            display_name = persona_name
            for instance in instances.values():
                if instance.first_name.lower() == persona_name.lower():
                    display_name = instance.full_name
                    break
            logs = self.log_db.get_persona_logs(persona_name=display_name, limit=limit)
            
            return web.json_response({
                'status': 'success',
                'persona': persona_name,
                'display_name': display_name,
                'logs': logs
            })
        except Exception as e:
            self.log_event("error", f"Failed to get logs for persona {persona_name}: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
            
    async def delete_old_logs(self, request):
        """POST /api/logs/cleanup - Delete logs older than X days"""
        try:
            data = await request.json()
            days = data.get('days', 7)  # Default to 7 days
            
            if days < 1:
                return web.json_response({'error': 'Days must be at least 1'}, status=400)
            
            system_deleted, persona_deleted = self.log_db.delete_old_logs(days)
            
            self.log_event("info", f"Cleaned up logs older than {days} days: {system_deleted} system, {persona_deleted} persona")
            
            return web.json_response({
                'status': 'success',
                'message': f'Deleted {system_deleted} system logs and {persona_deleted} persona logs older than {days} days'
            })
        except Exception as e:
            self.log_event("error", f"Failed to delete old logs: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)

    async def get_workflows(self, request):
        """GET /api/workflows - Get all workflow definitions from YAML files"""
        try:
            workflows_dir = Path(__file__).parent.parent / 'workflows' / 'definitions'
            workflows = []
            
            # Get categories from database
            db_categories = self.workflow_categories_db.get_all_categories()
            categories = [cat['id'] for cat in db_categories]
            
            for category in categories:
                category_dir = workflows_dir / category
                # Ensure directory exists for each category
                category_dir.mkdir(parents=True, exist_ok=True)
                
                if category_dir.exists():
                    # Get all YAML files in this category
                    for yaml_file in sorted(category_dir.glob('*.yaml')):
                        try:
                            # Read raw YAML content
                            with open(yaml_file, 'r') as f:
                                raw_yaml_content = f.read()
                                
                            # Also parse it for metadata
                            workflow_data = yaml.safe_load(raw_yaml_content)
                                
                            # Extract workflow ID from filename (e.g., wf0-feature-development.yaml -> wf0)
                            workflow_id = yaml_file.stem.split('-')[0]
                            
                            # Extract name from metadata
                            metadata = workflow_data.get('metadata', {})
                            if metadata and 'name' in metadata:
                                # Use the human-readable name from metadata
                                clean_name = metadata['name']
                            elif metadata and 'id' in metadata:
                                # Fallback: generate from ID if name not present
                                name_parts = metadata['id'].split('-')
                                if name_parts[0].startswith('wf'):
                                    # Skip the wf# part
                                    clean_name = ' '.join(name_parts[1:]).title()
                                else:
                                    clean_name = ' '.join(name_parts).title()
                            else:
                                # Last fallback: use filename
                                base_name = yaml_file.stem
                                if base_name.startswith('wf') and '-' in base_name:
                                    name_parts = base_name.split('-')
                                    clean_name = ' '.join(name_parts[1:]).title()
                                else:
                                    clean_name = base_name.replace('-', ' ').title()
                            
                            formatted_workflow = {
                                'id': workflow_id,
                                'name': clean_name,
                                'category': category,
                                'description': self._format_workflow_description(workflow_data),
                                'raw_data': workflow_data,
                                'raw_yaml': raw_yaml_content
                            }
                            workflows.append(formatted_workflow)
                            
                        except Exception as e:
                            self.log_event("error", f"Failed to load workflow {yaml_file.name}: {str(e)}")
            
            # Sort by workflow ID (wf0, wf1, etc.)
            workflows.sort(key=lambda w: int(w['id'][2:]) if w['id'].startswith('wf') else 999)
            
            return web.json_response({
                'success': True,
                'workflows': workflows,
                'total': len(workflows)
            })
            
        except Exception as e:
            self.log_event("error", f"Failed to get workflows: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    def _format_workflow_description(self, workflow_data):
        """Format YAML workflow data into a readable description"""
        sections = []
        
        # Metadata section
        if 'metadata' in workflow_data:
            meta = workflow_data['metadata']
            sections.append("## Metadata")
            sections.append(f"- **Version**: {meta.get('version', '1.0.0')}")
            sections.append(f"- **Type**: {meta.get('type', 'Unknown')}")
            sections.append(f"- **Purpose**: {meta.get('purpose', 'No purpose defined')}")
            if 'average_duration' in meta:
                sections.append(f"- **Average Duration**: {meta['average_duration']}")
            sections.append("")
        
        # Description
        if 'description' in workflow_data:
            sections.append("## Description")
            sections.append(workflow_data['description'])
            sections.append("")
        
        # Inputs
        if 'inputs' in workflow_data:
            sections.append("## Inputs")
            for input_item in workflow_data['inputs']:
                sections.append(f"- **{input_item.get('name', 'Unknown')}**: {input_item.get('description', 'No description')}")
                if 'required' in input_item:
                    sections.append(f"  - Required: {input_item['required']}")
                if 'default' in input_item:
                    sections.append(f"  - Default: {input_item['default']}")
            sections.append("")
        
        # Prerequisites
        if 'prerequisites' in workflow_data:
            sections.append("## Prerequisites")
            for prereq in workflow_data['prerequisites']:
                sections.append(f"- {prereq}")
            sections.append("")
        
        # Steps
        if 'steps' in workflow_data:
            sections.append("## Workflow Steps")
            for i, step in enumerate(workflow_data['steps'], 1):
                sections.append(f"\n### Step {i}: {step.get('name', 'Unnamed Step')}")
                if 'description' in step:
                    sections.append(step['description'])
                
                # Format the action based on type
                if 'execute' in step:
                    sections.append("```yaml")
                    sections.append(f"execute: {step['execute']}")
                    if 'inputs' in step:
                        sections.append("inputs:")
                        for key, value in step['inputs'].items():
                            sections.append(f"  {key}: {value}")
                    sections.append("```")
                elif 'condition' in step:
                    sections.append("```yaml")
                    sections.append(f"condition: {step['condition']}")
                    if 'then' in step:
                        sections.append(f"then: {step['then']}")
                    if 'else' in step:
                        sections.append(f"else: {step['else']}")
                    sections.append("```")
                elif 'loop' in step:
                    sections.append("```yaml")
                    sections.append(f"loop: {step['loop']}")
                    sections.append("```")
        
        # Outputs
        if 'outputs' in workflow_data:
            sections.append("\n## Outputs")
            for output in workflow_data['outputs']:
                sections.append(f"- **{output.get('name', 'Unknown')}**: {output.get('description', 'No description')}")
            sections.append("")
        
        return '\n'.join(sections)
    
    async def get_workflow(self, request):
        """GET /api/workflows/{id} - Get a specific workflow by ID"""
        try:
            workflow_id = request.match_info['id']
            workflows_dir = Path(__file__).parent.parent / 'workflows' / 'definitions'
            
            # Get categories from database
            db_categories = self.workflow_categories_db.get_all_categories()
            categories = [cat['id'] for cat in db_categories]
            
            # Search for the workflow file in all categories
            for category in categories:
                category_dir = workflows_dir / category
                if category_dir.exists():
                    # Try different possible filenames
                    for pattern in [f"{workflow_id}-*.yaml", f"{workflow_id}.yaml"]:
                        matching_files = list(category_dir.glob(pattern))
                        if matching_files:
                            yaml_file = matching_files[0]
                            
                            # Read the YAML file
                            with open(yaml_file, 'r') as f:
                                raw_yaml_content = f.read()
                                workflow_data = yaml.safe_load(raw_yaml_content)
                            
                            # Get version history
                            history = self.workflow_history_db.get_workflow_history(workflow_id)
                            current_version = 1
                            if history:
                                current_version = max(h['version'] for h in history) + 1
                            
                            # Extract metadata
                            metadata = workflow_data.get('metadata', {})
                            name = metadata.get('name', workflow_id)
                            
                            return web.json_response({
                                'success': True,
                                'workflow': {
                                    'id': workflow_id,
                                    'name': name,
                                    'category': category,
                                    'filename': yaml_file.name,
                                    'version': current_version,
                                    'yaml': raw_yaml_content,
                                    'metadata': metadata
                                }
                            })
            
            # Workflow not found
            return web.json_response({
                'success': False,
                'error': f'Workflow {workflow_id} not found'
            }, status=404)
            
        except Exception as e:
            self.log_event("error", f"Failed to get workflow: {str(e)}")
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
    
    async def validate_workflow(self, request):
        """POST /api/workflows/validate - Validate a YAML workflow"""
        try:
            data = await request.json()
            workflow_yaml = data.get('yaml', '')
            
            if not workflow_yaml:
                return web.json_response({
                    'success': False,
                    'error': 'No YAML content provided'
                }, status=400)
            
            try:
                # Parse the YAML to validate it
                workflow_data = yaml.safe_load(workflow_yaml)
                
                # Basic validation checks
                errors = []
                warnings = []
                
                # Check required metadata fields
                if 'metadata' not in workflow_data:
                    errors.append("Missing 'metadata' section")
                else:
                    metadata = workflow_data['metadata']
                    required_fields = ['id', 'name', 'version', 'type']
                    for field in required_fields:
                        if field not in metadata:
                            errors.append(f"Missing required metadata field: '{field}'")
                    
                    # Check type is valid
                    if 'type' in metadata and metadata['type'] not in ['master', 'core', 'support']:
                        errors.append(f"Invalid workflow type: '{metadata['type']}'. Must be 'master', 'core', or 'support'")
                
                # Check for steps section
                if 'steps' not in workflow_data:
                    warnings.append("No 'steps' section defined")
                elif not isinstance(workflow_data['steps'], list):
                    errors.append("'steps' must be a list")
                else:
                    # Validate each step has required fields
                    for i, step in enumerate(workflow_data['steps']):
                        if 'id' not in step:
                            errors.append(f"Step {i+1} missing 'id' field")
                        if 'name' not in step:
                            warnings.append(f"Step {i+1} missing 'name' field")
                
                # Check for inputs section
                if 'inputs' in workflow_data and not isinstance(workflow_data['inputs'], list):
                    errors.append("'inputs' must be a list")
                
                # Check for outputs section
                if 'outputs' in workflow_data and not isinstance(workflow_data['outputs'], list):
                    errors.append("'outputs' must be a list")
                
                return web.json_response({
                    'success': len(errors) == 0,
                    'valid': len(errors) == 0,
                    'errors': errors,
                    'warnings': warnings,
                    'parsed_data': workflow_data if len(errors) == 0 else None
                })
                
            except yaml.YAMLError as e:
                return web.json_response({
                    'success': False,
                    'valid': False,
                    'errors': [f"YAML parsing error: {str(e)}"],
                    'warnings': []
                }, status=400)
                
        except Exception as e:
            self.log_event("error", f"Failed to validate workflow: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def save_workflow(self, request):
        """POST /api/workflows/save - Save or update a YAML workflow"""
        try:
            data = await request.json()
            workflow_id = data.get('id')
            workflow_yaml = data.get('yaml', '')
            
            if not workflow_id or not workflow_yaml:
                return web.json_response({
                    'success': False,
                    'error': 'Missing workflow ID or YAML content'
                }, status=400)
            
            # Parse YAML to get metadata
            try:
                workflow_data = yaml.safe_load(workflow_yaml)
            except yaml.YAMLError as e:
                return web.json_response({
                    'success': False,
                    'error': f"Invalid YAML: {str(e)}"
                }, status=400)
            
            # Get workflow type from metadata
            workflow_type = workflow_data.get('metadata', {}).get('type', 'core')
            if workflow_type not in ['master', 'core', 'support']:
                workflow_type = 'core'  # Default to core if invalid
            
            # Determine filename from metadata
            workflow_name = workflow_data.get('metadata', {}).get('name', 'unnamed')
            # Convert name to filename format (lowercase, replace spaces with hyphens)
            filename_base = workflow_name.lower().replace(' ', '-').replace('_', '-')
            # Remove 'workflow' from the end if it exists
            if filename_base.endswith('-workflow'):
                filename_base = filename_base[:-9]
            
            # Construct filename: wfX-name.yaml
            filename = f"{workflow_id}-{filename_base}.yaml"
            
            # Build file path
            workflows_dir = Path(__file__).parent.parent / 'workflows' / 'definitions' / workflow_type
            file_path = workflows_dir / filename
            
            # Create directory if it doesn't exist
            workflows_dir.mkdir(parents=True, exist_ok=True)
            
            # Check if this is a rename (old file exists with different name)
            old_files = list(workflows_dir.glob(f"{workflow_id}-*.yaml"))
            for old_file in old_files:
                if old_file.name != filename:
                    # Delete old file if it has a different name
                    old_file.unlink()
                    self.log_event("info", f"Deleted old workflow file: {old_file.name}")
            
            # Save the workflow
            with open(file_path, 'w') as f:
                f.write(workflow_yaml)
            
            # Store version history
            version = workflow_data.get('metadata', {}).get('version', '1.0.0')
            change_notes = data.get('changeNotes', '')
            try:
                self.workflows_db.add_version(
                    workflow_id=workflow_id,
                    version=version,
                    yaml_content=workflow_yaml,
                    change_notes=change_notes,
                    created_by='user'
                )
                self.log_event("info", f"Saved workflow {workflow_id} version {version} to history")
            except Exception as e:
                self.log_event("warning", f"Failed to save workflow history: {str(e)}")
                # Continue even if history fails
            
            self.log_event("info", f"Saved workflow {workflow_id} to {file_path}")
            
            return web.json_response({
                'success': True,
                'message': f'Workflow {workflow_id} saved successfully',
                'file_path': str(file_path.relative_to(Path(__file__).parent.parent.parent))
            })
            
        except Exception as e:
            self.log_event("error", f"Failed to save workflow: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def delete_workflow(self, request):
        """DELETE /api/workflows/{id} - Delete a workflow"""
        try:
            workflow_id = request.match_info.get('id')
            
            if not workflow_id:
                return web.json_response({
                    'success': False,
                    'error': 'No workflow ID provided'
                }, status=400)
            
            # Search for the workflow file in all categories
            workflows_dir = Path(__file__).parent.parent / 'workflows' / 'definitions'
            workflow_file = None
            
            for category in ['master', 'core', 'support']:
                category_dir = workflows_dir / category
                if category_dir.exists():
                    # Look for files matching the workflow ID
                    matching_files = list(category_dir.glob(f"{workflow_id}-*.yaml"))
                    if matching_files:
                        workflow_file = matching_files[0]  # Take the first match
                        break
            
            if not workflow_file:
                return web.json_response({
                    'success': False,
                    'error': f'Workflow {workflow_id} not found'
                }, status=404)
            
            # Delete the file
            workflow_file.unlink()
            self.log_event("info", f"Deleted workflow {workflow_id} from {workflow_file}")
            
            return web.json_response({
                'success': True,
                'message': f'Workflow {workflow_id} deleted successfully'
            })
            
        except Exception as e:
            self.log_event("error", f"Failed to delete workflow: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_workflow_history(self, request):
        """GET /api/workflows/{id}/history - Get workflow version history"""
        try:
            workflow_id = request.match_info.get('id')
            
            if not workflow_id:
                return web.json_response({
                    'success': False,
                    'error': 'No workflow ID provided'
                }, status=400)
            
            # Get history from database
            history = self.workflows_db.get_history(workflow_id, limit=20)
            
            # Format the history for the frontend
            formatted_history = []
            for entry in history:
                formatted_history.append({
                    'id': entry['id'],
                    'version': entry['version'],
                    'changeNotes': entry.get('change_notes', ''),
                    'createdAt': entry['created_at'],
                    'createdBy': entry.get('created_by', 'system'),
                    'yamlContent': entry['yaml_content']
                })
            
            return web.json_response({
                'success': True,
                'history': formatted_history,
                'workflowId': workflow_id
            })
            
        except Exception as e:
            self.log_event("error", f"Failed to get workflow history: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    # Workflow Category endpoints
    
    async def get_workflow_categories(self, request):
        """GET /api/workflows/categories - Get all workflow categories"""
        try:
            categories = self.workflow_categories_db.get_all_categories()
            return web.json_response({
                'categories': categories,
                'total': len(categories)
            })
        except Exception as e:
            self.log_event("error", f"Failed to get workflow categories: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def create_workflow_category(self, request):
        """POST /api/workflows/categories - Create a new workflow category"""
        try:
            data = await request.json()
            category_id = data.get('id')
            name = data.get('name')
            description = data.get('description', '')
            
            if not category_id or not name:
                return web.json_response({
                    'error': 'Category ID and name are required'
                }, status=400)
            
            # Sanitize category ID (alphanumeric and hyphens only)
            import re
            if not re.match(r'^[a-z0-9-]+$', category_id):
                return web.json_response({
                    'error': 'Category ID must contain only lowercase letters, numbers, and hyphens'
                }, status=400)
            
            result = self.workflow_categories_db.create_category(
                category_id=category_id,
                name=name,
                description=description
            )
            
            # Create the corresponding directory for the category
            workflows_dir = Path(__file__).parent.parent / 'workflows' / 'definitions' / category_id
            workflows_dir.mkdir(parents=True, exist_ok=True)
            
            self.log_event("info", f"Created workflow category: {category_id}")
            return web.json_response(result)
            
        except ValueError as e:
            return web.json_response({'error': str(e)}, status=400)
        except Exception as e:
            self.log_event("error", f"Failed to create workflow category: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def update_workflow_category(self, request):
        """PUT /api/workflows/categories/{id} - Update a workflow category"""
        try:
            category_id = request.match_info.get('id')
            data = await request.json()
            
            result = self.workflow_categories_db.update_category(
                category_id=category_id,
                **data
            )
            
            self.log_event("info", f"Updated workflow category: {category_id}")
            return web.json_response(result)
            
        except ValueError as e:
            return web.json_response({'error': str(e)}, status=400)
        except Exception as e:
            self.log_event("error", f"Failed to update workflow category: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def delete_workflow_category(self, request):
        """DELETE /api/workflows/categories/{id} - Delete a workflow category"""
        try:
            category_id = request.match_info.get('id')
            
            # Check if any workflows use this category
            workflows_dir = Path(__file__).parent.parent / 'workflows' / 'definitions' / category_id
            if workflows_dir.exists() and any(workflows_dir.glob('*.yaml')):
                return web.json_response({
                    'error': f'Cannot delete category "{category_id}" - it contains workflows'
                }, status=400)
            
            result = self.workflow_categories_db.delete_category(category_id)
            
            self.log_event("info", f"Deleted workflow category: {category_id}")
            return web.json_response(result)
            
        except ValueError as e:
            return web.json_response({'error': str(e)}, status=400)
        except Exception as e:
            self.log_event("error", f"Failed to delete workflow category: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def reorder_workflow_categories(self, request):
        """PUT /api/workflows/categories/reorder - Reorder workflow categories"""
        try:
            data = await request.json()
            category_order = data.get('order', [])
            
            if not isinstance(category_order, list):
                return web.json_response({
                    'error': 'Order must be a list of category IDs'
                }, status=400)
            
            result = self.workflow_categories_db.reorder_categories(category_order)
            
            self.log_event("info", "Reordered workflow categories")
            return web.json_response(result)
            
        except Exception as e:
            self.log_event("error", f"Failed to reorder workflow categories: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    # Workflow Diagram endpoints
    
    async def get_workflow_diagram(self, request):
        """GET /api/workflows/{id}/diagrams/{type} - Get a specific diagram"""
        try:
            workflow_id = request.match_info.get('id')
            diagram_type = request.match_info.get('type')
            
            if diagram_type not in ['orchestration', 'interaction', 'raci']:
                return web.json_response({
                    'error': 'Invalid diagram type. Must be orchestration, interaction, or raci'
                }, status=400)
            
            diagram = self.workflow_diagrams_db.get_diagram(workflow_id, diagram_type)
            
            if diagram:
                return web.json_response(diagram)
            else:
                return web.json_response({
                    'error': f'No {diagram_type} diagram found for workflow {workflow_id}'
                }, status=404)
        except Exception as e:
            self.log_event("error", f"Failed to get workflow diagram: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def save_workflow_diagram(self, request):
        """POST /api/workflows/{id}/diagrams/{type} - Save/update a diagram"""
        try:
            workflow_id = request.match_info.get('id')
            diagram_type = request.match_info.get('type')
            data = await request.json()
            
            if diagram_type not in ['orchestration', 'interaction', 'raci']:
                return web.json_response({
                    'error': 'Invalid diagram type. Must be orchestration, interaction, or raci'
                }, status=400)
            
            content = data.get('content')
            format = data.get('format', 'mermaid' if diagram_type != 'raci' else 'html')
            metadata = data.get('metadata', {})
            
            if not content:
                return web.json_response({
                    'error': 'Diagram content is required'
                }, status=400)
            
            diagram_id = self.workflow_diagrams_db.save_diagram(
                workflow_id=workflow_id,
                diagram_type=diagram_type,
                content=content,
                format=format,
                metadata=metadata
            )
            
            self.log_event("info", f"Saved {diagram_type} diagram for workflow {workflow_id}")
            return web.json_response({
                'id': diagram_id,
                'message': f'{diagram_type.capitalize()} diagram saved successfully'
            })
            
        except Exception as e:
            self.log_event("error", f"Failed to save workflow diagram: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_workflow_diagrams(self, request):
        """GET /api/workflows/{id}/diagrams - Get all diagrams for a workflow"""
        try:
            workflow_id = request.match_info.get('id')
            diagrams = self.workflow_diagrams_db.get_workflow_diagrams(workflow_id)
            
            return web.json_response({
                'workflow_id': workflow_id,
                'diagrams': diagrams,
                'total': len(diagrams)
            })
        except Exception as e:
            self.log_event("error", f"Failed to get workflow diagrams: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def delete_workflow_diagram(self, request):
        """DELETE /api/workflows/{id}/diagrams/{type} - Delete a diagram"""
        try:
            workflow_id = request.match_info.get('id')
            diagram_type = request.match_info.get('type')
            
            if self.workflow_diagrams_db.delete_diagram(workflow_id, diagram_type):
                self.log_event("info", f"Deleted {diagram_type} diagram for workflow {workflow_id}")
                return web.json_response({
                    'message': f'{diagram_type.capitalize()} diagram deleted successfully'
                })
            else:
                return web.json_response({
                    'error': f'No {diagram_type} diagram found for workflow {workflow_id}'
                }, status=404)
                
        except Exception as e:
            self.log_event("error", f"Failed to delete workflow diagram: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    # System Prompt endpoints
    
    async def get_system_prompt(self, request):
        """GET /api/prompts/system - Get current system prompt"""
        try:
            prompt = self.prompts_db.get_system_prompt()
            if prompt:
                return web.json_response(prompt)
            else:
                return web.json_response({
                    'error': 'No system prompt found'
                }, status=404)
        except Exception as e:
            self.log_event("error", f"Failed to get system prompt: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def update_system_prompt(self, request):
        """PUT /api/prompts/system - Update system prompt"""
        try:
            data = await request.json()
            prompt_text = data.get('prompt')
            
            if not prompt_text:
                return web.json_response({
                    'error': 'Prompt text is required'
                }, status=400)
            
            # Update prompt - user info could come from auth in the future
            result = self.prompts_db.update_system_prompt(
                prompt=prompt_text,
                created_by=data.get('created_by', 'user'),
                change_notes=data.get('change_notes', None)
            )
            
            self.log_event("info", f"System prompt updated to version {result['version']}")
            return web.json_response(result)
            
        except Exception as e:
            self.log_event("error", f"Failed to update system prompt: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_prompt_history(self, request):
        """GET /api/prompts/system/history - Get prompt version history"""
        try:
            limit = int(request.query.get('limit', 50))
            history = self.prompts_db.get_prompt_history(limit=limit)
            
            return web.json_response({
                'history': history,
                'count': len(history)
            })
        except Exception as e:
            self.log_event("error", f"Failed to get prompt history: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def get_prompt_version(self, request):
        """GET /api/prompts/system/version/{version} - Get specific version"""
        try:
            version = int(request.match_info['version'])
            prompt = self.prompts_db.get_prompt_version(version)
            
            if prompt:
                return web.json_response(prompt)
            else:
                return web.json_response({
                    'error': f'Version {version} not found'
                }, status=404)
        except Exception as e:
            self.log_event("error", f"Failed to get prompt version: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def revert_prompt_version(self, request):
        """POST /api/prompts/system/revert/{version} - Revert to specific version"""
        try:
            version = int(request.match_info['version'])
            data = await request.json() if request.can_read_body else {}
            
            result = self.prompts_db.revert_to_version(
                version=version,
                created_by=data.get('created_by', 'user')
            )
            
            self.log_event("info", f"System prompt reverted to version {version}")
            return web.json_response(result)
            
        except ValueError as e:
            return web.json_response({
                'error': str(e)
            }, status=404)
        except Exception as e:
            self.log_event("error", f"Failed to revert prompt version: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def export_system_prompt(self, request):
        """GET /api/prompts/system/export - Export current system prompt"""
        try:
            prompt = self.prompts_db.get_system_prompt()
            if not prompt:
                return web.json_response({
                    'error': 'No system prompt found'
                }, status=404)
            
            # Export as JSON with metadata
            export_data = {
                'prompt': prompt['prompt'],
                'version': prompt['version'],
                'exported_at': datetime.now().isoformat(),
                'metadata': {
                    'created_at': prompt['created_at'],
                    'updated_at': prompt['updated_at']
                }
            }
            
            return web.json_response(export_data)
            
        except Exception as e:
            self.log_event("error", f"Failed to export system prompt: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)
    
    async def import_system_prompt(self, request):
        """POST /api/prompts/system/import - Import system prompt"""
        try:
            data = await request.json()
            prompt_text = data.get('prompt')
            
            if not prompt_text:
                return web.json_response({
                    'error': 'Prompt text is required'
                }, status=400)
            
            # Import as new version
            result = self.prompts_db.update_system_prompt(
                prompt=prompt_text,
                created_by=data.get('created_by', 'import'),
                change_notes=f"Imported from {data.get('source', 'external source')}"
            )
            
            self.log_event("info", f"System prompt imported as version {result['version']}")
            return web.json_response(result)
            
        except Exception as e:
            self.log_event("error", f"Failed to import system prompt: {str(e)}")
            return web.json_response({'error': str(e)}, status=500)


def create_app():
    """Create the web application"""
    api = RealFactoryAPI()
    
    app = web.Application()
    app.router.add_get('/api/status', api.get_status)
    app.router.add_get('/api/personas', api.get_personas)
    app.router.add_get('/api/work-queue', api.get_work_queue)
    app.router.add_post('/api/work-queue', api.add_work_item)
    app.router.add_get('/api/logs', api.get_logs)
    app.router.add_get('/api/personas/{persona_name}/logs', api.get_persona_logs)
    app.router.add_post('/api/logs/cleanup', api.delete_old_logs)
    app.router.add_post('/api/factory/start', api.start_factory)
    app.router.add_post('/api/factory/stop', api.stop_factory)
    app.router.add_get('/api/settings', api.get_settings)
    app.router.add_post('/api/settings', api.save_settings)
    app.router.add_post('/api/test-connection', api.test_connection)
    app.router.add_post('/api/project-configuration', api.save_project_configuration)
    app.router.add_get('/api/project-configuration', api.get_project_configuration)
    app.router.add_post('/api/check-team-membership', api.check_team_membership)
    app.router.add_get('/api/completed-items', api.get_completed_items)
    app.router.add_get('/api/work-queue-azure', api.get_work_queue_from_azure)
    app.router.add_get('/api/completed-items-azure', api.get_completed_items_from_azure)
    app.router.add_get('/api/workflows', api.get_workflows)
    
    # Workflow Category routes - MUST come before {id} routes to avoid conflicts
    app.router.add_get('/api/workflows/categories', api.get_workflow_categories)
    app.router.add_post('/api/workflows/categories', api.create_workflow_category)
    app.router.add_put('/api/workflows/categories/reorder', api.reorder_workflow_categories)
    app.router.add_put('/api/workflows/categories/{id}', api.update_workflow_category)
    app.router.add_delete('/api/workflows/categories/{id}', api.delete_workflow_category)
    
    # Workflow routes with {id} parameters - MUST come after specific routes
    app.router.add_get('/api/workflows/{id}', api.get_workflow)
    app.router.add_post('/api/workflows/validate', api.validate_workflow)
    app.router.add_post('/api/workflows/save', api.save_workflow)
    app.router.add_delete('/api/workflows/{id}', api.delete_workflow)
    app.router.add_get('/api/workflows/{id}/history', api.get_workflow_history)
    
    # Workflow Diagram routes
    app.router.add_get('/api/workflows/{id}/diagrams', api.get_workflow_diagrams)
    app.router.add_get('/api/workflows/{id}/diagrams/{type}', api.get_workflow_diagram)
    app.router.add_post('/api/workflows/{id}/diagrams/{type}', api.save_workflow_diagram)
    app.router.add_delete('/api/workflows/{id}/diagrams/{type}', api.delete_workflow_diagram)
    
    # System Prompt routes
    app.router.add_get('/api/prompts/system', api.get_system_prompt)
    app.router.add_put('/api/prompts/system', api.update_system_prompt)
    app.router.add_get('/api/prompts/system/history', api.get_prompt_history)
    app.router.add_get('/api/prompts/system/version/{version}', api.get_prompt_version)
    app.router.add_post('/api/prompts/system/revert/{version}', api.revert_prompt_version)
    app.router.add_get('/api/prompts/system/export', api.export_system_prompt)
    app.router.add_post('/api/prompts/system/import', api.import_system_prompt)
    
    # Register persona API routes
    register_persona_routes(app)
    
    # Add CORS headers
    @web.middleware
    async def cors_middleware(request, handler):
        if request.method == 'OPTIONS':
            response = web.Response(status=200)
        else:
            response = await handler(request)
        
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
        
    app.middlewares.append(cors_middleware)
    
    return app


async def main():
    """Main entry point"""
    app = create_app()
    
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    
    logger.info("Starting Real AI Factory API on http://localhost:8080")
    logger.info("This version uses actual persona processors!")
    logger.info("Currently implemented personas: Steve (Security Architect), Kav (Test Engineer)")
    logger.info("")
    logger.info("Endpoints:")
    logger.info("  GET  /api/status        - Factory status")
    logger.info("  GET  /api/personas      - List all personas with real status")
    logger.info("  GET  /api/work-queue    - View work queue")
    logger.info("  POST /api/work-queue    - Add work item")
    logger.info("  GET  /api/logs          - System logs")
    logger.info("  POST /api/factory/start - Start factory")
    logger.info("  POST /api/factory/stop  - Stop factory")
    
    await site.start()
    
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == '__main__':
    asyncio.run(main())