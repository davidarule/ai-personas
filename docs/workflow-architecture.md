# AI Personas Workflow Architecture

## Overview

The AI Personas system now includes a comprehensive workflow engine that enables personas to discover, load, and execute structured workflows. This architecture separates workflow definitions from UI code and provides programmatic access for personas to automate complex development processes.

## Architecture Components

### 1. Workflow Storage (`src/workflows/`)

```
src/workflows/
├── definitions/          # Individual workflow YAML/JSON files
│   ├── master/          # Orchestration workflows
│   ├── core/            # Core development workflows
│   └── support/         # Supporting workflows
├── schemas/             # JSON Schema for validation
│   └── workflow-schema.json
└── index.json          # Auto-generated registry index
```

### 2. Workflow Engine (`src/workflow_engine/`)

- **WorkflowLoader**: Loads and validates workflow definitions
- **WorkflowParser**: Parses expressions and resolves variables
- **WorkflowContext**: Manages execution state and variables
- **WorkflowRegistry**: Discovers and indexes available workflows
- **WorkflowExecutor**: Executes workflow steps

### 3. Persona Integration

- **WorkflowEnabledProcessor**: Base class adding workflow capabilities
- **Workflow-aware personas**: Enhanced personas that can execute workflows

## Workflow Definition Format

Workflows are defined in YAML with the following structure:

```yaml
metadata:
  id: unique-workflow-id
  name: Human Readable Name
  version: 1.0.0
  type: master|core|support|utility
  description: Detailed description

inputs:
  - name: PARAMETER_NAME
    type: string|number|boolean|enum
    required: true
    description: Parameter description

prerequisites:
  - description: What must be true before execution
    check: Optional automated check
    required: true

steps:
  - id: step-id
    name: Step Name
    action: execute-workflow|shell-command|git-operation|etc
    inputs:
      key: value
    outputs:
      - VARIABLE_NAME

outputs:
  - name: OUTPUT_NAME
    value: ${expression}
    description: Output description

successCriteria:
  - What constitutes success

errorHandling:
  strategy: fail-fast|continue-on-error|rollback
```

## Expression Language

The workflow engine supports variable resolution using `${path.to.variable}` syntax:

- `${inputs.PARAMETER}` - Access input parameters
- `${context.variable}` - Access context variables
- `${steps.step-id.OUTPUT}` - Access step outputs
- `${outputs.NAME}` - Access workflow outputs

## Available Actions

1. **execute-workflow**: Execute another workflow
2. **shell-command**: Run shell commands
3. **git-operation**: Perform git operations
4. **azure-devops**: Interact with Azure DevOps
5. **conditional**: If-then logic
6. **while-loop**: Repeat until condition
7. **parallel**: Execute steps in parallel
8. **set-variable**: Set context variables
9. **log**: Log messages

## Using Workflows in Personas

### 1. Basic Workflow Execution

```python
from workflow_enabled_processor import WorkflowEnabledProcessor

class MyPersona(WorkflowEnabledProcessor):
    async def process_work_item(self, work_item):
        # Execute a workflow
        result = await self.execute_workflow('feature-development', {
            'FEATURE_ID': work_item['id'],
            'FEATURE_DESCRIPTION': 'my-feature',
            'PRIORITY': 'high'
        })
        
        if result['success']:
            print(f"Branch created: {result['outputs']['FEATURE_BRANCH']}")
```

### 2. Discovering Workflows

```python
# List all workflows
workflows = persona.discover_workflows()

# Filter by type
master_workflows = persona.discover_workflows(workflow_type='master')

# Search workflows
matching = persona.search_workflows('branch')

# Get recommended workflows for a work item
recommended = persona.get_recommended_workflows(work_item)
```

### 3. Processing Work Items with Workflows

```python
# Automatic workflow selection and execution
result = await persona.process_work_item_with_workflow(
    work_item, 
    'feature-development'
)
```

## Migrating from Hardcoded Workflows

1. Extract workflow from `index.html`
2. Convert to YAML format
3. Place in appropriate directory (`master/`, `core/`, `support/`)
4. Validate with schema
5. Test with workflow executor
6. Update UI to load dynamically

## Testing Workflows

Run the test script to validate the workflow system:

```bash
python3 test_workflow_system.py
```

## Benefits

1. **Separation of Concerns**: Workflows separate from UI code
2. **Reusability**: Personas can discover and execute any workflow
3. **Maintainability**: Version-controlled, validated workflows
4. **Extensibility**: Easy to add new workflows and actions
5. **Testability**: Workflows can be unit tested
6. **Discoverability**: Registry provides search and filtering

## Next Steps

1. Complete migration of all workflows from `index.html`
2. Implement remaining workflow actions (git, Azure DevOps)
3. Add workflow execution UI in the dashboard
4. Create workflow editor interface
5. Implement workflow versioning and rollback
6. Add workflow metrics and monitoring

## Example: Security Workflow Integration

The `SteveWorkflowProcessor` demonstrates how security personas can leverage workflows:

```python
# Automatically selects appropriate workflow based on work item
if 'vulnerability' in work_item['title']:
    workflow = 'bug-fix'  # or 'hotfix' for critical
elif 'compliance' in work_item['title']:
    workflow = 'feature-development'

# Executes with security-specific context
result = await steve.execute_security_workflow(workflow, {
    'PRIORITY': 'high',  # Security is always high priority
    'WORK_ITEM_ID': work_item['id']
})
```

This architecture provides a robust foundation for automated development workflows that can be shared and executed by all AI personas in the system.