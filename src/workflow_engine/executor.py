"""
Workflow Executor Module

Executes workflow definitions step by step.
"""

import logging
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime

from .loader import WorkflowLoader
from .parser import WorkflowParser
from .context import WorkflowContext
from .registry import WorkflowRegistry

logger = logging.getLogger(__name__)


class WorkflowExecutor:
    """Executes workflow definitions."""
    
    def __init__(self, registry: Optional[WorkflowRegistry] = None):
        """
        Initialize workflow executor.
        
        Args:
            registry: WorkflowRegistry instance
        """
        self.registry = registry or WorkflowRegistry()
        self.parser = WorkflowParser()
        self.active_executions = {}
        
    async def execute_workflow(self, workflow_id: str, 
                             inputs: Optional[Dict[str, Any]] = None) -> WorkflowContext:
        """
        Execute a workflow by ID.
        
        Args:
            workflow_id: The workflow to execute
            inputs: Input parameters
            
        Returns:
            Execution context with results
        """
        # Get workflow definition
        workflow_def = self.registry.get_workflow(workflow_id)
        if not workflow_def:
            raise ValueError(f"Workflow '{workflow_id}' not found")
        
        # Parse workflow
        parsed_workflow = self.parser.parse_workflow(workflow_def)
        
        # Validate inputs
        validated_inputs = self.parser.validate_inputs(
            parsed_workflow['inputs'], 
            inputs or {}
        )
        
        # Create execution context
        context = WorkflowContext(workflow_id, validated_inputs)
        
        # Store active execution
        execution_id = context.get_variable('context.execution_id')
        self.active_executions[execution_id] = context
        
        try:
            # Check prerequisites
            await self._check_prerequisites(parsed_workflow['prerequisites'], context)
            
            # Execute steps
            await self._execute_steps(parsed_workflow['steps'], context)
            
            # Compute outputs
            outputs = await self._compute_outputs(parsed_workflow['outputs'], context)
            
            # Record completion
            context.record_workflow_complete(outputs)
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            context.record_workflow_error(e)
            raise
        finally:
            # Remove from active executions
            del self.active_executions[execution_id]
        
        return context
    
    async def _check_prerequisites(self, prerequisites: List[Dict[str, Any]], 
                                 context: WorkflowContext) -> None:
        """Check workflow prerequisites."""
        logger.info("Checking prerequisites...")
        
        for prereq in prerequisites:
            if prereq.get('required', True):
                # In a real implementation, this would execute the check
                logger.info(f"Checking: {prereq['description']}")
                # For now, we'll assume all prerequisites pass
    
    async def _execute_steps(self, steps: List[Dict[str, Any]], 
                           context: WorkflowContext) -> None:
        """Execute workflow steps."""
        for step in steps:
            await self._execute_step(step, context)
    
    async def _execute_step(self, step: Dict[str, Any], 
                          context: WorkflowContext) -> None:
        """Execute a single workflow step."""
        logger.info(f"Executing step: {step['id']} ({step['action']})")
        context.record_step_start(step)
        
        try:
            # Execute based on action type
            if step['action'] == 'execute-workflow':
                outputs = await self._execute_workflow_action(step, context)
            elif step['action'] == 'shell-command':
                outputs = await self._execute_shell_action(step, context)
            elif step['action'] == 'git-operation':
                outputs = await self._execute_git_action(step, context)
            elif step['action'] == 'set-variable':
                outputs = await self._execute_set_variable_action(step, context)
            elif step['action'] == 'log':
                outputs = await self._execute_log_action(step, context)
            elif step['action'] in ['conditional', 'while-loop', 'for-loop']:
                outputs = await self._execute_control_flow_action(step, context)
            elif step['action'] == 'azure-devops':
                outputs = await self._execute_azure_devops_action(step, context)
            elif step['action'] == 'parallel':
                outputs = await self._execute_parallel_action(step, context)
            elif step['action'] == 'wait':
                outputs = await self._execute_wait_action(step, context)
            else:
                raise ValueError(f"Unknown action type: {step['action']}")
            
            # Store step outputs
            if outputs and 'outputs' in step:
                context.set_step_output(step['id'], outputs)
            
            context.record_step_complete(step, outputs)
            
        except Exception as e:
            logger.error(f"Step {step['id']} failed: {e}")
            context.record_step_error(step, e)
            
            # Handle error based on strategy
            if step.get('onError', 'fail') == 'fail':
                raise
            elif step['onError'] == 'continue':
                logger.warning(f"Continuing after error in step {step['id']}")
            elif step['onError'] == 'retry':
                # Implement retry logic
                pass
    
    async def _execute_workflow_action(self, step: Dict[str, Any], 
                                     context: WorkflowContext) -> Dict[str, Any]:
        """Execute a sub-workflow."""
        workflow_id = step['workflow']
        
        # Resolve input expressions
        inputs = {}
        for key, value in step.get('inputs', {}).items():
            inputs[key] = self.parser.resolve_expression(value, context.to_dict())
        
        # Create child context and execute
        child_context = context.create_child_context(workflow_id, inputs)
        await self.execute_workflow(workflow_id, inputs)
        
        return context.merge_child_outputs(child_context)
    
    async def _execute_shell_action(self, step: Dict[str, Any], 
                                   context: WorkflowContext) -> Dict[str, Any]:
        """Execute a shell command."""
        command = self.parser.resolve_expression(step['command'], context.to_dict())
        logger.info(f"Executing shell command: {command}")
        
        # In a real implementation, this would execute the command
        # For now, return mock output
        return {'output': f"Output from: {command}"}
    
    
    async def _execute_set_variable_action(self, step: Dict[str, Any], 
                                         context: WorkflowContext) -> None:
        """Set a variable in the context."""
        variable = step['variable']
        value = self.parser.resolve_expression(step['value'], context.to_dict())
        
        context.set_variable(variable, value)
        logger.info(f"Set variable {variable} = {value}")
        
        return None
    
    async def _execute_log_action(self, step: Dict[str, Any], 
                                context: WorkflowContext) -> None:
        """Execute a log action."""
        message = self.parser.resolve_expression(step['message'], context.to_dict())
        level = step.get('level', 'info')
        
        log_func = getattr(logger, level, logger.info)
        log_func(message)
        
        return None
    
    async def _execute_control_flow_action(self, step: Dict[str, Any], 
                                         context: WorkflowContext) -> Dict[str, Any]:
        """Execute control flow actions (conditional, loops)."""
        if step['action'] == 'conditional':
            condition = self.parser.evaluate_condition(step['condition'], context.to_dict())
            if condition:
                await self._execute_steps(step.get('steps', []), context)
        
        elif step['action'] == 'while-loop':
            while self.parser.evaluate_condition(step['condition'], context.to_dict()):
                await self._execute_steps(step.get('steps', []), context)
        
        elif step['action'] == 'for-loop':
            items = self.parser.resolve_expression(step['items'], context.to_dict())
            if not isinstance(items, list):
                raise ValueError(f"for-loop items must be a list, got {type(items)}")
                
            for index, item in enumerate(items):
                # Set loop variables in context
                context.set_variable('item', item)
                context.set_variable('index', index)
                
                # Execute loop steps
                await self._execute_steps(step.get('steps', []), context)
        
        return {}
    
    async def _compute_outputs(self, outputs: List[Dict[str, Any]], 
                             context: WorkflowContext) -> Dict[str, Any]:
        """Compute workflow outputs."""
        result = {}
        
        for output in outputs:
            name = output['name']
            value = self.parser.resolve_expression(output['value'], context.to_dict())
            result[name] = value
            
        return result
    
    async def _execute_azure_devops_action(self, step: Dict[str, Any],
                                         context: WorkflowContext) -> Dict[str, Any]:
        """Execute Azure DevOps operations."""
        operation = step['operation']
        inputs = step.get('inputs', {})
        
        # Resolve input expressions
        resolved_inputs = {}
        for key, value in inputs.items():
            resolved_inputs[key] = self.parser.resolve_expression(value, context.to_dict())
        
        logger.info(f"Executing Azure DevOps operation: {operation}")
        logger.debug(f"Inputs: {resolved_inputs}")
        
        # Map operations to their expected outputs
        operation_outputs = {
            'create-work-item': {'work_item_id': 'WI-12345', 'url': 'https://dev.azure.com/...'},
            'update-work-item': {'success': True, 'updated_fields': []},
            'get-work-item': {'title': 'Work Item Title', 'state': 'Active', 'assigned_to': 'user@example.com'},
            'create-pr': {'pr_id': 123, 'pr_url': 'https://dev.azure.com/...'},
            'update-pr': {'success': True},
            'add-pr-comment': {'comment_id': 456},
            'get-pr': {'state': 'active', 'reviewers': []},
            'trigger-pipeline': {'run_id': 789, 'status': 'queued'},
            'check-permission': {'authorized': True},
            'create-incident': {'incident_id': 'INC-001'},
            'update-incident': {'success': True},
            'send-notification': {'sent': True},
            'page-oncall': {'paged': True},
            'get-pr-work-items': {'work_item_ids': ['WI-123', 'WI-124']},
            'add-work-item-comment': {'success': True},
            'get-work-item-relations': {'parent_ids': [], 'child_ids': []},
            'check-children-status': {'all_children_complete': True},
            'get-work-item-watchers': {'watchers': ['user1@example.com', 'user2@example.com']},
            'wait-for-deployment': {'deployment_status': 'succeeded'}
        }
        
        # Return mock outputs based on operation
        return operation_outputs.get(operation, {'status': 'success'})
    
    async def _execute_parallel_action(self, step: Dict[str, Any],
                                     context: WorkflowContext) -> Dict[str, Any]:
        """Execute steps in parallel."""
        logger.info(f"Executing {len(step.get('steps', []))} steps in parallel")
        
        # Create tasks for all parallel steps
        tasks = []
        for parallel_step in step.get('steps', []):
            task = asyncio.create_task(self._execute_step(parallel_step, context))
            tasks.append((parallel_step['id'], task))
        
        # Wait for all tasks to complete
        results = {}
        for step_id, task in tasks:
            try:
                await task
                results[step_id] = {'status': 'success'}
            except Exception as e:
                logger.error(f"Parallel step {step_id} failed: {e}")
                results[step_id] = {'status': 'failed', 'error': str(e)}
                
                # If any parallel step fails and error handling is 'fail', raise
                if step.get('onError', 'fail') == 'fail':
                    raise
        
        return results
    
    async def _execute_wait_action(self, step: Dict[str, Any],
                                 context: WorkflowContext) -> None:
        """Execute a wait/delay action."""
        duration = step.get('duration', 1)
        unit = step.get('unit', 'seconds')
        
        # Convert to seconds
        multipliers = {
            'seconds': 1,
            'minutes': 60,
            'hours': 3600
        }
        
        seconds = duration * multipliers.get(unit, 1)
        logger.info(f"Waiting for {duration} {unit} ({seconds} seconds)")
        
        # In production, we'd actually wait
        # For testing, we'll just log
        await asyncio.sleep(min(seconds, 0.1))  # Cap at 0.1s for testing
        
        return None
    
    async def _execute_git_action(self, step: Dict[str, Any], 
                                context: WorkflowContext) -> Dict[str, Any]:
        """Execute a git operation."""
        operation = step['operation']
        inputs = step.get('inputs', {})
        
        # Resolve input expressions
        resolved_inputs = {}
        for key, value in inputs.items():
            resolved_inputs[key] = self.parser.resolve_expression(value, context.to_dict())
        
        logger.info(f"Executing git operation: {operation}")
        logger.debug(f"Inputs: {resolved_inputs}")
        
        # Map operations to their expected outputs
        operation_outputs = {
            'checkout': {'branch': resolved_inputs.get('branch', 'main'), 'status': 'success'},
            'create-branch': {'branch': resolved_inputs.get('branch', 'new-branch'), 'created': True},
            'commit': {'commit_sha': 'abc123def456', 'message': resolved_inputs.get('message', '')},
            'push': {'pushed': True, 'branch': resolved_inputs.get('branch', 'main')},
            'pull': {'updated': True, 'commits': 5},
            'merge': {'merged': True, 'conflicts': False},
            'rebase': {'rebased': True, 'conflicts': False},
            'stash': {'stashed': True, 'stash_id': 'stash@{0}'},
            'tag': {'tagged': True, 'tag': resolved_inputs.get('tag_name', 'v1.0.0')},
            'clone': {'cloned': True, 'path': resolved_inputs.get('path', './repo')},
            'fetch': {'fetched': True},
            'reset': {'reset': True, 'mode': resolved_inputs.get('mode', 'hard')}
        }
        
        # Return mock outputs based on operation
        return operation_outputs.get(operation, {'status': 'success'})
    
    def get_active_executions(self) -> List[str]:
        """Get list of active execution IDs."""
        return list(self.active_executions.keys())
    
    def get_execution_context(self, execution_id: str) -> Optional[WorkflowContext]:
        """Get context for an active execution."""
        return self.active_executions.get(execution_id)