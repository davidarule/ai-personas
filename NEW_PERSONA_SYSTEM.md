# AI Personas Dynamic System v2.0

## Overview
The AI Personas system has been upgraded from 13 static personas to a dynamic system supporting 25 base persona types with unlimited instances.

## Key Features
- **25 Base Persona Types**: Each with specific skills, tools, and MCP servers
- **Dynamic Instance Creation**: Create multiple instances of each persona type
- **Customizable Configuration**: Override names, skills, tools, and MCP servers per instance
- **Persistent State**: Persona configurations saved to disk
- **RESTful API**: Complete CRUD operations for persona management
- **Backward Compatibility**: Steve and Kav processors still work

## Architecture

### Core Components
1. **PersonaConfig**: Configuration dataclass for persona types
2. **PersonaInstance**: Runtime instance with state and metrics
3. **PersonaRegistry**: Global registry of all persona types
4. **PersonaManager**: High-level instance lifecycle management
5. **ProcessorFactory (New)**: Integrates with legacy processors

### File Structure
```
/opt/ai-personas/
├── src/
│   ├── personas/
│   │   ├── models/
│   │   │   └── persona.py              # Base classes
│   │   ├── types/                      # 25 persona type definitions
│   │   │   ├── __init__.py
│   │   │   ├── software_architect.py
│   │   │   ├── devsecops_engineer.py
│   │   │   └── ... (23 more)
│   │   ├── processor_factory_new.py    # New factory implementation
│   │   └── persona_manager.py          # Instance management
│   └── api/
│       ├── real_factory_api.py         # Updated main API
│       ├── persona_api.py              # Persona management endpoints
│       └── persona_api_integration.py  # aiohttp integration
├── config/
│   └── personas.json                   # Saved persona instances
├── settings_extended.json              # Extended settings v2.0
└── migrate_to_new_persona_system.py   # Migration script
```

## API Endpoints

### Persona Management
- `GET /api/personas/types` - List all available persona types
- `GET /api/personas/instances` - List all persona instances
- `GET /api/personas/instances/{id}` - Get specific instance
- `POST /api/personas/instances` - Create new instance
- `PUT /api/personas/instances/{id}` - Update instance
- `DELETE /api/personas/instances/{id}` - Delete instance
- `POST /api/personas/instances/{id}/toggle` - Toggle active state

### MCP Servers
- `GET /api/mcp-servers` - List all MCP servers
- `POST /api/mcp-servers/{name}/toggle` - Toggle server enabled

### Tools
- `GET /api/tools/categories` - List tool categories
- `GET /api/tools/category/{name}` - Get tools in category
- `POST /api/tools/{name}/toggle` - Toggle tool enabled

## Migration Guide

### Step 1: Run Migration Script
```bash
cd /opt/ai-personas
python3 migrate_to_new_persona_system.py
```

This will:
- Create config directory
- Initialize persona manager
- Create default instances (Steve, Kav, and examples)
- Create settings_extended.json
- Set up templates directory

### Step 2: Update API Service
The real_factory_api.py has been updated to use the new system:
- Imports processor_factory_new instead of old factory
- Creates persona instances on startup
- Uses instance-based persona tracking
- Integrates new persona API endpoints

### Step 3: Start Services
```bash
# Start API (Port 8080)
cd /opt/ai-personas/src/api && python3 real_factory_api.py

# Start Dashboard (Port 3000)
cd /opt/ai-personas && python3 -m http.server 3000
```

## Creating Persona Instances

### Via API
```bash
curl -X POST http://localhost:8080/api/personas/instances \
  -H "Content-Type: application/json" \
  -d '{
    "persona_type": "frontend-developer",
    "first_name": "Alice",
    "last_name": "Smith",
    "email": "alice.smith@company.com",
    "skills": ["React", "TypeScript", "CSS", "Testing"],
    "mcp_servers": ["memory", "filesystem", "github"],
    "tools": ["vscode", "jest", "webpack"]
  }'
```

### Via Dashboard (Coming Soon)
1. Click "+" button in left panel
2. Select persona type from dropdown
3. Customize name, skills, tools, MCP servers
4. Click "Create Persona"

## Persona Types Available

### Development (7)
- Software Architect (Archy)
- Developer Engineer (Devy)
- Frontend Developer (Frendy)
- Backend Developer (Backy)
- Mobile Developer (Moby)
- AI Engineer (Aidy)
- Data Engineer (Dylan)

### DevOps & Security (5)
- DevSecOps Engineer (Deso)
- Security Engineer (Secy)
- Security Architect (Sophia)
- Site Reliability Engineer (Srey)
- Configuration & Release Engineer (Carl)

### Testing & Quality (1)
- QA/Test Engineer (Quinn)

### Management & Analysis (6)
- Project Manager (Projy)
- Product Owner (Patricia)
- Business Analyst (Brian)
- Requirements Analyst (Rachel)
- Scrum Master (Scrumy)
- Engineering Manager (Engy)

### Design & Documentation (3)
- UI/UX Designer (Uma)
- Technical Writer (Teresa)
- Cloud Architect (Cameron)

### Infrastructure (3)
- Database Administrator (Daby)
- Systems Architect (Simon)
- Integration Engineer (Ivan)

## Legacy Compatibility

The system maintains backward compatibility with existing Steve and Kav processors:
- Steve → Software Architect persona type
- Kav → QA/Test Engineer persona type

Legacy processors are automatically wrapped when creating instances of these types.

## Configuration Files

### settings_extended.json
```json
{
  "version": "2.0",
  "personas": {
    "enabled": true,
    "defaultEmailDomain": "company.com"
  },
  "mcp_servers": { ... },
  "tools": { ... },
  "workflows": { ... }
}
```

### config/personas.json
```json
{
  "version": "2.0",
  "instances": [
    {
      "instance_id": "uuid",
      "persona_type": "software-architect",
      "first_name": "Steve",
      "last_name": "Bot",
      "skills": [...],
      "mcp_servers": [...],
      "tools": [...]
    }
  ]
}
```

## Troubleshooting

### Issue: Old personas not showing
**Solution**: Run the migration script to create default instances

### Issue: API endpoints return 404
**Solution**: Ensure real_factory_api.py is using the new imports

### Issue: Cannot create new personas
**Solution**: Check that processor_factory_new.py is being used

### Issue: Settings not loading
**Solution**: Create settings_extended.json using migration script

## Future Enhancements

### Phase 3 (Dashboard UI)
- Dynamic persona list in left panel
- "+" button for creating new personas
- Settings tabs for Personas, MCP Servers, Tools
- Persona instance management interface

### Phase 4 (Workflow Integration)
- Connect persona workflows to instances
- Implement workflow triggers
- Add workflow execution tracking

### Phase 5 (Advanced Features)
- Persona collaboration features
- Cross-persona communication
- Skill-based task routing
- Performance analytics dashboard