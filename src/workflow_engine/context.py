"""
Workflow Context Module

Manages the execution context for workflows, including variables, state, and history.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from copy import deepcopy

logger = logging.getLogger(__name__)


class WorkflowContext:
    """Manages execution context for a workflow."""
    
    def __init__(self, workflow_id: str, inputs: Optional[Dict[str, Any]] = None):
        """
        Initialize workflow context.
        
        Args:
            workflow_id: The ID of the workflow being executed
            inputs: Initial input values
        """
        self.workflow_id = workflow_id
        self.start_time = datetime.utcnow()
        self.end_time = None
        self.status = "running"
        
        # Variable scopes
        self.variables = {
            'inputs': inputs or {},
            'outputs': {},
            'context': {
                'workflow_id': workflow_id,
                'start_time': self.start_time.isoformat(),
                'execution_id': self._generate_execution_id()
            },
            'steps': {},
            'temp': {}
        }
        
        # Execution history
        self.history = []
        self.errors = []
        self.current_step = None
        
    def _generate_execution_id(self) -> str:
        """Generate a unique execution ID."""
        timestamp = self.start_time.strftime("%Y%m%d%H%M%S")
        return f"{self.workflow_id}-{timestamp}"
    
    def get_variable(self, path: str, default: Any = None) -> Any:
        """
        Get a variable value by path.
        
        Args:
            path: Dot-notation path (e.g., "inputs.FEATURE_ID")
            default: Default value if not found
            
        Returns:
            The variable value or default
        """
        parts = path.split('.')
        value = self.variables
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                return default
                
        return value
    
    def set_variable(self, path: str, value: Any) -> None:
        """
        Set a variable value by path.
        
        Args:
            path: Dot-notation path
            value: Value to set
        """
        parts = path.split('.')
        target = self.variables
        
        # Navigate to the parent
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
            
        # Set the value
        target[parts[-1]] = value
        
        logger.debug(f"Set variable {path} = {value}")
    
    def set_step_output(self, step_id: str, outputs: Dict[str, Any]) -> None:
        """
        Store outputs from a step execution.
        
        Args:
            step_id: The step identifier
            outputs: Output values from the step
        """
        self.variables['steps'][step_id] = outputs
        
        # Also update the context namespace for convenience
        for key, value in outputs.items():
            self.set_variable(f'context.{key}', value)
    
    def add_to_history(self, event: Dict[str, Any]) -> None:
        """
        Add an event to the execution history.
        
        Args:
            event: Event data to record
        """
        event['timestamp'] = datetime.utcnow().isoformat()
        self.history.append(event)
        
    def record_step_start(self, step: Dict[str, Any]) -> None:
        """Record the start of a step execution."""
        self.current_step = step['id']
        self.add_to_history({
            'type': 'step_start',
            'step_id': step['id'],
            'step_name': step.get('name', step['id']),
            'action': step['action']
        })
    
    def record_step_complete(self, step: Dict[str, Any], 
                            outputs: Optional[Dict[str, Any]] = None) -> None:
        """Record successful step completion."""
        self.add_to_history({
            'type': 'step_complete',
            'step_id': step['id'],
            'outputs': outputs or {}
        })
        self.current_step = None
    
    def record_step_error(self, step: Dict[str, Any], error: Exception) -> None:
        """Record a step execution error."""
        error_data = {
            'type': 'step_error',
            'step_id': step['id'],
            'error_type': type(error).__name__,
            'error_message': str(error)
        }
        
        self.add_to_history(error_data)
        self.errors.append(error_data)
        self.current_step = None
    
    def record_workflow_complete(self, outputs: Dict[str, Any]) -> None:
        """Record workflow completion."""
        self.end_time = datetime.utcnow()
        self.status = "completed"
        self.variables['outputs'] = outputs
        
        self.add_to_history({
            'type': 'workflow_complete',
            'duration': (self.end_time - self.start_time).total_seconds(),
            'outputs': outputs
        })
    
    def record_workflow_error(self, error: Exception) -> None:
        """Record workflow-level error."""
        self.end_time = datetime.utcnow()
        self.status = "failed"
        
        error_data = {
            'type': 'workflow_error',
            'error_type': type(error).__name__,
            'error_message': str(error),
            'duration': (self.end_time - self.start_time).total_seconds()
        }
        
        self.add_to_history(error_data)
        self.errors.append(error_data)
    
    def create_child_context(self, workflow_id: str, inputs: Dict[str, Any]) -> 'WorkflowContext':
        """
        Create a child context for sub-workflow execution.
        
        Args:
            workflow_id: ID of the child workflow
            inputs: Inputs for the child workflow
            
        Returns:
            New context for child workflow
        """
        child = WorkflowContext(workflow_id, inputs)
        
        # Inherit parent context values
        child.variables['parent'] = {
            'workflow_id': self.workflow_id,
            'execution_id': self.get_variable('context.execution_id')
        }
        
        return child
    
    def merge_child_outputs(self, child_context: 'WorkflowContext') -> Dict[str, Any]:
        """
        Merge outputs from a child workflow execution.
        
        Args:
            child_context: The child workflow context
            
        Returns:
            Child workflow outputs
        """
        return child_context.variables.get('outputs', {})
    
    @property
    def execution_time(self) -> float:
        """Get execution time in seconds."""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        else:
            return (datetime.utcnow() - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary for serialization.
        
        Returns:
            Dictionary representation of the context
        """
        return {
            'workflow_id': self.workflow_id,
            'execution_id': self.get_variable('context.execution_id'),
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'variables': deepcopy(self.variables),
            'history': self.history,
            'errors': self.errors
        }
    
    def get_execution_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the workflow execution.
        
        Returns:
            Execution summary
        """
        duration = None
        if self.end_time:
            duration = (self.end_time - self.start_time).total_seconds()
        
        return {
            'workflow_id': self.workflow_id,
            'execution_id': self.get_variable('context.execution_id'),
            'status': self.status,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration': duration,
            'steps_executed': len([h for h in self.history if h['type'] == 'step_start']),
            'steps_completed': len([h for h in self.history if h['type'] == 'step_complete']),
            'errors': len(self.errors),
            'outputs': self.variables.get('outputs', {})
        }