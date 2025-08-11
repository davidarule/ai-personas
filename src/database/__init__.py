"""
Database module for AI Personas
"""

from .log_database import LogDatabase, get_log_database
from .tools_database import ToolsDatabase, get_tools_database
from .prompts_database import PromptsDatabase, get_prompts_database
from .workflows_database import WorkflowsDatabase, get_workflows_database
from .workflow_categories_database import WorkflowCategoriesDatabase, get_workflow_categories_database
from .workflow_diagrams_database import WorkflowDiagramsDatabase, get_workflow_diagrams_database
from .workflow_history_database import WorkflowHistoryDatabase, get_workflow_history_database
from .repository_database import RepositoryDatabase

# Create singleton instances
_repository_db = None

def get_repository_database():
    """Get singleton instance of RepositoryDatabase"""
    global _repository_db
    if _repository_db is None:
        _repository_db = RepositoryDatabase()
    return _repository_db

__all__ = ['LogDatabase', 'get_log_database', 'ToolsDatabase', 'get_tools_database', 
           'PromptsDatabase', 'get_prompts_database', 'WorkflowsDatabase', 'get_workflows_database',
           'WorkflowCategoriesDatabase', 'get_workflow_categories_database',
           'WorkflowDiagramsDatabase', 'get_workflow_diagrams_database',
           'WorkflowHistoryDatabase', 'get_workflow_history_database',
           'RepositoryDatabase', 'get_repository_database']