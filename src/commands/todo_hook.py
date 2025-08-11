"""
Todo Hook for automatic session state saving
Integrates with TodoWrite tool to save complete todo items
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Any

from .session_state_manager import get_session_manager

logger = logging.getLogger(__name__)


class TodoHook:
    """Automatically saves todo state when TodoWrite is used"""
    
    def __init__(self):
        self.session_manager = get_session_manager()
    
    def on_todo_update(self, todos: List[Dict[str, Any]], 
                      current_task: str = None) -> None:
        """
        Called whenever todos are updated via TodoWrite
        
        Args:
            todos: Complete list of todo items from TodoWrite
            current_task: Description of current task
        """
        try:
            # Extract context from current environment
            context = {
                "project": "AI Personas",
                "working_dir": "/opt/ai-personas",
                "api_port": 8080,
                "dashboard_port": 3000,
                "azure_org": "data6",
                "enabled_projects": ["AI-Personas-Test-Sandbox", "AI-Personas-Test-Sandbox-2"]
            }
            
            # Save complete todo state
            saved_state = self.session_manager.save_session_state(
                todos=todos,
                current_task=current_task,
                context=context
            )
            
            # Also prepare for Memory MCP save
            self._prepare_memory_mcp_entity(saved_state)
            
            logger.info(f"Todo state auto-saved: {len(todos)} items")
            
        except Exception as e:
            logger.error(f"Failed to save todo state: {e}")
    
    def _prepare_memory_mcp_entity(self, session_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare entity structure for Memory MCP
        This shows what should be saved in Claude environment
        """
        entity = {
            "name": "CurrentSessionState",
            "entityType": "SessionState",
            "observations": [
                f"Session from {session_state['timestamp']}",
                f"Todo Statistics: Total={session_state['statistics']['total_todos']}, "
                f"Completed={session_state['statistics']['completed']}, "
                f"Pending={session_state['statistics']['pending']}, "
                f"In Progress={session_state['statistics']['in_progress']}",
                # Full state with complete todos as JSON
                json.dumps(session_state)
            ]
        }
        
        # Log what would be saved
        logger.info("Memory MCP entity prepared with full todo details")
        
        # In Claude environment, this would call:
        # mcp__memory__search_nodes("CurrentSessionState") 
        # mcp__memory__delete_entities(["CurrentSessionState"])  # if exists
        # mcp__memory__create_entities([entity])
        
        return entity


# Global hook instance
_todo_hook = None


def get_todo_hook() -> TodoHook:
    """Get or create the todo hook instance"""
    global _todo_hook
    if _todo_hook is None:
        _todo_hook = TodoHook()
    return _todo_hook


def register_todo_hook():
    """
    Register the todo hook with the TodoWrite tool
    This would be called during initialization
    """
    hook = get_todo_hook()
    logger.info("Todo hook registered for automatic session state saving")
    return hook