#!/usr/bin/env python3
"""
Enhanced /remember Command Implementation
Restores critical memory and context from multiple MCP servers

Loads in sequence:
1. User CLAUDE.md instructions
2. Project CLAUDE.md instructions  
3. ALL entities from Memory MCP (not filtered)
4. ALL project-specific memories from Serena
5. Serena's initial instructions and capabilities
6. Previous session state

IMPORTANT: This command now loads ALL available memories comprehensively,
not just specific entity types. When used in Claude, replace the placeholder
None values with actual MCP function calls as indicated in comments.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)
# Import session state manager
try:
    from .session_state_manager import get_session_manager
except ImportError:
    get_session_manager = None


class RememberCommand:
    """Enhanced /remember command for memory restoration"""

    def __init__(self):
        self.memories_loaded = {
            "user_instructions": False,
            "project_instructions": False,
            "global_memories": False,
            "project_memories": False,
            "serena_instructions": False,
            "session_state": False,
            "project_activated": False,
        }

    async def execute(self) -> str:
        """Execute the /remember command sequence"""
        try:
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

            # 3. Query Memory MCP for key entities
            global_memories = await self._load_global_memories()
            if global_memories:
                results.append(
                    f"✓ Loaded {len(global_memories)} global memory entities"
                )
                self.memories_loaded["global_memories"] = True

            # 4. Load Serena project memories (if available)
            project_memories = await self._load_project_memories()
            if project_memories:
                results.append(
                    f"✓ Loaded {len(project_memories)} "
                    "project-specific memories"
                )
                self.memories_loaded["project_memories"] = True

            # 5. Load Serena's initial instructions
            serena_instructions = await self._load_serena_instructions()
            if serena_instructions:
                results.append("✓ Loaded Serena's initial instructions")
                self.memories_loaded["serena_instructions"] = True

            # 6. Restore session state
            session_state = await self._restore_session_state()
            if session_state:
                results.append("✓ Restored previous session state")
                self.memories_loaded["session_state"] = True

            # 7. Activate ai-personas project
            project_activation = await self._activate_project()
            if project_activation:
                results.append("✓ Activated ai-personas project")
                self.memories_loaded["project_activated"] = True

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

        except Exception as e:
            logger.error(f"Error in /remember command: {e}")
            return f"Error loading memories: {str(e)}"

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

    async def _load_global_memories(self) -> List[Dict[str, Any]]:
        """Load ALL entities from Memory MCP"""
        memories = []
        
        try:
            logger.info("Loading complete memory graph from Memory MCP...")
            
            # Load the entire memory graph
            graph_result = mcp__memory__read_graph()
            
            if graph_result and 'entities' in graph_result:
                # Group ALL entities by type - don't filter anything
                entities_by_type = {}
                total_entities = 0
                
                for entity in graph_result['entities']:
                    entity_type = entity.get('entityType', 'Unknown')
                    if entity_type not in entities_by_type:
                        entities_by_type[entity_type] = []
                    entities_by_type[entity_type].append(entity)
                    total_entities += 1
                
                logger.info(f"Loaded {total_entities} total entities across {len(entities_by_type)} types")
                
                # Create memory entries for ALL entity types found
                for entity_type, entities in entities_by_type.items():
                    memory_entry = {
                        "type": entity_type,
                        "entities": entities,
                        "count": len(entities)
                    }
                    memories.append(memory_entry)
                    logger.info(f"  - {entity_type}: {len(entities)} entities")
                
                # Also store the full graph for reference
                memories.append({
                    "type": "_FULL_GRAPH",
                    "entities": graph_result.get('entities', []),
                    "relations": graph_result.get('relations', [])
                })
                
            else:
                logger.warning("Could not load memory graph - Memory MCP may not be connected")
                
        except Exception as e:
            logger.error(f"Failed to load memory graph: {e}")
            memories.append({
                "type": "_ERROR",
                "error": str(e),
                "entities": []
            })

        return memories

    async def _load_project_memories(self) -> List[Dict[str, Any]]:
        """Load ALL project-specific memories from Serena"""
        memories = []

        try:
            logger.info("Listing all available Serena memories...")
            
            # List all available Serena memories
            available_memories = mcp__serena__list_memories()
            
            # For testing/documentation, we know these are available:
            # ["codebase_structure", "task_completion_checklist", "suggested_commands", 
            #  "code_style_conventions", "project_entrypoints", "project_overview"]
            
            if available_memories:
                if isinstance(available_memories, list):
                    # If it returns a list directly
                    memory_files = available_memories
                elif isinstance(available_memories, dict) and 'memories' in available_memories:
                    # If it returns a dict with memories key
                    memory_files = available_memories['memories']
                else:
                    memory_files = []
                
                logger.info(f"Found {len(memory_files)} Serena memories to load")
                
                # Read ALL available memories
                for memory_file in memory_files:
                    try:
                        logger.info(f"Reading Serena memory: {memory_file}")
                        
                        # Read the memory file
                        content = mcp__serena__read_memory(memory_file)
                        
                        if content:
                            memory_entry = {
                                "key": memory_file,
                                "value": content,
                                "loaded": True
                            }
                            memories.append(memory_entry)
                            logger.info(f"  ✓ Loaded {memory_file}")
                        else:
                            memory_entry = {
                                "key": memory_file,
                                "value": None,
                                "loaded": False,
                                "reason": "Empty content"
                            }
                            memories.append(memory_entry)
                            
                    except Exception as e:
                        logger.error(f"Failed to read Serena memory {memory_file}: {e}")
                        memory_entry = {
                            "key": memory_file,
                            "value": None,
                            "loaded": False,
                            "error": str(e)
                        }
                        memories.append(memory_entry)
                
            else:
                logger.warning("Could not list Serena memories - Serena MCP may not be connected")
                memories.append({
                    "key": "_ERROR",
                    "value": None,
                    "loaded": False,
                    "error": "Serena MCP not available"
                })
                    
        except Exception as e:
            logger.error(f"Failed to access Serena memories: {e}")
            memories.append({
                "key": "_ERROR",
                "value": None,
                "loaded": False,
                "error": str(e)
            })

        return memories

    async def _load_serena_instructions(self) -> Optional[str]:
        """Load Serena's initial instructions"""
        try:
            instructions_parts = []
            
            # 1. Check onboarding status
            logger.info("Checking Serena onboarding status...")
            onboarding_status = mcp__serena__check_onboarding_performed()
            
            if onboarding_status is not None:
                instructions_parts.append(f"Serena onboarding status: {onboarding_status}")
            
            # 2. Get onboarding instructions
            logger.info("Getting Serena onboarding instructions...")
            onboarding_instructions = mcp__serena__onboarding()
            
            if onboarding_instructions:
                instructions_parts.append("Serena Instructions:")
                instructions_parts.append(str(onboarding_instructions))
            
            # 3. Try to read Serena instruction memories
            logger.info("Checking for Serena instruction memories...")
            instruction_keys = [
                "serena_initial_instructions",
                "serena_usage_guidelines",
                "serena_capabilities"
            ]
            
            for key in instruction_keys:
                try:
                    # Read the Serena instruction memory
                    content = mcp__serena__read_memory(key)
                    
                    if content:
                        instructions_parts.append(f"\n{key}:")
                        instructions_parts.append(str(content))
                        logger.info(f"Loaded {key}")
                except Exception as e:
                    logger.debug(f"Could not load {key}: {e}")
            
            # Return combined instructions if found
            if instructions_parts:
                return "\n".join(instructions_parts)
            
            # Return None if no instructions found (not hardcoded text)
            logger.info("No Serena instructions found from any source")
            return None
            
        except Exception as e:
            logger.error(f"Failed to load Serena instructions: {e}")
            return None

    async def _restore_session_state(self) -> Optional[Dict[str, Any]]:
        """Restore previous session state if available"""
        session_file = Path(".memory/session_state.json")

        if session_file.exists():
            try:
                with open(session_file, "r") as f:
                    state = json.load(f)

                # Check if state is recent (within 24 hours)
                if "timestamp" in state:
                    saved_time = datetime.fromisoformat(state["timestamp"])
                    if (datetime.now() - saved_time).days < 1:
                        # Delete the file after reading
                        session_file.unlink()
                        logger.info("Session state file removed after reading")
                        return state

            except Exception as e:
                logger.error(f"Failed to load session state: {e}")

        # Also try to get from Memory MCP
        try:
            logger.info("Checking Memory MCP for session state")
            # Search for CurrentSessionState entity
            session_nodes = mcp__memory__search_nodes("CurrentSessionState")
            
            if session_nodes and 'nodes' in session_nodes and session_nodes['nodes']:
                # Get the most recent session state
                latest_session = session_nodes['nodes'][0]
                if 'observations' in latest_session and latest_session['observations']:
                    # Parse the session state from observations
                    for obs in latest_session['observations']:
                        try:
                            state = json.loads(obs)
                            if isinstance(state, dict) and 'timestamp' in state:
                                # Check if recent
                                saved_time = datetime.fromisoformat(state["timestamp"])
                                if (datetime.now() - saved_time).days < 1:
                                    logger.info("Found recent session state in Memory MCP")
                                    # Delete after reading
                                    mcp__memory__delete_entities(["CurrentSessionState"])
                                    return state
                        except:
                            continue
                            
        except Exception as e:
            logger.error(f"Failed to check Memory MCP: {e}")

        return None

    async def _activate_project(self) -> dict:
        """Activate the ai-personas project"""
        try:
            logger.info("Activating ai-personas project in Serena...")
            
            # Activate the project in Serena
            activation_result = await mcp__serena__activate_project("/opt/ai-personas")
            
            if activation_result:
                logger.info(f"Project activated: {activation_result.get('project', 'unknown')}")
                logger.info(f"Available memories: {activation_result.get('memories_available', [])}")
            
            return activation_result
            
        except Exception as e:
            logger.error(f"Failed to activate project: {e}")
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

        # User instructions summary
        if user_instructions:
            key_points = self._extract_key_points(user_instructions)
            summary_parts.append(
                f"\nUser Instructions ({len(key_points)} key points):"
            )
            for point in key_points[:5]:  # Show top 5
                summary_parts.append(f"  • {point}")

        # Project instructions summary
        if project_instructions:
            summary_parts.append("\nProject: AI Personas DevSecOps")

        # Global memories summary
        if global_memories:
            summary_parts.append("\nMemory MCP Entities Loaded:")
            
            # Count total entities
            total_entities = 0
            entity_counts = {}
            full_graph = None
            
            for memory in global_memories:
                if memory.get("type") == "_FULL_GRAPH":
                    full_graph = memory
                    continue
                elif memory.get("type") == "_ERROR":
                    summary_parts.append(f"  ⚠️ Error loading memories: {memory.get('error', 'Unknown error')}")
                    continue
                    
                entity_type = memory.get("type", "Unknown")
                count = memory.get("count", len(memory.get("entities", [])))
                if count > 0:
                    entity_counts[entity_type] = count
                    total_entities += count
            
            # Show total
            summary_parts.append(f"  Total: {total_entities} entities across {len(entity_counts)} types")
            
            # Show counts by type
            for entity_type, count in sorted(entity_counts.items(), key=lambda x: x[1], reverse=True):
                summary_parts.append(f"  • {entity_type}: {count}")
            
            # Show key workflow rules
            workflow_rules = []
            user_prefs = []
            for memory in global_memories:
                if memory.get("type") == "WorkflowRule" and memory.get("entities"):
                    workflow_rules.extend(memory["entities"])
                elif memory.get("type") == "UserPreference" and memory.get("entities"):
                    user_prefs.extend(memory["entities"])
            
            if workflow_rules:
                summary_parts.append("\n✓ Key Workflow Rules:")
                for rule in workflow_rules[:5]:  # Show top 5
                    rule_name = rule.get('name', 'Unknown')
                    summary_parts.append(f"  • {rule_name}")
                    # Show first observation as description
                    if rule.get('observations') and len(rule['observations']) > 0:
                        summary_parts.append(f"    → {rule['observations'][0][:80]}...")
                        
            if user_prefs:
                summary_parts.append("\n✓ User Preferences:")
                for pref in user_prefs[:3]:  # Show top 3
                    pref_name = pref.get('name', 'Unknown')
                    summary_parts.append(f"  • {pref_name}")
                    if pref.get('observations') and len(pref['observations']) > 0:
                        summary_parts.append(f"    → {pref['observations'][0][:80]}...")

        # Serena memories summary
        if project_memories:
            summary_parts.append("\nSerena Project Memories:")
            
            loaded_count = 0
            failed_count = 0
            for memory in project_memories:
                if memory.get("key") == "_ERROR":
                    summary_parts.append(f"  ⚠️ Error: {memory.get('error', 'Unknown error')}")
                elif memory.get("loaded", False):
                    loaded_count += 1
                else:
                    failed_count += 1
            
            if loaded_count > 0:
                summary_parts.append(f"  ✓ Successfully loaded {loaded_count} memories:")
                for memory in project_memories:
                    if memory.get("loaded", False):
                        summary_parts.append(f"    • {memory['key']}")
            
            if failed_count > 0:
                summary_parts.append(f"  ⚠️ Failed to load {failed_count} memories")

        # Serena instructions summary
        if serena_instructions:
            summary_parts.append("\nSerena MCP Server:")
            summary_parts.append(
                "  • Code analysis and navigation tools available"
            )
            summary_parts.append("  • Project memory management available")

        # Session state summary
        if session_state:
            summary_parts.append("\nPrevious Session:")
            if "current_task" in session_state:
                task = session_state['current_task']
                summary_parts.append(f"  • Task: {task}")
            
            # Show todo statistics if available
            if "statistics" in session_state:
                stats = session_state['statistics']
                summary_parts.append(f"  • Todos: {stats.get('total_todos', 0)} total "
                                   f"({stats.get('completed', 0)} completed, "
                                   f"{stats.get('pending', 0)} pending, "
                                   f"{stats.get('in_progress', 0)} in progress)")
            elif "todos" in session_state and isinstance(session_state['todos'], list):
                # If we have the full todo list, show it
                todos = session_state['todos']
                if todos and all(isinstance(t, dict) for t in todos):
                    summary_parts.append(f"  • Restored {len(todos)} complete todo items")
                    # Show a few examples
                    for todo in todos[:3]:
                        if 'content' in todo:
                            status = todo.get('status', 'pending')
                            summary_parts.append(f"    - #{todo.get('id', '?')} [{status}]: {todo['content'][:50]}...")
                elif todos:
                    # Old format with just IDs
                    summary_parts.append(f"  • Found {len(todos)} todo IDs (descriptions missing - old format)")

        return "\n".join(summary_parts)

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from instruction text"""
        key_points = []

        # Look for lines starting with - or *
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if line.startswith(("- ", "* ", "• ")):
                key_points.append(line[2:].strip())

        return key_points


# Singleton instance
_remember_command = None


async def execute_remember_command() -> str:
    """Execute the /remember command"""
    global _remember_command

    if _remember_command is None:
        _remember_command = RememberCommand()

    return await _remember_command.execute()


# Integration with Claude's command system
async def handle_remember_command():
    """Handler for /remember command in Claude"""
    result = await execute_remember_command()

    # Create a memory entity to track this restoration
    if _remember_command:
        restoration_record = {
            "timestamp": datetime.now().isoformat(),
            "memories_loaded": _remember_command.memories_loaded,
            "success": all(_remember_command.memories_loaded.values()),
            "summary": result[:200] if result else "No result"  # First 200 chars of summary
        }
        
        # Store this in Memory MCP
        try:
            mcp__memory__create_entities({
                "entities": [{
                    "name": f"RememberCommandExecution_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "entityType": "CommandExecution",
                    "observations": [
                        f"Remember command executed at {restoration_record['timestamp']}",
                        f"Successfully loaded: {restoration_record['memories_loaded']}",
                        f"Overall success: {restoration_record['success']}"
                    ]
                }]
            })
            logger.info(f"Remember command execution tracked: {restoration_record['success']}")
        except Exception as e:
            logger.error(f"Failed to store remember command execution record: {e}")

    return result


if __name__ == "__main__":
    # Test the command
    asyncio.run(handle_remember_command())
