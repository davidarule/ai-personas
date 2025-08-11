#!/usr/bin/env python3
"""
Azure DevOps enabled processor for creating pull requests and managing Azure DevOps workflows
Replaces GitEnabledProcessor which was using GitHub API incorrectly
"""

import os
import json
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from .base_processor import BaseProcessor
import logging

# Import AzureDevOpsClient - fix path issue
import sys
import os
# Add the project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from orchestration.azure_devops_api_client import AzureDevOpsClient


class AzureDevOpsEnabledProcessor(BaseProcessor):
    """Base processor with Azure DevOps pull request capabilities"""
    
    def __init__(self, output_directory: str):
        super().__init__(output_directory)
        self.logger = logging.getLogger(self.__class__.__name__)
        self.azure_client = None
        self._init_azure_client()
        
    def _init_azure_client(self):
        """Initialize Azure DevOps client"""
        try:
            org = os.environ.get('AZURE_DEVOPS_ORG', 'data6')
            # Extract organization name from URL if provided
            if org.startswith('https://dev.azure.com/'):
                org = org.replace('https://dev.azure.com/', '')
            
            project = os.environ.get('AZURE_DEVOPS_PROJECT', 'AI-Pilot-Project')
            pat = os.environ.get('AZURE_DEVOPS_PAT')
            
            if pat:
                self.azure_client = AzureDevOpsClient(org, project, pat)
                self.logger.info(f"Initialized Azure DevOps client for {org}/{project}")
            else:
                self.logger.warning("AZURE_DEVOPS_PAT not set - PR creation will be disabled")
        except Exception as e:
            self.logger.error(f"Failed to initialize Azure DevOps client: {e}")
    
    async def _get_repo_config(self) -> Dict[str, str]:
        """Get Azure DevOps repository configuration"""
        return {
            'organization': os.environ.get('AZURE_DEVOPS_ORG', 'data6').replace('https://dev.azure.com/', ''),
            'project': os.environ.get('AZURE_DEVOPS_PROJECT', 'AI-Pilot-Project'),
            'repository': os.environ.get('AZURE_DEVOPS_REPO', 'AI-Personas-Repo'),
            'base_branch': 'main'
        }
    
    def _generate_branch_name(self, work_item_id: int, category: str) -> str:
        """Generate a unique branch name for the work item"""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        return f"feature/wi-{work_item_id}-{category}-{timestamp}"
    
    async def _create_azure_devops_pr(self, work_item: Any, outputs: List[Dict], 
                                      repo_config: Dict[str, str]) -> Dict[str, Any]:
        """Create a pull request in Azure DevOps"""
        if not self.azure_client:
            return {
                'status': 'error', 
                'message': 'Azure DevOps client not initialized'
            }
        
        try:
            # Generate branch name
            branch_name = self._generate_branch_name(work_item.id, self.persona_name.lower())
            
            # Get repository by name to get the ID
            repositories = await self.azure_client.git.get_repositories()
            repo_id = None
            for repo in repositories:
                if repo['name'] == repo_config['repository']:
                    repo_id = repo['id']
                    break
                    
            if not repo_id:
                return {
                    'status': 'error',
                    'message': f"Repository '{repo_config['repository']}' not found"
                }
            
            # Create branch using the existing API method
            branch_result = await self.azure_client.git.create_branch(
                repo_id, 
                branch_name, 
                f"refs/heads/{repo_config['base_branch']}"
            )
            
            if not branch_result:
                return {
                    'status': 'error',
                    'message': f"Failed to create branch '{branch_name}'"
                }
            
            # For now, we'll create a PR with a note about the files to be added
            # In a real implementation, we'd need to commit files first
            pr_title = f"[WI-{work_item.id}] {work_item.title}"
            pr_description = self._generate_pr_description(work_item, outputs)
            pr_description += "\n\n**Note:** Files need to be committed to the branch manually or through additional API calls."
            
            # Get suggested reviewers
            reviewers = self._get_suggested_reviewers(work_item, outputs)
            
            # Create pull request using the existing API method
            pr_result = await self.azure_client.git.create_pull_request(
                repo_id,
                source_branch=branch_name,
                target_branch=repo_config['base_branch'],
                title=pr_title,
                description=pr_description,
                reviewers=reviewers,
                draft=False
            )
            
            if pr_result:
                pr_url = f"https://dev.azure.com/{repo_config['organization']}/{repo_config['project']}/_git/{repo_config['repository']}/pullrequest/{pr_result['pullRequestId']}"
                
                return {
                    'status': 'success',
                    'branch': branch_name,
                    'pr_id': pr_result['pullRequestId'],
                    'pr_url': pr_url,
                    'reviewers': reviewers,
                    'message': f'Pull request created: {pr_url}'
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Failed to create pull request'
                }
                
        except Exception as e:
            self.logger.error(f"Error creating Azure DevOps PR: {e}")
            return {
                'status': 'error',
                'message': f'PR creation failed: {str(e)}'
            }
    
    # Removed methods that use non-existent API calls
    # The PR creation now uses only existing Azure DevOps API methods
    
    def _get_azure_devops_target_path(self, output: Dict) -> str:
        """Get the appropriate Azure DevOps repository path for output based on type"""
        output_type = output.get('type', 'unknown').lower()
        file_name = output.get('name', 'unnamed')
        
        # Map output types to Azure DevOps best practice locations
        if 'architecture' in output_type or 'design' in output_type:
            return f"/docs/architecture/{file_name}"
        elif 'security' in output_type:
            return f"/docs/security/{file_name}"
        elif 'test' in output_type:
            return f"/docs/testing/{file_name}"
        elif 'api' in output_type:
            return f"/docs/api/{file_name}"
        elif 'deployment' in output_type or 'devops' in output_type:
            return f"/docs/deployment/{file_name}"
        elif 'requirements' in output_type or 'specification' in output_type:
            return f"/docs/requirements/{file_name}"
        elif 'ui' in output_type or 'ux' in output_type:
            return f"/docs/design/{file_name}"
        else:
            return f"/docs/general/{file_name}"
    
    def _generate_pr_description(self, work_item: Any, outputs: List[Dict]) -> str:
        """Generate pull request description"""
        description = f"""## Work Item #{work_item.id}: {work_item.title}

**Generated by:** {self.persona_name} AI Persona
**Work Item Type:** {work_item.fields.get('System.WorkItemType', 'Unknown')}

### Description
{work_item.description or 'No description provided'}

### Outputs Generated
"""
        
        for i, output in enumerate(outputs, 1):
            description += f"\n{i}. **{output.get('type', 'Unknown')}:** {output.get('name', 'Unnamed')}"
            if output.get('description'):
                description += f"\n   - {output['description']}"
        
        description += f"""

### Azure DevOps Integration
- Files are stored in appropriate repository locations following Azure DevOps best practices
- Architecture documents: `/docs/architecture/`
- Security documents: `/docs/security/`
- Testing documents: `/docs/testing/`
- API documentation: `/docs/api/`

### Review Process
Please review the generated outputs for:
- Technical accuracy and completeness
- Alignment with project requirements
- Compliance with organizational standards
- Integration with existing documentation

**Closes:** Work Item #{work_item.id}
"""
        
        return description
    
    def _get_suggested_reviewers(self, work_item: Any, outputs: List[Dict]) -> List[str]:
        """Get suggested reviewers based on work item and output types"""
        reviewers = []
        
        # For test purposes, we'll return empty reviewers since we don't have real Azure DevOps users
        # In a real implementation, these would map to actual Azure DevOps user IDs or emails
        # 
        # Example mapping that would work with real users:
        # reviewer_map = {
        #     'security': ['user1@company.com', 'user2@company.com'],
        #     'architecture': ['architect@company.com', 'lead@company.com'],
        #     ...
        # }
        
        # Return empty list for now to avoid PR creation errors
        return []
    
    async def _update_work_item_with_pr(self, work_item_id: int, pr_info: Dict) -> bool:
        """Update work item with pull request information"""
        try:
            if not self.azure_client:
                return False
            
            # Update work item with PR link and status
            updates = [
                {
                    "op": "add",
                    "path": "/fields/System.Description",
                    "value": f"Pull Request: {pr_info.get('pr_url', 'N/A')}\n\nBranch: {pr_info.get('branch', 'N/A')}"
                },
                {
                    "op": "replace",
                    "path": "/fields/System.State",
                    "value": "Active"
                }
            ]
            
            result = await self.azure_client.work_items.update_work_item(work_item_id, updates)
            return result is not None
            
        except Exception as e:
            self.logger.error(f"Error updating work item with PR info: {e}")
            return False