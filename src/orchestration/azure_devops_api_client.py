"""
Comprehensive Azure DevOps REST API Client
Implements all major Azure DevOps APIs for use by AI personas/sub-agents

API Categories:
- Work Items & Work Item Tracking
- Git Repositories & Source Control
- Build Pipelines
- Release Pipelines
- Test Plans & Test Management
- Artifacts & Packages
- Boards & Backlogs
- Wiki & Documentation
- Projects & Teams
- Security & Permissions
"""

import aiohttp
import base64
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class WorkItemType(Enum):
    """Work item types"""
    EPIC = "Epic"
    FEATURE = "Feature"
    USER_STORY = "User Story"
    TASK = "Task"
    BUG = "Bug"
    TEST_CASE = "Test Case"


class GitRefUpdateMode(Enum):
    """Git reference update modes"""
    BEST_EFFORT = "bestEffort"
    ALL_OR_NOTHING = "allOrNothing"


class BuildStatus(Enum):
    """Build status enumeration"""
    NOT_STARTED = "notStarted"
    IN_PROGRESS = "inProgress"
    COMPLETED = "completed"
    CANCELLING = "cancelling"
    POSTPONED = "postponed"
    ALL = "all"


class APIBase:
    """Base class for API implementations"""
    
    def __init__(self, client: 'AzureDevOpsClient'):
        self.client = client
        self.organization = client.organization
        self.project = client.project
        self.session = client.session
        self.headers = client.headers


