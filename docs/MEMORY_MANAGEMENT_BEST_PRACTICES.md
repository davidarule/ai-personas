# MCP Memory Management Best Practices

## Overview
This document outlines best practices for using MCP servers to maintain persistent memory between sessions and prevent important project details from being lost due to context compaction.

## The Challenge
- **Context Window Limitations**: AI assistants have limited context windows that get compacted over time
- **Session Boundaries**: Each new session starts with a fresh context
- **Information Loss**: Important project details, decisions, and state can be lost
- **Collaboration Continuity**: Multiple personas need shared memory for effective collaboration

## Available MCP Memory Tools

### 1. Memory MCP Server (Knowledge Graph)
- **Purpose**: Stores entities and relationships in a graph structure
- **Best For**: Project state, key decisions, user preferences, workflow rules
- **Access**: `mcp__memory__*` tools

### 2. Serena MCP Server (Project Memory)
- **Purpose**: Project-specific persistent memory storage
- **Best For**: Code patterns, project conventions, build commands, testing approaches
- **Access**: `write_memory`, `read_memory`, `list_memories`, `delete_memory` tools

### 3. Filesystem MCP Server
- **Purpose**: Persistent file storage
- **Best For**: Documentation, configurations, structured data
- **Access**: Standard file operations

### 4. PostgreSQL MCP Server
- **Purpose**: Structured relational data storage
- **Best For**: Complex project data, relationships, queries
- **Access**: SQL queries

## Memory Strategy Framework

### 1. Hierarchical Memory Organization

```
Global Memory (Cross-Project)
├── User Preferences & Instructions
├── Workflow Rules & Habits
├── Tool Usage Patterns
└── Common Conventions

Project Memory (Project-Specific)
├── Project Context & State
├── Architecture Decisions
├── Code Conventions
├── Build & Test Commands
└── Current Task Progress

Session Memory (Temporary)
├── Active Task Details
├── Recent Discoveries
├── Working State
└── Immediate Context
```

### 2. Memory Categories & Storage Recommendations

#### Critical Persistent Memory (Always Store)
- **User Instructions**: Store in Memory MCP as entities
- **Workflow Rules**: Store as WorkflowRule entities with observations
- **Project Configuration**: Store in both Memory MCP and Serena
- **Key Decisions**: Store as Decision entities with rationale
- **Active Tasks**: Store current state before session end

#### Project-Specific Memory (Store per Project)
- **Code Conventions**: Use Serena's write_memory
- **Build/Test Commands**: Store in Serena and Memory MCP
- **Architecture Patterns**: Document in files and Memory MCP
- **Dependencies & Tools**: Store in Serena for quick access
- **Common Issues & Solutions**: Create Knowledge entities

#### Session Continuity Memory
- **Current Task State**: Update Memory MCP before context compaction
- **Recent Changes**: Summarize and store in Memory MCP
- **Blockers & Issues**: Create Issue entities with context
- **Next Steps**: Store as pending tasks with clear descriptions

### 3. Memory Storage Patterns

#### Pattern 1: Entity-Relation Model (Memory MCP)
```python
# Store a workflow rule
Entity: "TodoCompletionWorkflow"
Type: "WorkflowRule"
Observations: [
  "After completing each todo item:",
  "1. Update todo list status",
  "2. Update relevant documentation",
  "3. Git add, commit, and push changes"
]

# Store project context
Entity: "CurrentProjectState"
Type: "ProjectContext"
Observations: [
  "Working on: AI Personas DevSecOps",
  "Current phase: Testing Steve persona",
  "Active work item: #265",
  "Blocker: PR reviewer identity mapping"
]
```

#### Pattern 2: Key-Value Storage (Serena)
```
Key: "build_commands"
Value: {
  "lint": "npm run lint",
  "typecheck": "npm run typecheck",
  "test": "npm test",
  "build": "npm run build"
}

Key: "project_conventions"
Value: {
  "imports": "Use absolute imports from src/",
  "testing": "Jest with TypeScript",
  "state": "React Query for server state",
  "styling": "Material-UI components"
}
```

#### Pattern 3: Structured Files (Filesystem)
```
/opt/ai-personas/
├── CLAUDE.md              # Project-specific instructions
├── docs/
│   ├── MEMORY_INDEX.md    # Index of important memories
│   ├── DECISIONS.md       # Architecture decisions
│   └── CONVENTIONS.md     # Code conventions
└── .memory/
    ├── session_state.json # Last session state
    └── task_progress.json # Current task progress
```

### 4. Memory Lifecycle Management

#### Session Start Protocol
1. **Load User Instructions**: Read CLAUDE.md files
2. **Query Global Memory**: Get user preferences and workflow rules
3. **Load Project Context**: Query project-specific memories
4. **Restore Session State**: Check for previous session data
5. **Verify Tool Access**: Ensure all MCP servers are connected

