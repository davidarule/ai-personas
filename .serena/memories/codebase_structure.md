# AI Personas Codebase Structure

## Directory Layout

```
/opt/ai-personas/
├── src/                          # Main source code
│   ├── personas/                 # Persona implementations
│   │   ├── processors/          # Individual persona processors
│   │   │   ├── base_processor.py       # Base class for all personas
│   │   │   ├── steve_processor.py      # Security Architect
│   │   │   ├── kav_processor.py        # Test Engineer
│   │   │   └── ...                     # Other personas
│   │   └── processor_factory.py
│   ├── azure_devops/            # Azure DevOps integration
│   ├── orchestration/           # Work item routing and collaboration
│   ├── pr_management/           # Pull request validation
│   ├── project_management/      # Multi-project support
│   ├── work_queue/             # Task queue management
│   └── commands/               # CLI commands
├── docs/                       # Documentation
│   ├── architecture/          # Architecture docs (Steve)
│   ├── security/             # Security docs (Steve, Kav)
│   ├── api/                  # API docs (Jordan, Puck)
│   ├── testing/              # Test docs (Kav)
│   └── ...
├── outputs/                   # Generated outputs by personas
│   ├── steve/                # Steve's outputs
│   ├── kav/                  # Kav's outputs
│   └── ...
├── tests/                    # Test files (currently empty)
├── venv/                     # Virtual environment
├── .venv/                    # Alternative venv
└── test_*.py                 # Test scripts at root level

## Key Components

### Persona Processors
- **BaseProcessor**: Abstract base class defining interface
- **AzureDevOpsEnabledProcessor**: Adds Azure DevOps capabilities
- **Individual Processors**: Steve, Kav, Lachlan, etc.

### Work Flow
1. Work items received from Azure DevOps
2. Routed to appropriate persona by orchestration
3. Persona processes and generates outputs
4. Creates Git branch and commits
5. Creates PR with appropriate reviewers
6. Review tasks created for other personas

### Integration Points
- Azure DevOps API for work items and PRs
- Git for version control
- File system for output generation
- Async processing for concurrent operations