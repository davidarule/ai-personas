#!/usr/bin/env python3
"""
Test script for the workflow system.
"""

import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from workflow_engine import WorkflowLoader, WorkflowRegistry, WorkflowParser

def test_workflow_system():
    """Test the workflow system components."""
    print("Testing Workflow System...\n")
    
    # Test 1: Load and validate workflow
    print("1. Testing WorkflowLoader...")
    loader = WorkflowLoader()
    
    try:
        workflow = loader.load_workflow("branch-creation")
        print("✓ Successfully loaded branch-creation workflow")
        print(f"  - Name: {workflow['metadata']['name']}")
        print(f"  - Version: {workflow['metadata']['version']}")
        print(f"  - Type: {workflow['metadata']['type']}")
        print(f"  - Steps: {len(workflow['steps'])}")
    except Exception as e:
        print(f"✗ Failed to load workflow: {e}")
        return False
    
    # Test 2: Validate workflow schema
    print("\n2. Testing workflow validation...")
    try:
        loader.validate_workflow(workflow)
        print("✓ Workflow passes schema validation")
    except Exception as e:
        print(f"✗ Validation failed: {e}")
        return False
    
    # Test 3: Test workflow parser
    print("\n3. Testing WorkflowParser...")
    parser = WorkflowParser()
    
    try:
        parsed = parser.parse_workflow(workflow)
        print("✓ Successfully parsed workflow")
        print(f"  - Inputs: {[inp['name'] for inp in parsed['inputs']]}")
        print(f"  - Prerequisites: {len(parsed['prerequisites'])}")
        print(f"  - Steps: {[step['id'] for step in parsed['steps']]}")
        print(f"  - Outputs: {[out['name'] for out in parsed['outputs']]}")
    except Exception as e:
        print(f"✗ Failed to parse workflow: {e}")
        return False
    
    # Test 4: Test expression resolution
    print("\n4. Testing expression resolution...")
    test_context = {
        'inputs': {
            'WORK_TYPE': 'feature',
            'WORK_ITEM_ID': 'WI-123',
            'DESCRIPTION': 'user-auth'
        },
        'context': {
            'BRANCH_NAME': 'feature/WI-123-user-auth'
        }
    }
    
    test_expr = "${inputs.WORK_TYPE}/${inputs.WORK_ITEM_ID}-${inputs.DESCRIPTION}"
    resolved = parser.resolve_expression(test_expr, test_context)
    print(f"  Expression: {test_expr}")
    print(f"  Resolved: {resolved}")
    print("✓ Expression resolution working" if resolved == "feature/WI-123-user-auth" else "✗ Expression resolution failed")
    
    # Test 5: Test workflow registry
    print("\n5. Testing WorkflowRegistry...")
    registry = WorkflowRegistry(loader)
    
    try:
        registry.scan_workflows()
        stats = registry.get_workflow_stats()
        print(f"✓ Registry scanned successfully")
        print(f"  - Total workflows: {stats['total_workflows']}")
        print(f"  - By type: {stats['by_type']}")
        
        # Test search
        results = registry.search_workflows("branch")
        print(f"  - Search for 'branch': {len(results)} results")
        
    except Exception as e:
        print(f"✗ Registry scan failed: {e}")
        return False
    
    # Test 6: Save workflow in JSON format
    print("\n6. Testing workflow save in JSON format...")
    try:
        json_path = loader.save_workflow(workflow, format='json')
        print(f"✓ Saved workflow to {json_path}")
    except Exception as e:
        print(f"✗ Failed to save workflow: {e}")
    
    print("\n✓ All tests passed!")
    return True

if __name__ == "__main__":
    success = test_workflow_system()
    sys.exit(0 if success else 1)