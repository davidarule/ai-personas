# AI Personas DevSecOps Control Center

## 🚀 Quick Start - CRITICAL ORDER
```bash
# ⚠️ MUST SET ENVIRONMENT VARIABLE FIRST!
export AZURE_DEVOPS_PAT="your_pat_token_here"

# ⚠️ MUST START IN THIS EXACT ORDER - Services depend on each other!

# 1. Backend API (Port 8080) - REQUIRED FIRST
cd /opt/ai-personas/src/api && python3 real_factory_api.py > ../../api.log 2>&1 &

# 2. Frontend Dashboard (Port 3000) 
cd /opt/ai-personas && python3 -m http.server 3000 > http_server.log 2>&1 &

# 3. Workflow API (Port 8081) - Optional
cd /opt/ai-personas && ./manage_workflow_api.sh start

# 4. Open Dashboard - MUST USE index.html
http://localhost:3000/index.html

# ⚠️ NEVER use dashboard.html - it's obsolete and has mock data!
```

## 🏥 Service Health Checks
```bash
# Verify services are running
lsof -i :8080  # Backend API - should show python3
lsof -i :3000  # Dashboard - should show python3  
lsof -i :8081  # Workflow API - optional

# Check if services are responding
curl -s http://localhost:8080/api/status | jq .
curl -s http://localhost:3000/index.html | head -n 5

# View logs if issues
tail -f /opt/ai-personas/api.log
tail -f /opt/ai-personas/http_server.log

# Kill stuck services
pkill -f real_factory_api
pkill -f "http.server 3000"
```

## 📁 Project Structure
```
/opt/ai-personas/
├── src/
│   ├── api/
│   │   ├── real_factory_api.py      ✅ CURRENT API - USE THIS
│   │   └── simple_factory_api.py    ❌ DEPRECATED - has mock data
│   ├── personas/
│   │   ├── processors/              
│   │   │   ├── base_processor.py    # Base class for all personas
│   │   │   ├── steve_processor.py   ✅ WORKING - 2201 lines
│   │   │   ├── kav_processor_enhanced.py ✅ WORKING
│   │   │   └── [others]_processor.py ❌ NOT IMPLEMENTED
│   │   └── processor_factory.py     # Factory pattern manager
│   └── workflows/
│       └── *.yaml                   # 14 workflow definitions (wf0-wf13)
├── outputs/                         # Generated artifacts - DO NOT DELETE
│   ├── steve/                       # Security architecture docs
│   └── kav/                         # Test plans and security tests
├── settings.json                    # Azure DevOps config - CRITICAL FILE
├── index.html                       ✅ MAIN DASHBOARD - USE THIS
├── dashboard.html                   ❌ OBSOLETE - DO NOT USE
└── CLAUDE.md                        # This file
```

## 🔧 Azure DevOps Configuration

### Environment Variables (Required)
```bash
# Set the Azure DevOps Personal Access Token
export AZURE_DEVOPS_PAT="your_pat_token_here"

# Optional: Set organization URL (can also be configured in UI)
export AZURE_DEVOPS_ORG="https://dev.azure.com/data6"
```

### Configuration
```json
{
  "organization": "data6",
  "base_url": "https://data6.visualstudio.com/",
  "projects": [
    "AI-Personas-Test-Sandbox",
    "AI-Personas-Test-Sandbox-2"  // Note the hyphen!
  ],
  "pat_token": "Now read from AZURE_DEVOPS_PAT environment variable"
}
```

⚠️ **IMPORTANT**: The PAT token is no longer stored in settings.json for security reasons. You must set the `AZURE_DEVOPS_PAT` environment variable before starting the API.

## 🤖 Persona Implementation Status

| Persona | Role | Status | Notes |
|---------|------|--------|-------|
| **Steve Bot** | System/Security Architect | ✅ WORKING | Generates docs, creates PRs |
| **Kav Bot** | Security Test Engineer | ✅ WORKING | SAST/DAST testing |
| Lachlan Bot | DevSecOps Engineer | ❌ Not Impl | Priority #3 |
| Ruley Bot | Requirements Analyst | ❌ Not Impl | Priority #4 |
| Dave Bot | Project Coordinator | ❌ Not Impl | |
| Jordan Bot | Backend Developer | ❌ Not Impl | |
| Matt Bot | Frontend Developer | ❌ Not Impl | |
| Puck Bot | Developer | ❌ Not Impl | |
| Moby Bot | Mobile Developer | ❌ Not Impl | |
| Shaun Bot | UI/UX Designer | ❌ Not Impl | |
| Laureen Bot | Technical Writer | ❌ Not Impl | |
| Claude Bot | AI Integration | ❌ Not Impl | |
| Brumbie Bot | Product Manager | ❌ Not Impl | |

## ⚠️ Known Issues & Workarounds

### Critical Issues
1. **Dashboard Shows Mock Data**
   - **Symptom**: Personas show fake status
   - **Fix**: Ensure API is running on 8080 FIRST
   - **Verify**: `curl http://localhost:8080/api/personas`

2. **Services Must Start in Order**
   - API (8080) → Dashboard (3000) → Workflow (8081)
   - If started wrong, kill all and restart

3. **PR Reviewer Assignment Fails**
   - **Issue**: Azure DevOps identity mapping problem
   - **Workaround**: Use fallback review tasks
   - **Details**: Different IDs for PR context vs Graph API

