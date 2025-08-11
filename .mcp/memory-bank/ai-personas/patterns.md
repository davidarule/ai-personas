# Patterns & Best Practices - AI-Personas

## MCP Configuration Pattern
**Pattern**: Separate global vs project servers
**Occurrences**: Will track after 3+ uses
**Benefits**: 
- Clean separation of concerns
- Reusable global tools
- Project-specific isolation

## Documentation Pattern
**Pattern**: Five-file memory bank structure
**Files**: goals.md, status.md, history.md, decisions.md, patterns.md
**Benefits**: 
- Clear organization
- Easy to navigate
- Captures different aspects of project knowledge

## Context Management Pattern
**Pattern**: Three-tier memory hierarchy
**Tiers**: Immediate (session), Working (active), Archival (compressed)
**Benefits**: 
- Efficient token usage
- Automatic context evolution
- Pattern recognition across sessions