#### During Session
1. **Progressive Storage**: Store important discoveries immediately
2. **Update Task State**: Keep Memory MCP updated with progress
3. **Document Decisions**: Create Decision entities with rationale
4. **Track Issues**: Create Issue entities for blockers
5. **Maintain Relations**: Link related concepts in knowledge graph

#### Pre-Compaction Protocol
1. **Summarize Current State**: Create comprehensive state summary
2. **Store Active Context**: Update CurrentProjectState entity
3. **Document Progress**: Update task progress in Memory MCP
4. **Save Working Files**: Ensure all changes are committed
5. **Create Continuation Point**: Store clear next steps

#### Session End Protocol
1. **Final State Update**: Store complete session summary
2. **Update Task Status**: Mark completed items, note pending work
3. **Document Learnings**: Add new Knowledge entities
4. **Save Session Metadata**: Timestamp and session highlights
5. **Prepare Handoff**: Create clear continuation instructions

### 5. The /remember Command Enhancement

The `/remember` command should execute this sequence:

```python
async def remember_command():
    # 1. Read user CLAUDE.md
    user_instructions = read_file("~/.claude/CLAUDE.md")
    
    # 2. Read project CLAUDE.md if exists
    project_instructions = read_file("./CLAUDE.md") if exists
    
    # 3. Query Memory MCP for key entities
    memories = query_memory_entities([
        "UserPreferences",
        "WorkflowRules",
        "CurrentProjectState",
        "ActiveTasks",
        "RecentDecisions"
    ])
    
    # 4. Load Serena project memories
    serena_memories = list_and_read_memories([
        "project_conventions",
        "build_commands",
        "common_issues",
        "testing_approach"
    ])
    
    # 5. Restore session context
    session_state = read_session_state()
    
    return "Loaded instructions and memories successfully"
```

### 6. Best Practices for Memory Content

#### DO:
- **Be Specific**: Store concrete, actionable information
- **Include Context**: Add why/when/how information
- **Use Consistent Keys**: Follow naming conventions
- **Version Important Data**: Track changes over time
- **Cross-Reference**: Link related memories

#### DON'T:
- **Store Redundant Data**: Avoid duplicating file content
- **Use Vague Descriptions**: Be precise and detailed
- **Forget Timestamps**: Always include temporal context
- **Ignore Cleanup**: Remove outdated memories
- **Store Sensitive Data**: No passwords or secrets

### 7. Memory Query Patterns

#### Finding Relevant Memories
```python
# Search by type and scope
memories = search_contexts(
    context_type=ContextType.WORKFLOW,
    scope=ContextScope.GLOBAL
)

# Search by tags
decisions = search_contexts(
    tags=["architecture", "security"]
)

# Get project-specific context
project_context = get_work_item_context(work_item_id)
```

#### Efficient Memory Access
1. **Index Key Memories**: Create an index entity listing important memories
2. **Use Relations**: Navigate knowledge graph efficiently
3. **Cache Common Queries**: Store frequently accessed combinations
4. **Batch Operations**: Load related memories together
5. **Prioritize Recent**: Access recently updated memories first

### 8. Integration with AI Personas

#### Shared Memory Patterns
- **Work Item Context**: All personas access same work item memories
- **Decision History**: Shared architectural decisions
- **Collaboration State**: Track multi-persona workflows
- **Knowledge Base**: Common technical knowledge

#### Persona-Specific Memory
- **Role Context**: Each persona's specific domain knowledge
- **Tool Preferences**: Persona-specific tool configurations
- **Work History**: Track what each persona has done
- **Expertise Areas**: Document specialized knowledge

## Implementation Checklist

### Immediate Actions
- [ ] Create Memory MCP entities for user preferences
- [ ] Store current project state and context
- [ ] Document workflow rules as entities
- [ ] Set up Serena project memories
- [ ] Create memory index documentation

### Session Practices
- [ ] Start each session with /remember protocol
- [ ] Update task progress regularly
- [ ] Store decisions with rationale
- [ ] Document blockers immediately
- [ ] Summarize before context compaction

### Maintenance Tasks
- [ ] Weekly memory cleanup
- [ ] Update memory index
- [ ] Archive old session data
- [ ] Review and update conventions
- [ ] Optimize query patterns

## Conclusion

Effective memory management using MCP servers enables:
- **Continuity**: Seamless work across sessions
- **Collaboration**: Shared context between personas
- **Efficiency**: Quick access to important information
- **Learning**: Building on past decisions and discoveries
- **Reliability**: Consistent behavior and conventions

By following these practices, important project details and user instructions will persist across context compactions and session boundaries, creating a more effective and continuous development experience.