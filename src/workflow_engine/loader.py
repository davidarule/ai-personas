"""
Workflow Loader Module

Handles loading and validation of workflow definitions from YAML/JSON files.
"""

import json
import yaml
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from jsonschema import validate, ValidationError, Draft7Validator

logger = logging.getLogger(__name__)


class WorkflowLoader:
    """Loads and validates workflow definitions from files."""
    
    def __init__(self, workflows_dir: Optional[Path] = None):
        """
        Initialize the workflow loader.
        
        Args:
            workflows_dir: Path to workflows directory. Defaults to src/workflows
        """
        if workflows_dir is None:
            workflows_dir = Path(__file__).parent.parent / "workflows"
        
        self.workflows_dir = Path(workflows_dir)
        self.definitions_dir = self.workflows_dir / "definitions"
        self.schemas_dir = self.workflows_dir / "schemas"
        self._schema = None
        self._workflows_cache = {}
        
    @property
    def schema(self) -> Dict[str, Any]:
        """Load and cache the workflow schema."""
        if self._schema is None:
            schema_path = self.schemas_dir / "workflow-schema.json"
            if not schema_path.exists():
                raise FileNotFoundError(f"Workflow schema not found at {schema_path}")
            
            with open(schema_path, 'r') as f:
                self._schema = json.load(f)
        
        return self._schema
    
    def load_workflow(self, workflow_id: str, force_reload: bool = False) -> Dict[str, Any]:
        """
        Load a workflow definition by ID.
        
        Args:
            workflow_id: The workflow identifier
            force_reload: Force reload from disk even if cached
            
        Returns:
            The validated workflow definition
            
        Raises:
            FileNotFoundError: If workflow file doesn't exist
            ValidationError: If workflow doesn't match schema
        """
        if not force_reload and workflow_id in self._workflows_cache:
            return self._workflows_cache[workflow_id]
        
        # Search for workflow file in subdirectories
        workflow_file = None
        for subdir in ['master', 'core', 'support', 'utility']:
            for ext in ['.yaml', '.yml', '.json']:
                path = self.definitions_dir / subdir / f"{workflow_id}{ext}"
                if path.exists():
                    workflow_file = path
                    break
            if workflow_file:
                break
        
        if not workflow_file:
            raise FileNotFoundError(f"Workflow '{workflow_id}' not found in {self.definitions_dir}")
        
        # Load the workflow file
        workflow_data = self._load_file(workflow_file)
        
        # Validate against schema
        self.validate_workflow(workflow_data)
        
        # Cache the workflow
        self._workflows_cache[workflow_id] = workflow_data
        
        logger.info(f"Loaded workflow '{workflow_id}' from {workflow_file}")
        return workflow_data
    
    def load_all_workflows(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all workflow definitions from the definitions directory.
        
        Returns:
            Dictionary mapping workflow IDs to their definitions
        """
        workflows = {}
        
        for subdir in ['master', 'core', 'support', 'utility']:
            subdir_path = self.definitions_dir / subdir
            if not subdir_path.exists():
                continue
                
            for file_path in subdir_path.iterdir():
                if file_path.suffix in ['.yaml', '.yml', '.json']:
                    try:
                        workflow_data = self._load_file(file_path)
                        self.validate_workflow(workflow_data)
                        
                        workflow_id = workflow_data['metadata']['id']
                        workflows[workflow_id] = workflow_data
                        self._workflows_cache[workflow_id] = workflow_data
                        
                        logger.info(f"Loaded workflow '{workflow_id}' from {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to load workflow from {file_path}: {e}")
        
        return workflows
    
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> None:
        """
        Validate a workflow definition against the schema.
        
        Args:
            workflow_data: The workflow definition to validate
            
        Raises:
            ValidationError: If validation fails
        """
        try:
            validate(instance=workflow_data, schema=self.schema)
        except ValidationError as e:
            # Provide more detailed error message
            validator = Draft7Validator(self.schema)
            errors = sorted(validator.iter_errors(workflow_data), key=lambda e: e.path)
            
            error_messages = []
            for error in errors:
                path = " -> ".join([str(p) for p in error.path])
                if path:
                    error_messages.append(f"At {path}: {error.message}")
                else:
                    error_messages.append(error.message)
            
            raise ValidationError(f"Workflow validation failed:\n" + "\n".join(error_messages))
    
    def save_workflow(self, workflow_data: Dict[str, Any], format: str = 'yaml') -> Path:
        """
        Save a workflow definition to file.
        
        Args:
            workflow_data: The workflow definition to save
            format: File format ('yaml' or 'json')
            
        Returns:
            Path to the saved file
        """
        # Validate before saving
        self.validate_workflow(workflow_data)
        
        metadata = workflow_data['metadata']
        workflow_id = metadata['id']
        workflow_type = metadata['type']
        
        # Determine file path
        subdir = self.definitions_dir / workflow_type
        subdir.mkdir(parents=True, exist_ok=True)
        
        ext = '.yaml' if format == 'yaml' else '.json'
        file_path = subdir / f"{workflow_id}{ext}"
        
        # Save the file
        with open(file_path, 'w') as f:
            if format == 'yaml':
                yaml.dump(workflow_data, f, default_flow_style=False, sort_keys=False)
            else:
                json.dump(workflow_data, f, indent=2)
        
        # Update cache
        self._workflows_cache[workflow_id] = workflow_data
        
        logger.info(f"Saved workflow '{workflow_id}' to {file_path}")
        return file_path
    
    def _load_file(self, file_path: Path) -> Dict[str, Any]:
        """Load a YAML or JSON file."""
        with open(file_path, 'r') as f:
            if file_path.suffix in ['.yaml', '.yml']:
                return yaml.safe_load(f)
            else:
                return json.load(f)
    
    def list_workflows(self, workflow_type: Optional[str] = None) -> List[Dict[str, str]]:
        """
        List available workflows.
        
        Args:
            workflow_type: Filter by workflow type (master, core, support, utility)
            
        Returns:
            List of workflow metadata summaries
        """
        workflows = []
        
        subdirs = [workflow_type] if workflow_type else ['master', 'core', 'support', 'utility']
        
        for subdir in subdirs:
            subdir_path = self.definitions_dir / subdir
            if not subdir_path.exists():
                continue
                
            for file_path in subdir_path.iterdir():
                if file_path.suffix in ['.yaml', '.yml', '.json']:
                    try:
                        workflow_data = self._load_file(file_path)
                        metadata = workflow_data.get('metadata', {})
                        workflows.append({
                            'id': metadata.get('id'),
                            'name': metadata.get('name'),
                            'type': metadata.get('type'),
                            'version': metadata.get('version'),
                            'description': metadata.get('description'),
                            'file': str(file_path.relative_to(self.workflows_dir))
                        })
                    except Exception as e:
                        logger.error(f"Failed to read metadata from {file_path}: {e}")
        
        return workflows