# AI Personas Project Context

## Overview
AI Personas is a DevSecOps automation system that uses AI-powered personas to handle different aspects of software development lifecycle. The system integrates with Azure DevOps and provides a web-based control center.

## Key Components

### 1. Personas System
- **Steve Bot**: System/Security Architect - Generates architecture docs, creates PRs
- **Kav Bot**: Security Test Engineer - Performs SAST/DAST testing
- **Lachlan Bot**: DevSecOps Engineer (Not implemented)
- **Ruley Bot**: Requirements Analyst (Not implemented)
- Additional personas planned for various roles

### 2. Architecture
- **Backend API**: Python-based API running on port 8080 (`src/api/real_factory_api.py`)
- **Frontend Dashboard**: Web interface on port 3000 (`index.html`)
- **Workflow Engine**: YAML-based workflow system with 14 predefined workflows
- **Database**: SQLite databases for logs and tools

### 3. Key Features
- Real-time persona status monitoring
- Azure DevOps integration for work item management
- Workflow automation system
- Tool management system
- AI agent configuration (OpenAI, Anthropic, Google Gemini)
- MCP (Model Context Protocol) server integration

### 4. Technical Stack
- **Backend**: Python 3, FastAPI
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Database**: SQLite
- **AI Integration**: Multiple LLM providers via API
- **Version Control**: Git
- **CI/CD**: Azure DevOps

### 5. Important Files
- `/opt/ai-personas/CLAUDE.md` - Project-specific instructions
- `/opt/ai-personas/settings.json` - Azure DevOps configuration
- `/opt/ai-personas/src/api/real_factory_api.py` - Main API server
- `/opt/ai-personas/index.html` - Main dashboard interface

### 6. Current Status
- ✅ Steve Bot and Kav Bot fully functional
- ✅ Dashboard with real-time updates
- ✅ Azure DevOps integration
- ✅ Workflow system operational
- 🔄 11 personas pending implementation
- 🔄 Enhanced monitoring and metrics

## Development Guidelines
1. Always start API before Dashboard
2. Use `index.html`, never `dashboard.html`
3. Check logs in `/opt/ai-personas/*.log`
4. PAT token required for Azure DevOps
5. Follow existing code patterns and conventions