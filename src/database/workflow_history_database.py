"""
Workflow History Database for AI Personas
Manages workflow version history in SQLite
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class WorkflowHistoryDatabase:
    """Manages workflow version history in SQLite database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / 'database' / 'workflow_history.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Workflow history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    yaml_content TEXT NOT NULL,
                    change_notes TEXT,
                    created_by TEXT DEFAULT 'system',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(workflow_id, version)
                )
            """)
            
            # Create indexes
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_workflow_id ON workflow_history(workflow_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_version ON workflow_history(version)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON workflow_history(created_at)")
            
            conn.commit()
            logger.info("Workflow history database initialized")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def add_workflow_version(self, workflow_id: str, yaml_content: str, 
                           change_notes: str = None, created_by: str = 'system') -> int:
        """Add a new version of a workflow
        
        Args:
            workflow_id: Unique workflow identifier
            yaml_content: YAML content of the workflow
            change_notes: Optional notes about what changed
            created_by: User/system that created this version
            
        Returns:
            Version number of the saved workflow
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get the next version number
            cursor.execute("""
                SELECT MAX(version) as max_version 
                FROM workflow_history 
                WHERE workflow_id = ?
            """, (workflow_id,))
            
            result = cursor.fetchone()
            next_version = 1 if not result['max_version'] else result['max_version'] + 1
            
            # Insert new version
            cursor.execute("""
                INSERT INTO workflow_history 
                (workflow_id, version, yaml_content, change_notes, created_by)
                VALUES (?, ?, ?, ?, ?)
            """, (workflow_id, next_version, yaml_content, change_notes, created_by))
            
            conn.commit()
            logger.info(f"Added version {next_version} for workflow {workflow_id}")
            return next_version
    
    def get_workflow_history(self, workflow_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get version history for a workflow
        
        Args:
            workflow_id: Workflow to get history for
            limit: Maximum number of versions to return
            
        Returns:
            List of version records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM workflow_history
                WHERE workflow_id = ?
                ORDER BY version DESC
                LIMIT ?
            """, (workflow_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_workflow_version(self, workflow_id: str, version: int) -> Optional[Dict[str, Any]]:
        """Get a specific version of a workflow
        
        Args:
            workflow_id: Workflow identifier
            version: Version number to retrieve
            
        Returns:
            Workflow record or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM workflow_history
                WHERE workflow_id = ? AND version = ?
            """, (workflow_id, version))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_latest_version(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest version of a workflow
        
        Args:
            workflow_id: Workflow identifier
            
        Returns:
            Latest workflow record or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM workflow_history
                WHERE workflow_id = ?
                ORDER BY version DESC
                LIMIT 1
            """, (workflow_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def delete_workflow_history(self, workflow_id: str) -> int:
        """Delete all history for a workflow
        
        Args:
            workflow_id: Workflow to delete history for
            
        Returns:
            Number of records deleted
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM workflow_history
                WHERE workflow_id = ?
            """, (workflow_id,))
            
            deleted = cursor.rowcount
            conn.commit()
            logger.info(f"Deleted {deleted} history records for workflow {workflow_id}")
            return deleted
    
    def get_all_workflows(self) -> List[str]:
        """Get list of all workflows that have history
        
        Returns:
            List of workflow IDs
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT DISTINCT workflow_id 
                FROM workflow_history
                ORDER BY workflow_id
            """)
            
            return [row['workflow_id'] for row in cursor.fetchall()]


# Singleton instance
_workflow_history_db_instance = None

def get_workflow_history_database() -> WorkflowHistoryDatabase:
    """Get or create the workflow history database instance"""
    global _workflow_history_db_instance
    if _workflow_history_db_instance is None:
        _workflow_history_db_instance = WorkflowHistoryDatabase()
    return _workflow_history_db_instance