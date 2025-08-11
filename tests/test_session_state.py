#!/usr/bin/env python3
"""
Test the session state manager with complete todo items
"""

import json
from datetime import datetime
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, 'src')

from commands.session_state_manager import SessionStateManager


def test_session_state_manager():
    """Test saving and loading complete todo items"""
    
    print("Testing Session State Manager...")
    manager = SessionStateManager()
    
    # Create sample todos with complete information
    todos = [
        {
            "id": "1",
            "content": "Fix session state memory to save complete todo items with descriptions",
            "status": "completed",
            "priority": "high"
        },
        {
            "id": "2", 
            "content": "Save the system logs and persona logs to a local database so the entire log can be shown for both the system and each persona",
            "status": "in_progress",
            "priority": "high"
        },
        {
            "id": "3",
            "content": "Have a means to automatically delete logs older than X days, where X is specified in the settings", 
            "status": "pending",
            "priority": "medium"
        },
        {
            "id": "4",
            "content": "Get the Logs displayed to go to the bottom of the panel",
            "status": "pending", 
            "priority": "medium"
        }
    ]
    
    # Save session state
    print("\n1. Saving session state with complete todos...")
    saved_state = manager.save_session_state(
        todos=todos,
        current_task="Testing session state manager",
        context={
            "project": "AI Personas",
            "test_mode": True
        },
        discoveries=["Session state now saves complete todos", "No more lost descriptions"],
        next_steps=["Test in Claude environment", "Update documentation"]
    )
    
    print(f"   ✓ Saved {len(todos)} complete todo items")
    print(f"   ✓ Statistics: {saved_state['statistics']}")
    
    # Verify file was created
    session_file = Path(".memory/session_state.json")
    assert session_file.exists(), "Session file should exist"
    print(f"   ✓ Session file created: {session_file}")
    
    # Load and verify
    print("\n2. Loading session state...")
    loaded_state = manager.load_session_state()
    assert loaded_state is not None, "Should load session state"
    assert len(loaded_state['todos']) == len(todos), "Should have same number of todos"
    
    print(f"   ✓ Loaded {len(loaded_state['todos'])} todos")
    
    # Verify todos have complete information
    print("\n3. Verifying todo completeness...")
    for i, todo in enumerate(loaded_state['todos']):
        assert 'id' in todo, f"Todo {i} missing id"
        assert 'content' in todo, f"Todo {i} missing content"
        assert 'status' in todo, f"Todo {i} missing status"
        assert 'priority' in todo, f"Todo {i} missing priority"
        print(f"   ✓ Todo #{todo['id']}: {todo['content'][:50]}...")
    
    # Test formatting
    print("\n4. Testing todo display formatting...")
    formatted = manager.format_todos_for_display(loaded_state['todos'])
    print(formatted)
    
    # Show what would be saved to Memory MCP
    print("\n5. Memory MCP entity structure:")
    entity = {
        "name": "CurrentSessionState",
        "entityType": "SessionState",
        "observations": [
            f"Session from {saved_state['timestamp']}",
            f"Total todos: {saved_state['statistics']['total_todos']} "
            f"(Completed: {saved_state['statistics']['completed']}, "
            f"Pending: {saved_state['statistics']['pending']}, "
            f"In Progress: {saved_state['statistics']['in_progress']})",
            json.dumps(saved_state)
        ]
    }
    
    print(f"   Entity: {entity['name']} ({entity['entityType']})")
    print(f"   Observations: {len(entity['observations'])} items")
    print(f"   Full state size: {len(entity['observations'][2])} chars")
    
    # Verify the JSON observation contains complete todos
    full_state = json.loads(entity['observations'][2])
    assert full_state['todos'][0]['content'] == todos[0]['content'], "Should preserve todo content"
    print("   ✓ Complete todo items preserved in Memory MCP format")
    
    print("\n✅ All tests passed! Session state properly saves complete todo items.")
    

if __name__ == "__main__":
    test_session_state_manager()