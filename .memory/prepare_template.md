# /prepare Command Template

When user types /prepare, I will:

1. Create a SessionState entity in Memory MCP with:
   - Current task and progress
   - Active todos and their status
   - Key decisions made
   - Next steps to take
   - Important discoveries
   - Context information

2. Save a backup to .memory/session_state.json

3. Provide confirmation with summary

## Implementation Steps:

```python
# 1. Gather current state
current_state = {
    "timestamp": "ISO timestamp",
    "current_task": "What I'm working on",
    "todos": [list of todos with status],
    "decisions": ["key decisions made"],
    "next_steps": ["what to do next"],
    "context": {
        "branch": "current git branch",
        "files_modified": ["list of files"],
        "api_status": "running/stopped",
        "other_context": "..."
    },
    "discoveries": ["important findings"]
}

# 2. Save to Memory MCP
mcp__memory__create_entities([{
    "name": "CurrentSessionState",
    "entityType": "SessionState",
    "observations": [
        "Session snapshot from [timestamp]",
        "Task: [current task]",
        "Progress: [what was completed]",
        "Next: [what's next]",
        "Full state: [JSON of current_state]"
    ]
}])

# 3. Save backup locally
Path(".memory/session_state.json").write_text(json.dumps(current_state))
```

## When user types /remember:

1. Search for CurrentSessionState entity
2. Extract and display the state
3. Delete the entity to keep it clean
4. Continue from where we left off