### Non-Critical Issues
- Azure DevOps API returns 400 errors sometimes (ignore)
- Log files grow large (clean periodically)
- Some personas show "undefined" if API not running

## 🛠️ Common Operations

### Start Everything
```bash
# One command to start all
cd /opt/ai-personas && \
  python3 src/api/real_factory_api.py > api.log 2>&1 & \
  python3 -m http.server 3000 > http_server.log 2>&1 & \
  echo "Services starting... wait 5 seconds" && \
  sleep 5 && \
  echo "Dashboard: http://localhost:3000/index.html"
```

### Stop Everything
```bash
pkill -f real_factory_api
pkill -f "http.server 3000"
pkill -f workflow_api
```

### Test Persona Processing
```bash
# Test Steve Bot
cd /opt/ai-personas
python3 test_steve_work_item_265.py

# Check output
ls -la outputs/steve/architecture/
```

### View Logs
```bash
# API logs
tail -f /opt/ai-personas/api.log | grep -v "OPTIONS"

# Dashboard access logs  
tail -f /opt/ai-personas/http_server.log

# Persona processing logs
tail -f /opt/ai-personas/outputs/steve/steve_processor.log
```

## 📝 Workflow System

### Overview
- **14 Workflows**: wf0-wf13 in YAML format
- **Categories**: 
  - Master (wf0-wf2): Orchestration workflows
  - Core (wf3-wf8): Main processing workflows
  - Support (wf9-wf13): Utility workflows
- **API**: http://localhost:8081/api/workflows (when running)

### Workflow Management
```bash
# Start workflow API
./manage_workflow_api.sh start

# List workflows
curl http://localhost:8081/api/workflows | jq .

# Execute workflow
curl -X POST http://localhost:8081/api/workflows/wf3/execute \
  -H "Content-Type: application/json" \
  -d '{"work_item_id": "123"}'
```

## 🔑 SSH Access
```bash
# Full tunnel for all services
ssh -i ~/.ssh/AiResearchServerKey3.pem \
  -L 3000:localhost:3000 \
  -L 8080:localhost:8080 \
  -L 8081:localhost:8081 \
  davidarule@20.53.139.22
```

## 📂 File Management

### Critical Files - DO NOT DELETE
```
real_factory_api.py       # Main API
processor_factory.py      # Persona management
settings.json            # Azure DevOps credentials
index.html              # Main dashboard
outputs/                # All generated artifacts
src/personas/processors/ # Persona implementations
```

### Files to Archive/Delete
```bash
# Archive old test files
mkdir -p archive/old_tests
mv test_*.py archive/old_tests/
mv fix_*.py archive/old_tests/

# Archive mock dashboards
mkdir -p archive/mock_dashboards  
mv enhanced_dashboard*.py archive/mock_dashboards/
mv dashboard_with_proxy.py archive/mock_dashboards/

# Clean logs periodically
rm *.log

# Remove node_modules if not using
rm -rf node_modules
```

## 🚨 Emergency Procedures

### If Dashboard Shows Mock Data
1. Check API is running: `lsof -i :8080`
2. Check API responses: `curl http://localhost:8080/api/personas`
3. Restart in correct order (API first, then dashboard)
4. Clear browser cache and reload

### If Personas Show "Undefined"
1. API not running or crashed
2. Check api.log for errors
3. Restart real_factory_api.py
4. Verify processor_factory.py exists

### If Azure DevOps Fails
1. Check PAT token in settings.json
2. Verify organization name is "data6"
3. Check project names (note hyphens!)
4. Test with: `curl -H "Authorization: Basic [PAT]" https://data6.visualstudio.com/_apis/projects`

## 📊 Development Status

### Currently Working
- ✅ Backend API with real processors
- ✅ Dashboard showing real persona states
- ✅ Steve Bot generating security docs
- ✅ Kav Bot security testing
- ✅ Basic Azure DevOps integration
- ✅ Workflow system (14 workflows)

### In Progress
- 🔄 Remaining 11 persona implementations
- 🔄 PR reviewer identity mapping
- 🔄 Real-time WebSocket updates
- 🔄 Persistent state management

### Not Started
- ❌ Automated work item routing
- ❌ Multi-project coordination
- ❌ Metrics and monitoring dashboard
- ❌ Admin interface for persona management

## 💡 Quick Tips

1. **Always start API before Dashboard** - Critical for real data
2. **Use index.html, never dashboard.html** - Avoid mock data
3. **Check logs when things fail** - Usually port conflicts or missing deps
4. **PAT token expires** - Regenerate in Azure DevOps if 401 errors
5. **Personas need API running** - Or they show as undefined
6. **Work items need proper tags** - "security" routes to Steve/Kav

## 🧠 MCP Servers (Model Context Protocol)

### Available MCP Servers
1. **rag-context**: Project documentation and context retrieval
   - Data stored in `./project-context/`
   - Use for retrieving project information

2. **memory-bank**: Persistent memory across sessions
   - Data stored in `./memory-bank/`
   - Organized into: decisions, learnings, context, issues

### Usage
```bash
# MCP servers are configured in .mcp/config.json
# They will auto-start when Claude accesses them
# Add context files to project-context/
# Memory bank auto-organizes in subdirectories
```

---
*Last Updated: 2025-01-09 | Version: 2.1 | Status: Production*
