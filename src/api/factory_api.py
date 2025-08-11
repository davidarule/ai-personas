#!/usr/bin/env python3
"""
AI Factory API Service
Provides real endpoints for factory state, work queue, and persona management
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from aiohttp import web
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personas.processor_factory import ProcessorFactory
from work_queue.work_queue import WorkQueue
from orchestration.work_item_router import WorkItemRouter
from azure_devops.multi_project_client import MultiProjectClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FactoryAPI:
    """API service for AI Factory operations"""
    
    def __init__(self):
        self.factory_state = {
            "running": False,
            "start_time": None,
            "personas": {},
            "work_queue": WorkQueue(),
            "processor_factory": ProcessorFactory(),
            "router": None,
            "azure_client": None
        }
        self.system_logs = []
        
    def log_event(self, level: str, message: str):
        """Log system events"""
        self.system_logs.append({
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message
        })
        # Keep only last 1000 logs
        if len(self.system_logs) > 1000:
            self.system_logs.pop(0)
            
    async def initialize(self):
        """Initialize factory components"""
        try:
            # Initialize Azure DevOps client
            config_path = Path(__file__).parent.parent.parent / "test_config.json"
            if config_path.exists():
                with open(config_path) as f:
                    config = json.load(f)
                    self.factory_state["azure_client"] = MultiProjectClient(
                        organization=config.get("organization", ""),
                        personal_access_token=config.get("pat", "")
                    )
                    
            # Initialize work item router
            self.factory_state["router"] = WorkItemRouter()
            
            # Initialize personas
            persona_types = [
                "dave", "steve", "kav", "lachlan", "jordan", "puck",
                "shaun", "matt", "moby", "ruley", "brumbie", "claude", "laureen"
            ]
            
            for persona_type in persona_types:
                try:
                    processor = self.factory_state["processor_factory"].create_processor(persona_type)
                    self.factory_state["personas"][persona_type] = {
                        "processor": processor,
                        "info": processor.get_info(),
                        "state": {
                            "status": "idle",
                            "current_work_item": None,
                            "work_items_completed": 0,
                            "outputs_generated": []
                        }
                    }
                    self.log_event("info", f"Initialized {persona_type} persona")
                except Exception as e:
                    self.log_event("error", f"Failed to initialize {persona_type}: {str(e)}")
                    
            self.log_event("success", "AI Factory API initialized")
            return True
            
        except Exception as e:
            self.log_event("error", f"Failed to initialize: {str(e)}")
            return False
            
    async def get_status(self, request):
        """GET /api/status - Get factory status"""
        data = {
            "factory_running": self.factory_state["running"],
            "personas_count": len(self.factory_state["personas"]),
            "work_queue_size": self.factory_state["work_queue"].size(),
            "system_time": datetime.now().isoformat()
        }
        return web.json_response(data)
        
    async def get_personas(self, request):
        """GET /api/personas - Get all personas"""
        personas_data = {}
        for persona_id, persona in self.factory_state["personas"].items():
            personas_data[persona_id] = {
                "info": persona["info"],
                "state": persona["state"]
            }
        return web.json_response(personas_data)
        
    async def get_work_queue(self, request):
        """GET /api/work-queue - Get work queue status"""
        queue = self.factory_state["work_queue"]
        data = {
            "size": queue.size(),
            "items": queue.get_all_items()
        }
        return web.json_response(data)
        
    async def add_work_item(self, request):
        """POST /api/work-queue - Add a work item"""
        try:
            data = await request.json()
            item_id = await self.factory_state["work_queue"].add_item(data)
            self.log_event("info", f"Added work item {item_id}")
            return web.json_response({"id": item_id, "status": "added"})
        except Exception as e:
            return web.json_response({"error": str(e)}, status=400)
        
    async def get_system_logs(self, request):
        """GET /api/logs - Get system logs"""
        limit = int(request.query.get('limit', 100))
        return web.json_response(self.system_logs[-limit:])
        
    async def start_factory(self, request):
        """POST /api/factory/start - Start the factory"""
        if not self.factory_state["running"]:
            self.factory_state["running"] = True
            self.factory_state["start_time"] = datetime.now()
            self.log_event("success", "Factory started")
            # Start processing loop
            asyncio.create_task(self.processing_loop())
        return web.json_response({"status": "started"})
        
    async def stop_factory(self, request):
        """POST /api/factory/stop - Stop the factory"""
        self.factory_state["running"] = False
        self.log_event("warning", "Factory stopped")
        
        # Reset all personas to idle
        for persona in self.factory_state["personas"].values():
            persona["state"]["status"] = "idle"
            persona["state"]["current_work_item"] = None
            
        return web.json_response({"status": "stopped"})
        
    async def processing_loop(self):
        """Main processing loop for work items"""
        while self.factory_state["running"]:
            try:
                # Check for work items
                work_item = await self.factory_state["work_queue"].get_next_item()
                if work_item:
                    # Find available persona
                    for persona_id, persona in self.factory_state["personas"].items():
                        if persona["state"]["status"] == "idle":
                            # Assign work
                            persona["state"]["status"] = "working"
                            persona["state"]["current_work_item"] = work_item
                            self.log_event("info", f"{persona_id} started working on item {work_item.get('id', 'unknown')}")
                            
                            # Process work item asynchronously
                            asyncio.create_task(self.process_work_item(persona_id, work_item))
                            break
                            
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except Exception as e:
                self.log_event("error", f"Processing loop error: {str(e)}")
                await asyncio.sleep(5)
                
    async def process_work_item(self, persona_id: str, work_item: Dict):
        """Process a single work item"""
        persona = self.factory_state["personas"][persona_id]
        try:
            # Simulate processing (in real implementation, call processor.process)
            await asyncio.sleep(10)  # Simulate work
            
            # Mark complete
            persona["state"]["status"] = "idle"
            persona["state"]["current_work_item"] = None
            persona["state"]["work_items_completed"] += 1
            
            self.log_event("success", f"{persona_id} completed work item")
            
        except Exception as e:
            persona["state"]["status"] = "error"
            self.log_event("error", f"{persona_id} failed: {str(e)}")


def create_app():
    """Create the web application"""
    api = FactoryAPI()
    
    app = web.Application()
    app.router.add_get('/api/status', api.get_status)
    app.router.add_get('/api/personas', api.get_personas)
    app.router.add_get('/api/work-queue', api.get_work_queue)
    app.router.add_post('/api/work-queue', api.add_work_item)
    app.router.add_get('/api/logs', api.get_system_logs)
    app.router.add_post('/api/factory/start', api.start_factory)
    app.router.add_post('/api/factory/stop', api.stop_factory)
    
    # Store api instance for initialization
    app['api'] = api
    
    return app


async def main():
    """Main entry point"""
    app = create_app()
    
    # Initialize the API
    await app['api'].initialize()
    
    # Start server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    
    logger.info("Starting AI Factory API on http://localhost:8080")
    await site.start()
    
    # Keep running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        logger.info("Shutting down...")


if __name__ == '__main__':
    asyncio.run(main())