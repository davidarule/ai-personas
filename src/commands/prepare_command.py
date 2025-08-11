#!/usr/bin/env python3
"""
/prepare Command Implementation
Saves current session state before compaction or session end

This command captures:
1. Current task and progress
2. Active todos and their status
3. Key decisions made during session
4. Next steps to take
5. Important context and discoveries
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class PrepareCommand:
    """Save session state for later restoration"""
    
    def __init__(self):
        self.session_data = {
            "timestamp": datetime.now().isoformat(),
            "current_task": None,
            "todos": [],
            "decisions": [],
            "next_steps": [],
            "context": {},
            "discoveries": []
        }
        
    async def execute(self, 
                     current_task: str,
                     todos: List[Dict[str, Any]],
                     decisions: List[str],
                     next_steps: List[str],
                     context: Dict[str, Any],
                     discoveries: List[str]) -> str:
        """Execute the /prepare command"""
        
        try:
            # Store all session data
            self.session_data.update({
                "timestamp": datetime.now().isoformat(),
                "current_task": current_task,
                "todos": todos,
                "decisions": decisions,
                "next_steps": next_steps,
                "context": context,
                "discoveries": discoveries
            })
            
            # Save to MCP Memory as SessionState entity
            session_saved = await self._save_to_memory_mcp()
            
            # Also save to local file as backup
            file_saved = await self._save_to_file()
            
            # Generate confirmation
            summary = self._generate_summary()
            
            result = ["Session state prepared for compaction/restart:"]
            if session_saved:
                result.append("✓ Saved to Memory MCP")
            if file_saved:
                result.append("✓ Saved to local backup")
            result.append("")
            result.append(summary)
            
            return "\n".join(result)
            
        except Exception as e:
            logger.error(f"Error in /prepare command: {e}")
            return f"Error preparing session state: {str(e)}"
    
    async def _save_to_memory_mcp(self) -> bool:
        """Save session state to Memory MCP"""
        try:
            # First, delete any existing CurrentSessionState entity
            import sys
            if 'mcp__memory__search_nodes' in sys.modules.get('__main__', {}).__dict__:
                # Search for existing session state
                existing = mcp__memory__search_nodes("CurrentSessionState")
                if existing and existing.get('nodes'):
                    # Delete existing session state
                    if 'mcp__memory__delete_entities' in sys.modules.get('__main__', {}).__dict__:
                        mcp__memory__delete_entities(["CurrentSessionState"])
                        logger.info("Deleted previous session state")
            
            # Create the entity structure
            entity = {
                "name": "CurrentSessionState",
                "entityType": "SessionState",
                "observations": [
                    f"Session from {self.session_data['timestamp']}",
                    f"Current task: {self.session_data['current_task']}",
                    f"Todos: {len(self.session_data['todos'])} items",
                    f"Next steps: {len(self.session_data['next_steps'])} items",
                    f"Decisions made: {len(self.session_data['decisions'])}",
                    f"Discoveries: {len(self.session_data['discoveries'])}"
                ]
            }
            
            # Store full data as JSON observation
            entity["observations"].append(json.dumps(self.session_data))
            
            # Actually save to Memory MCP if available
            if 'mcp__memory__create_entities' in sys.modules.get('__main__', {}).__dict__:
                result = mcp__memory__create_entities([entity])
                logger.info("Session state saved to Memory MCP")
                return True
            else:
                logger.warning("MCP functions not available, session state prepared but not saved")
                return False
            
        except Exception as e:
            logger.error(f"Failed to save to Memory MCP: {e}")
            return False
    
    async def _save_to_file(self) -> bool:
        """Save session state to local file"""
        try:
            # Create .memory directory if it doesn't exist
            memory_dir = Path(".memory")
            memory_dir.mkdir(exist_ok=True)
            
            # Save session state
            session_file = memory_dir / "session_state.json"
            with open(session_file, "w") as f:
                json.dump(self.session_data, f, indent=2)
            
            logger.info(f"Session state saved to {session_file}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save to file: {e}")
            return False
    
    def _generate_summary(self) -> str:
        """Generate a summary of what was saved"""
        parts = [f"Session prepared at: {self.session_data['timestamp']}"]
        
        if self.session_data['current_task']:
            parts.append(f"\nCurrent Task: {self.session_data['current_task']}")
        
        if self.session_data['todos']:
            parts.append(f"\nTodos ({len(self.session_data['todos'])} items):")
            for todo in self.session_data['todos'][:3]:  # Show first 3
                status_emoji = {
                    'completed': '✅',
                    'in_progress': '🔄',
                    'pending': '⏳'
                }.get(todo.get('status', 'pending'), '❓')
                parts.append(f"  {status_emoji} {todo.get('content', 'Unknown')}")
            if len(self.session_data['todos']) > 3:
                parts.append(f"  ... and {len(self.session_data['todos']) - 3} more")
        
        if self.session_data['next_steps']:
            parts.append(f"\nNext Steps:")
            for step in self.session_data['next_steps'][:3]:
                parts.append(f"  → {step}")
        
        if self.session_data['discoveries']:
            parts.append(f"\nKey Discoveries:")
            for discovery in self.session_data['discoveries'][:2]:
                parts.append(f"  💡 {discovery}")
        
        return "\n".join(parts)


# Example usage for AI Personas current session
async def prepare_current_session() -> str:
    """Prepare the current AI Personas session"""
    
    current_task = "Fixed AI Factory dashboard color scheme and persona status display"
    
    todos = [
        {"content": "Fix dashboard startup issues", "status": "completed", "priority": "high"},
        {"content": "Update color scheme to match user expectations", "status": "completed", "priority": "high"},
        {"content": "Add CSS for not_implemented status", "status": "completed", "priority": "medium"}
    ]
    
    decisions = [
        "Moved simple_factory_api.py to archive as it had mock data",
        "Fixed color scheme: Red=Stopped, Blue=Idle, Green=Working, Yellow=Error/Blocked",
        "Fixed logic so stopped factory shows personas as stopped (red) not idle"
    ]
    
    next_steps = [
        "Implement remaining 11 persona processors",
        "Create WorkItemRouter for automatic Azure DevOps polling",
        "Add WebSocket support for real-time dashboard updates",
        "Implement persona collaboration mechanisms"
    ]
    
    context = {
        "api_running": True,
        "api_port": 8080,
        "dashboard_port": 3000,
        "dashboard_file": "/opt/ai-personas/index.html",
        "active_personas": ["steve", "kav"],
        "branch": "feature/wi-501-stevebot-20250804-054020"
    }
    
    discoveries = [
        "simple_factory_api.py was showing mock data instead of real processor states",
        "Missing orchestration/azure_devops_api_client.py was in archive directory",
        "Dashboard needed proper status mapping: factory stopped → personas stopped"
    ]
    
    prepare_cmd = PrepareCommand()
    return await prepare_cmd.execute(
        current_task=current_task,
        todos=todos,
        decisions=decisions,
        next_steps=next_steps,
        context=context,
        discoveries=discoveries
    )


if __name__ == "__main__":
    import asyncio
    result = asyncio.run(prepare_current_session())
    print(result)