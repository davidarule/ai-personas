"""
Workflow Enabled Processor

Adds workflow execution capabilities to AI personas.
"""

import logging
import asyncio
from typing import Dict, List, Optional, Any
from pathlib import Path

from .base_processor import BaseProcessor
from ...workflow_engine import (
    WorkflowRegistry, 
    WorkflowExecutor, 
    WorkflowContext
)

logger = logging.getLogger(__name__)


class WorkflowEnabledProcessor(BaseProcessor):
    """Base processor with workflow execution capabilities."""
    
    def __init__(self, name: str, debug: bool = False):
        """
        Initialize workflow-enabled processor.
        
        Args:
            name: Persona name
            debug: Enable debug logging
        """
        super().__init__(name, debug)
        
        # Initialize workflow components
        self.workflow_registry = WorkflowRegistry()
        self.workflow_executor = WorkflowExecutor(self.workflow_registry)
        
        # Load available workflows
        self._load_workflows()
        
        # Track workflow executions
        self.workflow_history = []
        
    def _load_workflows(self) -> None:
        """Load and index available workflows."""
        try:
            # Try to load from index first
            if not self.workflow_registry.load_index():
                # Scan if no index exists
                self.workflow_registry.scan_workflows()
            
            stats = self.workflow_registry.get_workflow_stats()
            logger.info(
                f"{self.persona_name} loaded {stats['total_workflows']} workflows: "
                f"{stats['by_type']}"
            )
            
        except Exception as e:
            logger.error(f"Failed to load workflows: {e}")
    
    async def execute_workflow(self, workflow_id: str, 
                             inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a workflow by ID.
        
        Args:
            workflow_id: The workflow to execute
            inputs: Input parameters for the workflow
            
        Returns:
            Workflow execution results
        """
        logger.info(f"{self.persona_name} executing workflow: {workflow_id}")
        
        try:
            # Execute the workflow
            context = await self.workflow_executor.execute_workflow(workflow_id, inputs)
            
            # Store in history
            execution_summary = context.get_execution_summary()
            self.workflow_history.append(execution_summary)
            
            # Log results
            logger.info(
                f"Workflow {workflow_id} completed with status: {execution_summary['status']}"
            )
            
            return {
                'success': execution_summary['status'] == 'completed',
                'outputs': execution_summary['outputs'],
                'execution_id': execution_summary['execution_id'],
                'duration': execution_summary['duration']
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'outputs': {}
            }
    
    def discover_workflows(self, workflow_type: Optional[str] = None,
                          tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Discover available workflows.
        
        Args:
            workflow_type: Filter by type (master, core, support)
            tags: Filter by tags
            
        Returns:
            List of available workflows
        """
        return self.workflow_registry.list_workflows(workflow_type, tags)
    
    def search_workflows(self, query: str) -> List[Dict[str, Any]]:
        """
        Search for workflows by query.
        
        Args:
            query: Search query
            
        Returns:
            List of matching workflows
        """
        return self.workflow_registry.search_workflows(query)
    
    def get_workflow_details(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a workflow.
        
        Args:
            workflow_id: The workflow ID
            
        Returns:
            Workflow definition or None
        """
        return self.workflow_registry.get_workflow(workflow_id)
    
    async def process_work_item_with_workflow(self, work_item: Dict[str, Any], 
                                             workflow_id: str) -> Dict[str, Any]:
        """
        Process a work item using a specific workflow.
        
        Args:
            work_item: The work item to process
            workflow_id: The workflow to use
            
        Returns:
            Processing results
        """
        # Extract relevant inputs from work item
        inputs = self._extract_workflow_inputs(work_item, workflow_id)
        
        # Execute the workflow
        result = await self.execute_workflow(workflow_id, inputs)
        
        # Generate output based on workflow results
        if result['success']:
            output = self._generate_workflow_output(work_item, workflow_id, result)
            
            # Save the output
            output_path = self._save_output(
                f"{workflow_id}_{work_item.get('id', 'unknown')}.md",
                output,
                metadata={
                    'workflow_id': workflow_id,
                    'execution_id': result.get('execution_id'),
                    'workflow_outputs': result['outputs']
                }
            )
            
            return {
                'success': True,
                'output_path': output_path,
                'workflow_result': result
            }
        else:
            return {
                'success': False,
                'error': result.get('error', 'Unknown workflow error')
            }
    
    def _extract_workflow_inputs(self, work_item: Dict[str, Any], 
                               workflow_id: str) -> Dict[str, Any]:
        """Extract workflow inputs from work item."""
        # Get workflow definition to understand required inputs
        workflow = self.workflow_registry.get_workflow(workflow_id)
        if not workflow:
            return {}
        
        inputs = {}
        
        # Map common work item fields to workflow inputs
        input_mapping = {
            'WORK_ITEM_ID': work_item.get('id'),
            'FEATURE_ID': work_item.get('id'),
            'BUG_ID': work_item.get('id'),
            'TITLE': work_item.get('title'),
            'DESCRIPTION': work_item.get('description', '').lower().replace(' ', '-'),
            'PRIORITY': work_item.get('priority', 'medium').lower(),
            'ASSIGNED_TO': work_item.get('assignedTo'),
            'WORK_TYPE': work_item.get('type', 'feature').lower()
        }
        
        # Extract required inputs
        for input_def in workflow.get('inputs', []):
            input_name = input_def['name']
            if input_name in input_mapping and input_mapping[input_name]:
                inputs[input_name] = input_mapping[input_name]
        
        return inputs
    
    def _generate_workflow_output(self, work_item: Dict[str, Any], 
                                workflow_id: str, 
                                result: Dict[str, Any]) -> str:
        """Generate output document from workflow execution."""
        outputs = result.get('outputs', {})
        
        output = f"""# Workflow Execution Report

## Work Item
- **ID**: {work_item.get('id', 'Unknown')}
- **Title**: {work_item.get('title', 'Unknown')}
- **Type**: {work_item.get('type', 'Unknown')}

## Workflow Execution
- **Workflow**: {workflow_id}
- **Execution ID**: {result.get('execution_id', 'Unknown')}
- **Status**: {'✅ Success' if result['success'] else '❌ Failed'}
- **Duration**: {result.get('duration', 'Unknown')} seconds

## Outputs
"""
        
        for key, value in outputs.items():
            output += f"- **{key}**: {value}\n"
        
        # Add workflow-specific sections based on outputs
        if 'BRANCH_NAME' in outputs:
            output += f"\n### Created Branch\n`{outputs['BRANCH_NAME']}`\n"
        
        if 'PR_NUMBER' in outputs:
            output += f"\n### Pull Request\nPR #{outputs['PR_NUMBER']}"
            if 'PR_URL' in outputs:
                output += f" - [View PR]({outputs['PR_URL']})"
            output += "\n"
        
        if 'MERGE_COMMIT' in outputs:
            output += f"\n### Merge Commit\n`{outputs['MERGE_COMMIT']}`\n"
        
        return output
    
    def get_workflow_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get workflow execution history.
        
        Args:
            limit: Maximum number of entries to return
            
        Returns:
            List of execution summaries
        """
        history = self.workflow_history
        if limit:
            history = history[-limit:]
        return history
    
    def get_recommended_workflows(self, work_item: Dict[str, Any]) -> List[str]:
        """
        Get recommended workflows for a work item.
        
        Args:
            work_item: The work item to analyze
            
        Returns:
            List of recommended workflow IDs
        """
        recommendations = []
        work_type = work_item.get('type', '').lower()
        
        # Map work item types to workflows
        type_mapping = {
            'feature': ['wf0'],  # feature-development
            'bug': ['wf1'],      # bug-fix
            'hotfix': ['wf2'],   # hotfix
            'task': ['wf3', 'wf4'],  # branch-creation, code-commit
            'story': ['wf0'],    # feature-development
            'epic': ['wf0']      # feature-development
        }
        
        if work_type in type_mapping:
            recommendations.extend(type_mapping[work_type])
        
        # Add workflows based on keywords in title/description
        text = f"{work_item.get('title', '')} {work_item.get('description', '')}".lower()
        
        if 'conflict' in text or 'merge' in text:
            recommendations.append('wf10')  # conflict-resolution
        
        if 'rollback' in text or 'revert' in text:
            recommendations.append('wf11')  # rollback
        
        if 'pr' in text or 'pull request' in text:
            recommendations.append('wf5')  # pull-request-creation
        
        # Filter to only existing workflows
        available = [wf['id'] for wf in self.discover_workflows()]
        recommendations = [r for r in recommendations if r in available]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_recommendations = []
        for r in recommendations:
            if r not in seen:
                seen.add(r)
                unique_recommendations.append(r)
        
        return unique_recommendations