"""
Session State Manager for AI Personas
Properly saves and restores complete todo items and session state
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


class SessionStateManager:
    """Manages session state with proper todo item preservation"""
    
    def __init__(self):
        self.memory_dir = Path(".memory")
        self.memory_dir.mkdir(exist_ok=True)
        self.session_file = self.memory_dir / "session_state.json"
    
    def save_session_state(self, todos: List[Dict[str, Any]], 
                          current_task: Optional[str] = None,
                          context: Optional[Dict[str, Any]] = None,
                          discoveries: Optional[List[str]] = None,
                          next_steps: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Save complete session state with full todo items
        
        Args:
            todos: List of todo dictionaries with id, content, status, priority
            current_task: Description of current task being worked on
            context: Additional context (project info, settings, etc.)
            discoveries: List of discoveries made during session
            next_steps: List of next steps to take
            
        Returns:
            The saved session state dictionary
        """
        session_state = {
            "timestamp": datetime.now().isoformat(),
            "todos": todos,  # Complete todo items, not just IDs!
            "current_task": current_task,
            "context": context or {},
            "discoveries": discoveries or [],
            "next_steps": next_steps or [],
            "version": "2.0"  # Version to track format changes
        }
        
        # Calculate some statistics
        completed_todos = [t for t in todos if t.get("status") == "completed"]
        pending_todos = [t for t in todos if t.get("status") == "pending"]
        in_progress_todos = [t for t in todos if t.get("status") == "in_progress"]
        
        session_state["statistics"] = {
            "total_todos": len(todos),
            "completed": len(completed_todos),
            "pending": len(pending_todos),
            "in_progress": len(in_progress_todos)
        }
        
        # Save to file
        try:
            with open(self.session_file, "w") as f:
                json.dump(session_state, f, indent=2)
            logger.info(f"Saved session state with {len(todos)} todos to {self.session_file}")
        except Exception as e:
            logger.error(f"Failed to save session state to file: {e}")
        
        return session_state
    
    def load_session_state(self) -> Optional[Dict[str, Any]]:
        """
        Load session state from file
        
        Returns:
            The loaded session state or None if not found/invalid
        """
        if not self.session_file.exists():
            return None
            
        try:
            with open(self.session_file, "r") as f:
                state = json.load(f)
            
            # Validate it has the expected structure
            if not isinstance(state, dict) or "todos" not in state:
                logger.warning("Invalid session state format")
                return None
            
            # Check if it's recent (within 24 hours)
            if "timestamp" in state:
                saved_time = datetime.fromisoformat(state["timestamp"])
                if (datetime.now() - saved_time).days >= 1:
                    logger.info("Session state is too old, ignoring")
                    return None
            
            logger.info(f"Loaded session state with {len(state.get('todos', []))} todos")
            return state
            
        except Exception as e:
            logger.error(f"Failed to load session state: {e}")
            return None
    
    def format_todos_for_display(self, todos: List[Dict[str, Any]]) -> str:
        """Format todos for display"""
        if not todos:
            return "No todos found"
        
        lines = []
        for todo in todos:
            status_emoji = {
                "completed": "✅",
                "in_progress": "🔄", 
                "pending": "⏳"
            }.get(todo.get("status", "pending"), "❓")
            
            priority_badge = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(todo.get("priority", "medium"), "")
            
            lines.append(f"{status_emoji} #{todo.get('id', '?')} {priority_badge} - {todo.get('content', 'No description')}")
        
        return "\n".join(lines)
    
    def save_to_memory_mcp(self, session_state: Dict[str, Any]) -> bool:
        """
        Save session state to Memory MCP
        This would be called from Claude with actual MCP functions
        """
        # This is a placeholder - in Claude environment, this would:
        # 1. Check for existing CurrentSessionState entity
        # 2. Delete it if found
        # 3. Create new entity with full todo items
        
        entity_data = {
            "name": "CurrentSessionState",
            "entityType": "SessionState",
            "observations": [
                f"Session from {session_state['timestamp']}",
                f"Total todos: {session_state['statistics']['total_todos']} "
                f"(Completed: {session_state['statistics']['completed']}, "
                f"Pending: {session_state['statistics']['pending']}, "
                f"In Progress: {session_state['statistics']['in_progress']})",
                json.dumps(session_state)  # Full session state as JSON
            ]
        }
        
        logger.info("Would save to Memory MCP: %s", entity_data)
        return True


# Singleton instance
_session_manager = None


def get_session_manager() -> SessionStateManager:
    """Get or create the session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionStateManager()
    return _session_manager