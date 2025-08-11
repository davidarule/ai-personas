"""
Workflow Parser Module

Parses workflow definitions and resolves variable references, conditions, and expressions.
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union
from copy import deepcopy

logger = logging.getLogger(__name__)


class WorkflowParser:
    """Parses workflow steps and resolves dynamic expressions."""
    
    # Regex patterns for variable references
    VAR_PATTERN = re.compile(r'\$\{([^}]+)\}')
    
    # Supported expression operators
    OPERATORS = {
        'eq': lambda a, b: a == b,
        'ne': lambda a, b: a != b,
        'gt': lambda a, b: a > b,
        'lt': lambda a, b: a < b,
        'gte': lambda a, b: a >= b,
        'lte': lambda a, b: a <= b,
        'in': lambda a, b: a in b,
        'not_in': lambda a, b: a not in b,
        'and': lambda a, b: a and b,
        'or': lambda a, b: a or b,
        'not': lambda a: not a,
    }
    
    def __init__(self):
        """Initialize the workflow parser."""
        self.variables = {}
        
    def parse_workflow(self, workflow_def: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parse a workflow definition and prepare it for execution.
        
        Args:
            workflow_def: The workflow definition
            
        Returns:
            Parsed workflow ready for execution
        """
        # Create a deep copy to avoid modifying the original
        parsed = deepcopy(workflow_def)
        
        # Extract input definitions
        input_defs = self._parse_inputs(parsed.get('inputs', []))
        
        # Parse prerequisites
        prerequisites = self._parse_prerequisites(parsed.get('prerequisites', []))
        
        # Parse steps
        steps = self._parse_steps(parsed.get('steps', []))
        
        # Parse outputs
        outputs = self._parse_outputs(parsed.get('outputs', []))
        
        return {
            'metadata': parsed['metadata'],
            'inputs': input_defs,
            'prerequisites': prerequisites,
            'steps': steps,
            'outputs': outputs,
            'successCriteria': parsed.get('successCriteria', []),
            'errorHandling': parsed.get('errorHandling', {})
        }
    
    def _parse_inputs(self, inputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse input definitions."""
        parsed_inputs = []
        
        for input_def in inputs:
            parsed = {
                'name': input_def['name'],
                'type': input_def['type'],
                'required': input_def.get('required', True),
                'description': input_def.get('description', ''),
            }
            
            # Add type-specific attributes
            if 'default' in input_def:
                parsed['default'] = input_def['default']
            if 'values' in input_def and input_def['type'] == 'enum':
                parsed['values'] = input_def['values']
            if 'pattern' in input_def and input_def['type'] == 'string':
                parsed['pattern'] = re.compile(input_def['pattern'])
                
            parsed_inputs.append(parsed)
            
        return parsed_inputs
    
    def _parse_prerequisites(self, prerequisites: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse prerequisite definitions."""
        parsed_prereqs = []
        
        for prereq in prerequisites:
            parsed = {
                'description': prereq['description'],
                'required': prereq.get('required', True)
            }
            
            if 'check' in prereq:
                parsed['check'] = prereq['check']
                
            parsed_prereqs.append(parsed)
            
        return parsed_prereqs
    
    def _parse_steps(self, steps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse workflow steps."""
        parsed_steps = []
        
        for step in steps:
            parsed = {
                'id': step['id'],
                'action': step['action'],
                'name': step.get('name', step['id']),
                'description': step.get('description', ''),
                'onError': step.get('onError', 'fail'),
                'retryCount': step.get('retryCount', 3),
            }
            
            # Parse action-specific attributes
            if step['action'] == 'execute-workflow':
                parsed['workflow'] = step['workflow']
                parsed['inputs'] = step.get('inputs', {})
                
            elif step['action'] == 'shell-command':
                parsed['command'] = step['command']
                parsed['timeout'] = self._parse_timeout(step.get('timeout', '5m'))
                
            elif step['action'] in ['git-operation', 'azure-devops']:
                parsed['operation'] = step['operation']
                parsed['inputs'] = step.get('inputs', {})
                
            elif step['action'] in ['conditional', 'while-loop', 'for-loop']:
                parsed['condition'] = step['condition']
                parsed['steps'] = self._parse_steps(step.get('steps', []))
                
            elif step['action'] == 'parallel':
                parsed['steps'] = self._parse_steps(step.get('steps', []))
                
            elif step['action'] == 'wait':
                parsed['duration'] = self._parse_timeout(step.get('duration', '1s'))
                
            elif step['action'] == 'set-variable':
                parsed['variable'] = step['variable']
                parsed['value'] = step['value']
                
            elif step['action'] == 'log':
                parsed['message'] = step['message']
                parsed['level'] = step.get('level', 'info')
            
            # Parse outputs to capture
            if 'outputs' in step:
                parsed['outputs'] = step['outputs']
                
            parsed_steps.append(parsed)
            
        return parsed_steps
    
    def _parse_outputs(self, outputs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Parse output definitions."""
        parsed_outputs = []
        
        for output in outputs:
            parsed = {
                'name': output['name'],
                'value': output['value'],
                'description': output.get('description', '')
            }
            parsed_outputs.append(parsed)
            
        return parsed_outputs
    
    def _parse_timeout(self, timeout_str: str) -> int:
        """Parse timeout string to seconds."""
        match = re.match(r'^(\d+)([smh])$', timeout_str)
        if not match:
            raise ValueError(f"Invalid timeout format: {timeout_str}")
            
        value, unit = match.groups()
        value = int(value)
        
        if unit == 's':
            return value
        elif unit == 'm':
            return value * 60
        elif unit == 'h':
            return value * 3600
    
    def resolve_expression(self, expression: str, context: Dict[str, Any]) -> Any:
        """
        Resolve a variable expression or condition.
        
        Args:
            expression: The expression to resolve (e.g., "${inputs.FEATURE_ID}")
            context: The execution context containing variables
            
        Returns:
            The resolved value
        """
        if not isinstance(expression, str):
            return expression
            
        # Handle simple variable references
        matches = self.VAR_PATTERN.findall(expression)
        if len(matches) == 1 and expression == f"${{{matches[0]}}}":
            # This is a pure variable reference
            return self._resolve_path(matches[0], context)
        
        # Handle string interpolation
        result = expression
        for match in matches:
            value = self._resolve_path(match, context)
            result = result.replace(f"${{{match}}}", str(value))
            
        return result
    
    def _resolve_path(self, path: str, context: Dict[str, Any]) -> Any:
        """Resolve a dot-notation path in the context."""
        parts = path.split('.')
        value = context
        
        for part in parts:
            if isinstance(value, dict) and part in value:
                value = value[part]
            else:
                logger.warning(f"Unable to resolve path: {path}")
                return None
                
        return value
    
    def evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """
        Evaluate a condition expression.
        
        Args:
            condition: The condition to evaluate
            context: The execution context
            
        Returns:
            Boolean result of the condition
        """
        # First resolve any variable references
        resolved_condition = self.resolve_expression(condition, context)
        
        # If it's already a boolean, return it
        if isinstance(resolved_condition, bool):
            return resolved_condition
            
        # Parse complex conditions (simplified for now)
        # In a full implementation, this would use a proper expression parser
        try:
            # Handle simple comparisons
            for op_name, op_func in self.OPERATORS.items():
                if f' {op_name} ' in str(resolved_condition):
                    parts = str(resolved_condition).split(f' {op_name} ')
                    if len(parts) == 2:
                        left = self._parse_value(parts[0].strip())
                        right = self._parse_value(parts[1].strip())
                        return op_func(left, right)
            
            # Try to evaluate as Python expression (careful with security!)
            # In production, use a safe expression evaluator
            return bool(resolved_condition)
            
        except Exception as e:
            logger.error(f"Failed to evaluate condition '{condition}': {e}")
            return False
    
    def _parse_value(self, value_str: str) -> Any:
        """Parse a string value to its appropriate type."""
        value_str = value_str.strip()
        
        # Boolean
        if value_str.lower() in ['true', 'false']:
            return value_str.lower() == 'true'
            
        # Number
        try:
            if '.' in value_str:
                return float(value_str)
            return int(value_str)
        except ValueError:
            pass
            
        # String (remove quotes if present)
        if value_str.startswith('"') and value_str.endswith('"'):
            return value_str[1:-1]
        if value_str.startswith("'") and value_str.endswith("'"):
            return value_str[1:-1]
            
        return value_str
    
    def validate_inputs(self, input_defs: List[Dict[str, Any]], 
                       provided_inputs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate and normalize provided inputs against definitions.
        
        Args:
            input_defs: Input definitions from workflow
            provided_inputs: User-provided inputs
            
        Returns:
            Validated and normalized inputs
            
        Raises:
            ValueError: If validation fails
        """
        validated = {}
        
        for input_def in input_defs:
            name = input_def['name']
            
            # Check if required input is provided
            if input_def['required'] and name not in provided_inputs:
                if 'default' in input_def:
                    validated[name] = input_def['default']
                else:
                    raise ValueError(f"Required input '{name}' not provided")
            
            elif name in provided_inputs:
                value = provided_inputs[name]
                
                # Type validation
                if input_def['type'] == 'enum' and 'values' in input_def:
                    if value not in input_def['values']:
                        raise ValueError(
                            f"Input '{name}' must be one of {input_def['values']}"
                        )
                
                elif input_def['type'] == 'string' and 'pattern' in input_def:
                    if not input_def['pattern'].match(str(value)):
                        raise ValueError(
                            f"Input '{name}' does not match required pattern"
                        )
                
                validated[name] = value
        
        return validated