"""
Workflow Registry Module

Central registry for discovering and managing available workflows.
"""

import logging
import json
from pathlib import Path
from typing import Dict, List, Optional, Any, Set
from datetime import datetime

from .loader import WorkflowLoader

logger = logging.getLogger(__name__)


class WorkflowRegistry:
    """Central registry for workflow discovery and management."""
    
    def __init__(self, loader: Optional[WorkflowLoader] = None):
        """
        Initialize the workflow registry.
        
        Args:
            loader: WorkflowLoader instance. Creates default if not provided.
        """
        self.loader = loader or WorkflowLoader()
        self._registry = {}
        self._metadata_cache = {}
        self._dependency_graph = {}
        self._last_scan = None
        
    def scan_workflows(self) -> None:
        """Scan the workflows directory and update the registry."""
        logger.info("Scanning for workflows...")
        
        # Load all workflows
        workflows = self.loader.load_all_workflows()
        
        # Clear existing registry
        self._registry.clear()
        self._metadata_cache.clear()
        self._dependency_graph.clear()
        
        # Build registry
        for workflow_id, workflow_data in workflows.items():
            self._register_workflow(workflow_id, workflow_data)
            
        self._last_scan = datetime.utcnow()
        
        # Build dependency graph
        self._build_dependency_graph()
        
        # Save registry index
        self._save_index()
        
        logger.info(f"Registry updated: {len(self._registry)} workflows found")
    
    def _register_workflow(self, workflow_id: str, workflow_data: Dict[str, Any]) -> None:
        """Register a single workflow."""
        metadata = workflow_data['metadata']
        
        self._registry[workflow_id] = {
            'id': workflow_id,
            'name': metadata['name'],
            'version': metadata['version'],
            'type': metadata['type'],
            'description': metadata['description'],
            'tags': metadata.get('tags', []),
            'author': metadata.get('author', 'Unknown'),
            'averageDuration': metadata.get('averageDuration', 'Unknown'),
            'inputs': [inp['name'] for inp in workflow_data.get('inputs', [])],
            'outputs': [out['name'] for out in workflow_data.get('outputs', [])]
        }
        
        # Cache full metadata
        self._metadata_cache[workflow_id] = workflow_data
    
    def _build_dependency_graph(self) -> None:
        """Build workflow dependency graph."""
        for workflow_id, workflow_data in self._metadata_cache.items():
            dependencies = set()
            
            # Find workflow dependencies
            for step in workflow_data.get('steps', []):
                if step['action'] == 'execute-workflow':
                    dependencies.add(step['workflow'])
                    
            self._dependency_graph[workflow_id] = list(dependencies)
    
    def _save_index(self) -> None:
        """Save registry index to file."""
        index_path = self.loader.workflows_dir / "index.json"
        
        index_data = {
            'last_updated': self._last_scan.isoformat(),
            'workflow_count': len(self._registry),
            'workflows': self._registry,
            'dependencies': self._dependency_graph
        }
        
        with open(index_path, 'w') as f:
            json.dump(index_data, f, indent=2)
            
        logger.info(f"Saved registry index to {index_path}")
    
    def load_index(self) -> bool:
        """
        Load registry from saved index.
        
        Returns:
            True if index loaded successfully
        """
        index_path = self.loader.workflows_dir / "index.json"
        
        if not index_path.exists():
            return False
            
        try:
            with open(index_path, 'r') as f:
                index_data = json.load(f)
                
            self._registry = index_data['workflows']
            self._dependency_graph = index_data.get('dependencies', {})
            self._last_scan = datetime.fromisoformat(index_data['last_updated'])
            
            logger.info(f"Loaded registry index: {len(self._registry)} workflows")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load registry index: {e}")
            return False
    
    def get_workflow(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a workflow definition by ID.
        
        Args:
            workflow_id: The workflow identifier
            
        Returns:
            Workflow definition or None if not found
        """
        # Ensure registry is loaded
        if not self._registry and not self.load_index():
            self.scan_workflows()
            
        if workflow_id not in self._registry:
            return None
            
        # Load full workflow if not in cache
        if workflow_id not in self._metadata_cache:
            try:
                workflow_data = self.loader.load_workflow(workflow_id)
                self._metadata_cache[workflow_id] = workflow_data
            except Exception as e:
                logger.error(f"Failed to load workflow '{workflow_id}': {e}")
                return None
                
        return self._metadata_cache[workflow_id]
    
    def list_workflows(self, workflow_type: Optional[str] = None,
                      tags: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        List available workflows with optional filtering.
        
        Args:
            workflow_type: Filter by type (master, core, support, utility)
            tags: Filter by tags
            
        Returns:
            List of workflow summaries
        """
        # Ensure registry is loaded
        if not self._registry and not self.load_index():
            self.scan_workflows()
            
        workflows = list(self._registry.values())
        
        # Apply filters
        if workflow_type:
            workflows = [w for w in workflows if w['type'] == workflow_type]
            
        if tags:
            tag_set = set(tags)
            workflows = [
                w for w in workflows 
                if tag_set.intersection(set(w.get('tags', [])))
            ]
            
        return workflows
    
    def search_workflows(self, query: str) -> List[Dict[str, Any]]:
        """
        Search workflows by name or description.
        
        Args:
            query: Search query
            
        Returns:
            List of matching workflow summaries
        """
        # Ensure registry is loaded
        if not self._registry and not self.load_index():
            self.scan_workflows()
            
        query_lower = query.lower()
        matches = []
        
        for workflow in self._registry.values():
            if (query_lower in workflow['name'].lower() or 
                query_lower in workflow['description'].lower() or
                query_lower in workflow['id'].lower() or
                any(query_lower in tag.lower() for tag in workflow.get('tags', []))):
                matches.append(workflow)
                
        return matches
    
    def get_workflow_dependencies(self, workflow_id: str, 
                                 recursive: bool = True) -> Set[str]:
        """
        Get workflow dependencies.
        
        Args:
            workflow_id: The workflow to check
            recursive: Include transitive dependencies
            
        Returns:
            Set of dependency workflow IDs
        """
        if workflow_id not in self._dependency_graph:
            return set()
            
        dependencies = set(self._dependency_graph[workflow_id])
        
        if recursive:
            # Get transitive dependencies
            to_check = list(dependencies)
            while to_check:
                dep_id = to_check.pop()
                if dep_id in self._dependency_graph:
                    for sub_dep in self._dependency_graph[dep_id]:
                        if sub_dep not in dependencies:
                            dependencies.add(sub_dep)
                            to_check.append(sub_dep)
                            
        return dependencies
    
    def get_workflow_dependents(self, workflow_id: str) -> Set[str]:
        """
        Get workflows that depend on this workflow.
        
        Args:
            workflow_id: The workflow to check
            
        Returns:
            Set of dependent workflow IDs
        """
        dependents = set()
        
        for wf_id, deps in self._dependency_graph.items():
            if workflow_id in deps:
                dependents.add(wf_id)
                
        return dependents
    
    def validate_workflow_exists(self, workflow_id: str) -> bool:
        """
        Check if a workflow exists in the registry.
        
        Args:
            workflow_id: The workflow identifier
            
        Returns:
            True if workflow exists
        """
        # Ensure registry is loaded
        if not self._registry and not self.load_index():
            self.scan_workflows()
            
        return workflow_id in self._registry
    
    def get_workflow_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Registry statistics
        """
        # Ensure registry is loaded
        if not self._registry and not self.load_index():
            self.scan_workflows()
            
        type_counts = {}
        for workflow in self._registry.values():
            wf_type = workflow['type']
            type_counts[wf_type] = type_counts.get(wf_type, 0) + 1
            
        return {
            'total_workflows': len(self._registry),
            'by_type': type_counts,
            'last_scan': self._last_scan.isoformat() if self._last_scan else None,
            'workflows_with_dependencies': len([
                wf for wf, deps in self._dependency_graph.items() if deps
            ])
        }
    
    def export_registry(self, output_path: Path) -> None:
        """
        Export the full registry to a file.
        
        Args:
            output_path: Path to export file
        """
        export_data = {
            'metadata': {
                'exported_at': datetime.utcnow().isoformat(),
                'workflow_count': len(self._registry)
            },
            'workflows': self._registry,
            'dependencies': self._dependency_graph,
            'stats': self.get_workflow_stats()
        }
        
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
            
        logger.info(f"Exported registry to {output_path}")