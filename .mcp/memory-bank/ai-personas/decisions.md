# Technical Decisions - AI-Personas

## MCP Architecture
**Date**: 2025-08-09
**Decision**: Separate global and project-specific MCP servers
**Rationale**: 
- Global servers (memory, github, context7) provide cross-project functionality
- Project servers (filesystem, memory-bank, nova, serena) are specific to ai-personas
- This separation allows clean project isolation while sharing common tools
**Trade-offs**: 
- More complex configuration
- But better modularity and reusability

## HACS Implementation
**Date**: 2025-08-09
**Decision**: Use Memory + Memory-Bank + Nova + Serena combination
**Rationale**: 
- Memory: Knowledge graph for relationships
- Memory-Bank: Structured markdown documentation
- Nova: Context compression and management
- Serena: Code intelligence and navigation
- Together they implement full Hierarchical Adaptive Context System
**Trade-offs**: 
- Multiple servers to coordinate
- But provides complete context management capability