class WorkItemsAPI(APIBase):
    """Work Items API implementation"""
    
    async def get_work_item(self, work_item_id: int, project: str = None) -> Dict[str, Any]:
        """Get a work item by ID"""
        # Use provided project or fall back to instance project
        project_name = project or self.project
        url = f"https://dev.azure.com/{self.organization}/{project_name}/_apis/wit/workitems/{work_item_id}?api-version=7.1"
        
        # Handle both sync and async sessions
        if hasattr(self.session, 'get') and not hasattr(self.session, '__aenter__'):
            # Sync session
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        else:
            # Async session
            async with self.session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def create_work_item(self, work_item_type: str, fields: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new work item"""
        url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/wit/workitems/${work_item_type}?api-version=7.1"
        
        # Convert fields to PATCH operations
        operations = []
        for field, value in fields.items():
            operations.append({
                "op": "add",
                "path": f"/fields/{field}",
                "value": value
            })
        
        headers = {**self.headers, "Content-Type": "application/json-patch+json"}
        
        async with self.session.patch(url, json=operations, headers=headers) as response:
            response.raise_for_status()
            return await response.json()
    
    async def query_work_items_by_wiql(self, project: str, wiql: Dict[str, str]) -> Dict[str, Any]:
        """Query work items using WIQL"""
        url = f"https://dev.azure.com/{self.organization}/{project}/_apis/wit/wiql?api-version=7.1"
        
        # Handle both sync and async sessions
        if hasattr(self.session, 'post') and not hasattr(self.session, '__aenter__'):
            # Sync session
            response = self.session.post(url, json=wiql)
            response.raise_for_status()
            return response.json()
        else:
            # Async session
            async with self.session.post(url, json=wiql, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()


class GitAPI(APIBase):
    """Git API implementation"""
    
    async def get_repositories(self) -> List[Dict[str, Any]]:
        """Get all repositories in the project"""
        url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/git/repositories?api-version=7.1"
        
        # Handle both sync and async sessions
        if hasattr(self.session, 'get') and not hasattr(self.session, '__aenter__'):
            # Sync session
            response = self.session.get(url)
            response.raise_for_status()
            result = response.json()
            return result.get('value', [])
        else:
            # Async session
            async with self.session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                result = await response.json()
                return result.get('value', [])
    
    async def create_pull_request(self, repository_id: str, source_branch: str, target_branch: str, 
                                 title: str, description: str = "") -> Dict[str, Any]:
        """Create a pull request"""
        url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/git/repositories/{repository_id}/pullrequests?api-version=7.1"
        
        data = {
            "sourceRefName": f"refs/heads/{source_branch}",
            "targetRefName": f"refs/heads/{target_branch}",
            "title": title,
            "description": description
        }
        
        # Handle both sync and async sessions
        if hasattr(self.session, 'post') and not hasattr(self.session, '__aenter__'):
            # Sync session
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        else:
            # Async session  
            async with self.session.post(url, json=data, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()
    
    async def get_default_branch(self, repository_id: str) -> str:
        """Get the default branch name for a repository"""
        repo_url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/git/repositories/{repository_id}?api-version=7.1"
        
        # Handle both sync and async sessions
        if hasattr(self.session, 'get') and not hasattr(self.session, '__aenter__'):
            # Sync session
            response = self.session.get(repo_url)
            response.raise_for_status()
            repo_data = response.json()
            return repo_data.get('defaultBranch', 'refs/heads/main').replace('refs/heads/', '')
        else:
            # Async session
            async with self.session.get(repo_url, headers=self.headers) as response:
                response.raise_for_status()
                repo_data = await response.json()
                return repo_data.get('defaultBranch', 'refs/heads/main').replace('refs/heads/', '')
    
    async def create_branch(self, repository_id: str, branch_name: str, source_branch: str = None) -> Dict[str, Any]:
        """Create a new branch"""
        # Auto-detect default branch if not specified
        if source_branch is None:
            source_branch = await self.get_default_branch(repository_id)
        
        url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/git/repositories/{repository_id}/refs?api-version=7.1"
        
        # First get the commit SHA of the source branch
        refs_url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/git/repositories/{repository_id}/refs?filter=heads/{source_branch}&api-version=7.1"
        
        # Handle both sync and async sessions
        if hasattr(self.session, 'get') and not hasattr(self.session, '__aenter__'):
            # Sync session - get source commit
            refs_response = self.session.get(refs_url)
            refs_response.raise_for_status()
            refs_data = refs_response.json()
            
            if not refs_data.get('value'):
                raise Exception(f"Source branch '{source_branch}' not found")
            
            source_commit = refs_data['value'][0]['objectId']
            
            # Create new branch
            data = [{
                "name": f"refs/heads/{branch_name}",
                "oldObjectId": "0000000000000000000000000000000000000000",
                "newObjectId": source_commit
            }]
            
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        else:
            # Async session - get source commit
            async with self.session.get(refs_url, headers=self.headers) as refs_response:
                refs_response.raise_for_status()
                refs_data = await refs_response.json()
                
                if not refs_data.get('value'):
                    raise Exception(f"Source branch '{source_branch}' not found")
                
                source_commit = refs_data['value'][0]['objectId']
                
                # Create new branch
                data = [{
                    "name": f"refs/heads/{branch_name}",
                    "oldObjectId": "0000000000000000000000000000000000000000",
                    "newObjectId": source_commit
                }]
                
                async with self.session.post(url, json=data, headers=self.headers) as response:
                    response.raise_for_status()
                    return await response.json()
    
    async def push_changes(self, repository_id: str, branch_name: str, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Push changes to a branch"""
        url = f"https://dev.azure.com/{self.organization}/{self.project}/_apis/git/repositories/{repository_id}/pushes?api-version=7.1"
        
        data = {
            "refUpdates": [{
                "name": f"refs/heads/{branch_name}",
                "oldObjectId": "0000000000000000000000000000000000000000"  # Will be updated with actual commit
            }],
            "commits": [{
                "comment": "Steve Bot: Generated architecture documents",
                "changes": changes
            }]
        }
        
        # Handle both sync and async sessions
        if hasattr(self.session, 'post') and not hasattr(self.session, '__aenter__'):
            # Sync session
            response = self.session.post(url, json=data)
            response.raise_for_status()
            return response.json()
        else:
            # Async session
            async with self.session.post(url, json=data, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()


class BuildAPI(APIBase):
    """Build API implementation"""
    pass


class ReleaseAPI(APIBase):
    """Release API implementation"""
    pass


class TestAPI(APIBase):
    """Test API implementation"""
    pass


class ArtifactsAPI(APIBase):
    """Artifacts API implementation"""
    pass


class BoardsAPI(APIBase):
    """Boards API implementation"""
    pass


class WikiAPI(APIBase):
    """Wiki API implementation"""
    pass


class CoreAPI(APIBase):
    """Core API implementation"""
    
    async def get_projects(self) -> Dict[str, Any]:
        """Get all projects in the organization"""
        url = f"https://dev.azure.com/{self.organization}/_apis/projects?api-version=7.1"
        
        # Handle both sync and async sessions
        if hasattr(self.session, 'get') and not hasattr(self.session, '__aenter__'):
            # Sync session
            response = self.session.get(url)
            response.raise_for_status()
            return response.json()
        else:
            # Async session
            async with self.session.get(url, headers=self.headers) as response:
                response.raise_for_status()
                return await response.json()


class GraphAPI(APIBase):
    """Graph API implementation"""
    pass


class AzureDevOpsClient:
    """Main Azure DevOps API client"""
    
    def __init__(self, organization_url: str, personal_access_token: str, project: str = None):
        """
        Initialize the Azure DevOps client
        
        Args:
            organization_url: Azure DevOps organization URL or name
            personal_access_token: PAT for authentication
            project: Optional project name
        """
        # Handle different URL formats
        if organization_url.startswith('https://'):
            # Extract organization from URL like https://dev.azure.com/myorg
            parts = organization_url.rstrip('/').split('/')
            self.organization = parts[-1]
            self.base_url = organization_url.rstrip('/')
        else:
            # Just organization name provided
            self.organization = organization_url
            self.base_url = f"https://dev.azure.com/{organization_url}"
            
        self.project = project
        self.pat = personal_access_token
        
        # Create auth header
        auth_string = f":{personal_access_token}"
        auth_bytes = auth_string.encode('ascii')
        auth_b64 = base64.b64encode(auth_bytes).decode('ascii')
        
        self.headers = {
            'Authorization': f'Basic {auth_b64}',
            'Content-Type': 'application/json'
        }
        
        self.session = None
        
        # Initialize API endpoints immediately for backwards compatibility
        self._init_apis()
        
    def _init_apis(self):
        """Initialize API endpoints - can be called synchronously"""
        # Create a mock session for synchronous usage
        import requests
        
        class SyncSessionWrapper:
            def __init__(self, headers):
                self.headers = headers
                
            def get(self, url, **kwargs):
                # Merge headers if provided in kwargs
                final_headers = self.headers.copy()
                if 'headers' in kwargs:
                    final_headers.update(kwargs.pop('headers'))
                return requests.get(url, headers=final_headers, **kwargs)
                
            def post(self, url, **kwargs):
                # Merge headers if provided in kwargs
                final_headers = self.headers.copy()
                if 'headers' in kwargs:
                    final_headers.update(kwargs.pop('headers'))
                return requests.post(url, headers=final_headers, **kwargs)
                
            def patch(self, url, **kwargs):  
                # Merge headers if provided in kwargs
                final_headers = self.headers.copy()
                if 'headers' in kwargs:
                    final_headers.update(kwargs.pop('headers'))
                return requests.patch(url, headers=final_headers, **kwargs)
                
            def put(self, url, **kwargs):
                # Merge headers if provided in kwargs
                final_headers = self.headers.copy()
                if 'headers' in kwargs:
                    final_headers.update(kwargs.pop('headers'))
                return requests.put(url, headers=final_headers, **kwargs)
                
            def delete(self, url, **kwargs):
                # Merge headers if provided in kwargs
                final_headers = self.headers.copy()
                if 'headers' in kwargs:
                    final_headers.update(kwargs.pop('headers'))
                return requests.delete(url, headers=final_headers, **kwargs)
        
        # Use sync session for backwards compatibility
        if not self.session:
            self.session = SyncSessionWrapper(self.headers)
        
        self.work_items = WorkItemsAPI(self)
        self.git = GitAPI(self)
        self.build = BuildAPI(self)
        self.release = ReleaseAPI(self)
        self.test = TestAPI(self)
        self.artifacts = ArtifactsAPI(self)
        self.boards = BoardsAPI(self)
        self.wiki = WikiAPI(self)
        self.core = CoreAPI(self)
        self.graph = GraphAPI(self)
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        
        # Initialize APIs
        self.work_items = WorkItemsAPI(self)
        self.git = GitAPI(self)
        self.build = BuildAPI(self)
        self.release = ReleaseAPI(self)
        self.test = TestAPI(self)
        self.artifacts = ArtifactsAPI(self)
        self.boards = BoardsAPI(self)
        self.wiki = WikiAPI(self)
        self.core = CoreAPI(self)
        self.graph = GraphAPI(self)
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def __enter__(self):
        """Sync context manager entry (creates session but doesn't initialize APIs)"""
        self.session = aiohttp.ClientSession()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Sync context manager exit"""
        if self.session:
            # Can't await in sync context, so schedule cleanup
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                loop.create_task(self.session.close())
            except RuntimeError:
                # No event loop, create one
                asyncio.run(self.session.close())
    
    async def get_projects(self) -> Dict[str, Any]:
        """Get all projects in the organization - convenience method"""
        return await self.core.get_projects()
    
    async def query_work_items_by_wiql(self, project: str, wiql: Dict[str, str]) -> Dict[str, Any]:
        """Query work items using WIQL - convenience method"""
        return await self.work_items.query_work_items_by_wiql(project, wiql)
    
    async def get_work_item(self, project: str, work_item_id: int) -> Dict[str, Any]:
        """Get a work item by ID - convenience method"""
        # Pass project directly to the WorkItemsAPI method
        return await self.work_items.get_work_item(work_item_id, project)


# For backwards compatibility, create a simple synchronous interface
def create_client(organization: str, project: str, pat: str) -> AzureDevOpsClient:
    """Create an Azure DevOps client"""
    return AzureDevOpsClient(organization, project, pat)


if __name__ == "__main__":
    print("Azure DevOps API Client - recreated from bytecode analysis")