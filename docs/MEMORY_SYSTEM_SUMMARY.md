# AI Personas Memory Management System

## Quick Reference

### 🧠 Memory Hierarchy
```
┌─────────────────────────────────────────┐
│         GLOBAL MEMORY (Persistent)       │
│  • User preferences & instructions      │
│  • Workflow rules                       │
│  • Common patterns                      │
└────────────────────┬────────────────────┘
                     │
┌────────────────────┴────────────────────┐
│      PROJECT MEMORY (Per-Project)        │
│  • Code conventions                     │
│  • Build/test commands                  │
│  • Architecture decisions               │
│  • Current state & progress             │
└────────────────────┬────────────────────┘
                     │
┌────────────────────┴────────────────────┐
│      SESSION MEMORY (Temporary)          │
│  • Active task details                  │
│  • Recent discoveries                   │
│  • Working context                      │
└─────────────────────────────────────────┘
```

### 🔧 MCP Server Usage

| MCP Server | Use For | Access Pattern |
|------------|---------|----------------|
| **Memory** | Entities, relations, persistent state | `mcp__memory__*` |
| **Serena** | Project code patterns, conventions | `write_memory`, `read_memory` |
| **Filesystem** | Documentation, configs, structured data | Standard file ops |
| **PostgreSQL** | Complex relational data | SQL queries |

### 📝 Key Memory Patterns

#### 1. Store User Preferences
```python
Entity: "David's Collaboration Preferences"
Type: "UserPreference"
Observations: [
    "Always ask for help instead of workarounds",
    "Install packages system-wide",
    "Complete git workflow after each todo"
]
```

#### 2. Store Project State
```python
Entity: "CurrentProjectState"
Type: "ProjectContext"
Observations: [
    "Project: AI Personas DevSecOps",
    "Current task: Testing Steve persona",
    "Work item: #265",
    "Next: Fix reviewer identity mapping"
]
```

#### 3. Store Build Commands (Serena)
```
Key: "build_commands"
Value: {
    "lint": "npm run lint",
    "typecheck": "npm run typecheck",
    "test": "npm test"
}
```

### 🚀 Session Protocols

#### Session Start
1. Run `/remember` command
2. Verify MCP connections
3. Load project context
4. Check previous session state

#### During Work
1. Update task progress regularly
2. Store key decisions immediately
3. Document blockers and issues
4. Create knowledge entities for discoveries

#### Before Compaction
1. Summarize current state
2. Update all active memories
3. Commit and push changes
4. Store continuation point

### 💡 The /remember Command

When you type `/remember`, Claude will:
1. ✓ Read user ~/.claude/CLAUDE.md
2. ✓ Read project ./CLAUDE.md
3. ✓ Query Memory MCP for key entities
4. ✓ Load Serena project memories
5. ✓ Restore session state

### 📋 Quick Checklist

**Every Session:**
- [ ] Start with `/remember`
- [ ] Check MCP connections
- [ ] Update task progress
- [ ] Store decisions

**Before Compaction:**
- [ ] Update CurrentProjectState
- [ ] Save working context
- [ ] Document next steps
- [ ] Run final `/remember`

**After Each Todo:**
- [ ] Update todo status
- [ ] Update documentation
- [ ] Git add, commit, push
- [ ] Store any new learnings

### 🔍 Finding Memories

```python
# Get all workflow rules
mcp__memory__search_nodes("WorkflowRule")

# Get current project state
mcp__memory__open_nodes(["CurrentProjectState"])

# List Serena memories
serena list_memories

# Read specific memory
serena read_memory("build_commands")
```

### 🎯 Critical Memories to Maintain

1. **User Instructions** - Personal preferences and rules
2. **Project Context** - Current state and progress
3. **Workflow Rules** - How to complete tasks
4. **Build Commands** - Project-specific commands
5. **Active Tasks** - What you're working on
6. **Key Decisions** - Architecture and design choices
7. **Known Issues** - Problems and solutions

## Implementation Status

✅ **Completed:**
- Memory MCP server integrated
- Best practices documented
- /remember command designed
- Storage patterns defined

🔄 **Next Steps:**
- Test /remember command with real MCP calls
- Create memory index entity
- Set up automated session state saving
- Implement pre-compaction protocol

---

**Remember**: The key to continuity is progressive storage. Don't wait until the end of a session to save important information!