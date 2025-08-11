"""
Workflow API endpoints for serving workflow definitions.
"""

import os
import json
import yaml
from typing import Dict, List, Any
from pathlib import Path
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Base path for workflows
WORKFLOWS_BASE = Path(__file__).parent.parent / 'workflows' / 'definitions'
INDEX_PATH = Path(__file__).parent.parent / 'workflows' / 'index.json'


def load_workflow_file(file_path: Path) -> Dict[str, Any]:
    """Load a workflow file (YAML or JSON)."""
    try:
        with open(file_path, 'r') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None


def convert_workflow_for_ui(workflow_data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert workflow data to UI format."""
    metadata = workflow_data.get('metadata', {})
    
    # Build description in markdown format
    description_parts = ['## Metadata']
    description_parts.append(f"- **Workflow Type**: {metadata.get('type', 'unknown')}")
    description_parts.append(f"- **Version**: {metadata.get('version', '1.0.0')}")
    description_parts.append(f"- **Purpose**: {metadata.get('description', '')}")
    description_parts.append(f"- **Average Duration**: {metadata.get('averageDuration', 'Unknown')}")
    
    # Add inputs section
    if 'inputs' in workflow_data:
        description_parts.append('\n## Inputs')
        for input_item in workflow_data['inputs']:
            name = input_item.get('name', '')
            desc = input_item.get('description', '')
            required = ' (required)' if input_item.get('required', False) else ' (optional)'
            description_parts.append(f"- **{name}**: {desc}{required}")
    
    # Add prerequisites
    if 'prerequisites' in workflow_data:
        description_parts.append('\n## Prerequisites')
        for prereq in workflow_data['prerequisites']:
            description_parts.append(f"- {prereq.get('description', '')}")
    
    # Add steps overview
    if 'steps' in workflow_data:
        description_parts.append('\n## Steps')
        for i, step in enumerate(workflow_data['steps'], 1):
            step_name = step.get('name', f"Step {i}")
            step_desc = step.get('description', '')
            description_parts.append(f"{i}. **{step_name}**: {step_desc}")
    
    # Add outputs
    if 'outputs' in workflow_data:
        description_parts.append('\n## Outputs')
        for output in workflow_data['outputs']:
            name = output.get('name', '')
            desc = output.get('description', '')
            description_parts.append(f"- **{name}**: {desc}")
    
    # Add success criteria
    if 'successCriteria' in workflow_data:
        description_parts.append('\n## Success Criteria')
        for criterion in workflow_data['successCriteria']:
            description_parts.append(f"- {criterion}")
    
    return {
        'id': metadata.get('id', 'unknown'),
        'name': metadata.get('name', 'Unknown Workflow'),
        'description': '\n'.join(description_parts)
    }


@app.route('/api/workflows', methods=['GET'])
def get_workflows():
    """Get all available workflows."""
    workflows = []
    
    # Always scan directories directly to get all workflows
    # This ensures we load all 14 workflows, not just the 6 in the outdated index.json
    for subdir in ['master', 'core', 'support']:
        subdir_path = WORKFLOWS_BASE / subdir
        if subdir_path.exists():
            for file_path in subdir_path.glob('wf*.yaml'):
                print(f"Loading workflow: {file_path}")
                workflow_data = load_workflow_file(file_path)
                if workflow_data:
                    ui_workflow = convert_workflow_for_ui(workflow_data)
                    workflows.append(ui_workflow)
                    print(f"  ✓ Loaded: {ui_workflow['id']}")
                else:
                    print(f"  ✗ Failed to load: {file_path}")
    
    # Sort workflows by ID
    workflows.sort(key=lambda x: int(x['id'].replace('wf', '').split('-')[0]) if x['id'].startswith('wf') else 999)
    
    return jsonify({
        'success': True,
        'workflows': workflows,
        'count': len(workflows)
    })


@app.route('/api/workflows/<workflow_id>', methods=['GET'])
def get_workflow(workflow_id):
    """Get a specific workflow by ID."""
    # Find the workflow file
    workflow_file = None
    for subdir in ['master', 'core', 'support']:
        for ext in ['.yaml', '.yml', '.json']:
            path = WORKFLOWS_BASE / subdir / f"{workflow_id}{ext}"
            if path.exists():
                workflow_file = path
                break
        if workflow_file:
            break
    
    if not workflow_file:
        return jsonify({'success': False, 'error': 'Workflow not found'}), 404
    
    workflow_data = load_workflow_file(workflow_file)
    if not workflow_data:
        return jsonify({'success': False, 'error': 'Failed to load workflow'}), 500
    
    return jsonify({
        'success': True,
        'workflow': workflow_data
    })


if __name__ == '__main__':
    app.run(port=8081, debug=True)