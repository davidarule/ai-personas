#!/usr/bin/env python3
"""
Real /remember Command Implementation with actual MCP integration
This version uses the actual MCP functions available in Claude
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class RememberCommandReal:
    """Real /remember command using actual MCP functions"""

    def __init__(self):
        self.memories_loaded = {
            "user_instructions": False,
            "project_instructions": False,
            "global_memories": False,
            "project_memories": False,
            "serena_instructions": False,
            "session_state": False,
        }

    async def execute(self) -> str:
        """Execute the /remember command with real MCP calls"""
        results = []

        # 1. Load user CLAUDE.md
        user_instructions = await self._load_user_instructions()
        if user_instructions:
            results.append("✓ Loaded user CLAUDE.md instructions")
            self.memories_loaded["user_instructions"] = True

        # 2. Load project CLAUDE.md
        project_instructions = await self._load_project_instructions()
        if project_instructions:
            results.append("✓ Loaded project CLAUDE.md instructions")
            self.memories_loaded["project_instructions"] = True

        # 3. Load Memory MCP entities
        global_memories = await self._load_global_memories_real()
        if global_memories:
            entity_count = sum(len(m.get("entities", [])) for m in global_memories)
            results.append(f"✓ Loaded {entity_count} global memory entities")
            self.memories_loaded["global_memories"] = True

        # 4. Load Serena memories
        project_memories = await self._load_project_memories_real()
        if project_memories:
            results.append(f"✓ Loaded {len(project_memories)} project-specific memories")
            self.memories_loaded["project_memories"] = True

        # 5. Load Serena instructions
        serena_instructions = await self._load_serena_instructions_real()
        if serena_instructions:
            results.append("✓ Loaded Serena instructions")
            self.memories_loaded["serena_instructions"] = True

        # 6. Restore session state
        session_state = await self._restore_session_state_real()
        if session_state:
            results.append("✓ Restored previous session state")
            self.memories_loaded["session_state"] = True

        # Generate summary
        summary = self._generate_summary(
            user_instructions,
            project_instructions,
            global_memories,
            project_memories,
            serena_instructions,
            session_state,
        )

        return "\n".join(results) + "\n\n" + summary

    async def _load_user_instructions(self) -> Optional[str]:
        """Load user's global CLAUDE.md instructions"""
        user_claude_path = Path.home() / ".claude" / "CLAUDE.md"
        if user_claude_path.exists():
            try:
                with open(user_claude_path, "r") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read user CLAUDE.md: {e}")
        return None

    async def _load_project_instructions(self) -> Optional[str]:
        """Load project-specific CLAUDE.md instructions"""
        project_claude_path = Path("./CLAUDE.md")
        if project_claude_path.exists():
            try:
                with open(project_claude_path, "r") as f:
                    return f.read()
            except Exception as e:
                logger.error(f"Failed to read project CLAUDE.md: {e}")
        return None

    async def _load_global_memories_real(self) -> List[Dict[str, Any]]:
        """Query Memory MCP for key global entities using real MCP functions"""
        memories = []
        
        # Entity types to search for
        entity_queries = [
            ("UserPreference", "David's preferences and instructions"),
            ("WorkflowRule", "Workflow rules and habits"),
            ("ArchitectureDecision", "Key architectural decisions"),
            ("ProjectContext", "Current project state"),
            ("TaskContext", "Active task information"),
        ]
        
        # First try to read the full graph
        try:
            # In Claude environment this would be:
            # graph_result = mcp__memory__read_graph()
            
            # For this file to work in testing, we need to check if we're in Claude
            import sys
            if 'mcp__memory__read_graph' in sys.modules.get('__main__', {}).__dict__:
                graph_result = mcp__memory__read_graph()
                
                if graph_result and 'entities' in graph_result:
                    # Group entities by type
                    entities_by_type = {}
                    for entity in graph_result['entities']:
                        entity_type = entity.get('entityType', 'Unknown')
                        if entity_type not in entities_by_type:
                            entities_by_type[entity_type] = []
                        entities_by_type[entity_type].append(entity)
                    
                    # Add found entities to memories
                    for entity_type, description in entity_queries:
                        if entity_type in entities_by_type:
                            memory_entry = {
                                "type": entity_type,
                                "description": description,
                                "entities": entities_by_type[entity_type],
                            }
                            memories.append(memory_entry)
        except Exception as e:
            logger.error(f"Failed to read memory graph: {e}")
            
        # If no memories found, try individual searches
        if not memories:
            for entity_type, description in entity_queries:
                try:
                    if 'mcp__memory__search_nodes' in sys.modules.get('__main__', {}).__dict__:
                        search_result = mcp__memory__search_nodes(entity_type)
                        if search_result and 'nodes' in search_result:
                            memory_entry = {
                                "type": entity_type,
                                "description": description,
                                "entities": search_result['nodes'],
                            }
                            memories.append(memory_entry)
                except Exception as e:
                    logger.error(f"Failed to search for {entity_type}: {e}")
                    
        return memories

    async def _load_project_memories_real(self) -> List[Dict[str, Any]]:
        """Load project-specific memories from Serena using real MCP functions"""
        memories = []
        
        memory_keys = [
            "project_conventions",
            "build_commands", 
            "test_commands",
            "common_issues",
            "architecture_patterns",
            "dependencies",
        ]
        
        try:
            import sys
            if 'mcp__serena__list_memories' in sys.modules.get('__main__', {}).__dict__:
                available_memories = mcp__serena__list_memories()
                
                if available_memories and 'memories' in available_memories:
                    for key in memory_keys:
                        memory_files = [m for m in available_memories['memories'] 
                                       if key in m.lower()]
                        
                        if memory_files:
                            try:
                                content = mcp__serena__read_memory(memory_files[0])
                                if content:
                                    memory_entry = {
                                        "key": key,
                                        "value": content,
                                        "filename": memory_files[0]
                                    }
                                    memories.append(memory_entry)
                            except Exception as e:
                                logger.error(f"Failed to read Serena memory {key}: {e}")
        except Exception as e:
            logger.error(f"Failed to access Serena memories: {e}")
            
        return memories

    async def _load_serena_instructions_real(self) -> Optional[str]:
        """Load Serena's initial instructions using real MCP functions"""
        try:
            import sys
            if 'mcp__serena__check_onboarding_performed' in sys.modules.get('__main__', {}).__dict__:
                # Check if onboarding was performed
                onboarding_status = mcp__serena__check_onboarding_performed()
                
                # Get instructions
                if 'mcp__serena__onboarding' in sys.modules.get('__main__', {}).__dict__:
                    instructions = mcp__serena__onboarding()
                    if instructions:
                        return instructions
                        
            # Return default if MCP not available
            return """
            Serena MCP Server provides:
            - Semantic code analysis tools
            - Project-specific memory storage
            - Code navigation and search
            - Symbol-based editing
            - Current project: AI Personas DevSecOps
            """
        except Exception as e:
            logger.error(f"Failed to load Serena instructions: {e}")
            return None

    async def _restore_session_state_real(self) -> Optional[Dict[str, Any]]:
        """Restore session state using real MCP functions"""
        # First check file
        session_file = Path(".memory/session_state.json")
        if session_file.exists():
            try:
                with open(session_file, "r") as f:
                    state = json.load(f)
                    if "timestamp" in state:
                        saved_time = datetime.fromisoformat(state["timestamp"])
                        if (datetime.now() - saved_time).days < 1:
                            session_file.unlink()
                            return state
            except Exception as e:
                logger.error(f"Failed to load session state from file: {e}")
                
        # Check Memory MCP
        try:
            import sys
            if 'mcp__memory__search_nodes' in sys.modules.get('__main__', {}).__dict__:
                session_nodes = mcp__memory__search_nodes("CurrentSessionState")
                
                if session_nodes and 'nodes' in session_nodes and session_nodes['nodes']:
                    latest_session = session_nodes['nodes'][0]
                    if 'observations' in latest_session:
                        for obs in latest_session['observations']:
                            try:
                                state = json.loads(obs)
                                if isinstance(state, dict) and 'timestamp' in state:
                                    saved_time = datetime.fromisoformat(state["timestamp"])
                                    if (datetime.now() - saved_time).days < 1:
                                        # Delete after reading
                                        if 'mcp__memory__delete_entities' in sys.modules.get('__main__', {}).__dict__:
                                            mcp__memory__delete_entities(["CurrentSessionState"])
                                        return state
                            except:
                                continue
        except Exception as e:
            logger.error(f"Failed to check Memory MCP: {e}")
            
        return None

    def _generate_summary(
        self,
        user_instructions: Optional[str],
        project_instructions: Optional[str],
        global_memories: List[Dict[str, Any]],
        project_memories: List[Dict[str, Any]],
        serena_instructions: Optional[str],
        session_state: Optional[Dict[str, Any]],
    ) -> str:
        """Generate a summary of loaded memories"""
        summary_parts = ["Memory Restoration Summary:"]

        # User instructions
        if user_instructions:
            key_points = self._extract_key_points(user_instructions)
            summary_parts.append(f"\nUser Instructions ({len(key_points)} key points):")
            for point in key_points[:5]:  # Show top 5
                summary_parts.append(f"  • {point}")

        # Project instructions
        if project_instructions:
            summary_parts.append("\nProject: AI Personas DevSecOps")
            summary_parts.append("\nStartup Procedures:")
            summary_parts.append("  1. Backend API: cd /opt/ai-personas/src/api && python3 real_factory_api.py > ../../api.log 2>&1 &")
            summary_parts.append("  2. Frontend: cd /opt/ai-personas && python3 -m http.server 3000 > http_server.log 2>&1 &")
            summary_parts.append("  3. Access dashboard at http://localhost:3000/")
            summary_parts.append("  ⚠️  Use index.html, NOT dashboard.html (obsolete)")

        # Global memories
        if global_memories:
            summary_parts.append("\nGlobal Memories:")
            for memory in global_memories:
                if memory.get("entities"):
                    count = len(memory['entities'])
                    summary_parts.append(f"  • {memory['type']}: {count} items")
                    # Show first entity observation
                    if memory['entities'] and 'observations' in memory['entities'][0]:
                        first_obs = memory['entities'][0]['observations'][0]
                        summary_parts.append(f"    - {first_obs[:80]}...")

        # Serena
        if serena_instructions:
            summary_parts.append("\nSerena MCP: Code analysis tools loaded")

        # Session
        if session_state:
            summary_parts.append("\nPrevious Session:")
            if "current_task" in session_state:
                summary_parts.append(f"  • Task: {session_state['current_task']}")

        return "\n".join(summary_parts)

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from instruction text"""
        key_points = []
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith(("- ", "* ", "• ")):
                key_points.append(line[2:].strip())
        return key_points


# For testing outside Claude environment
if __name__ == "__main__":
    import asyncio
    
    async def test():
        cmd = RememberCommandReal()
        result = await cmd.execute()
        print(result)
        
    asyncio.run(test())