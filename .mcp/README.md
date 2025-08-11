# MCP Server Configuration for AI Personas

This directory contains the Model Context Protocol (MCP) server configuration for the AI Personas project.

## Configured Servers

### 1. rag-context
- **Purpose**: Provides RAG (Retrieval Augmented Generation) capabilities for project context
- **Data Directory**: `./project-context`
- **Usage**: Store project documentation, context files, and reference materials

### 2. memory-bank
- **Purpose**: Persistent memory storage across sessions
- **Root Directory**: `./memory-bank`
- **Usage**: Store decisions, learnings, issues, and long-term project knowledge

## Setup Instructions

1. Ensure Node.js and npm are installed
2. The MCP servers will be automatically installed via npx when first accessed
3. Add context files to `project-context/` directory
4. Memory bank will automatically organize content in subdirectories

## Directory Structure
```
/opt/ai-personas/
├── .mcp/
│   ├── config.json         # MCP server configuration
│   └── README.md          # This file
├── project-context/       # RAG context data
│   └── ai-personas-context.md
└── memory-bank/          # Persistent memory storage
    ├── decisions/        # Architecture decisions
    ├── learnings/        # Discovered patterns
    ├── context/          # Project context
    └── issues/           # Known issues
```

## Usage in Claude
When Claude starts a session in this project, these MCP servers will be available for:
- Retrieving project context and documentation
- Storing and recalling decisions and learnings
- Maintaining persistent knowledge across sessions