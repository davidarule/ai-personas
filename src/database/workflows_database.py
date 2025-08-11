"""
Workflows database for storing workflow version history
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any
import threading

class WorkflowsDatabase:
    """Database for storing workflow version history"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_dir = Path(__file__).parent.parent.parent / 'data'
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / 'workflows.db')
        
        self.db_path = db_path
        self._local = threading.local()
        self._init_db()
    
    @property
    def conn(self):
        """Get thread-local database connection"""
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(self.db_path)
            self._local.conn.row_factory = sqlite3.Row
        return self._local.conn
    
    def _init_db(self):
        """Initialize database tables"""
        with self.conn:
            self.conn.execute('''
                CREATE TABLE IF NOT EXISTS workflow_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    version TEXT NOT NULL,
                    yaml_content TEXT NOT NULL,
                    change_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT DEFAULT 'system'
                )
            ''')
            
            # Create index for faster lookups
            self.conn.execute('''
                CREATE INDEX IF NOT EXISTS idx_workflow_id 
                ON workflow_history(workflow_id)
            ''')
    
    def add_version(self, workflow_id: str, version: str, yaml_content: str, 
                   change_notes: str = None, created_by: str = 'system') -> int:
        """Add a new version to workflow history"""
        with self.conn:
            cursor = self.conn.execute('''
                INSERT INTO workflow_history 
                (workflow_id, version, yaml_content, change_notes, created_by)
                VALUES (?, ?, ?, ?, ?)
            ''', (workflow_id, version, yaml_content, change_notes, created_by))
            return cursor.lastrowid
    
    def get_history(self, workflow_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get version history for a workflow"""
        cursor = self.conn.execute('''
            SELECT id, workflow_id, version, yaml_content, change_notes, 
                   created_at, created_by
            FROM workflow_history
            WHERE workflow_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (workflow_id, limit))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_version(self, workflow_id: str, version: str) -> Optional[Dict[str, Any]]:
        """Get a specific version of a workflow"""
        cursor = self.conn.execute('''
            SELECT id, workflow_id, version, yaml_content, change_notes, 
                   created_at, created_by
            FROM workflow_history
            WHERE workflow_id = ? AND version = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (workflow_id, version))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def get_latest_version(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get the latest version of a workflow"""
        cursor = self.conn.execute('''
            SELECT id, workflow_id, version, yaml_content, change_notes, 
                   created_at, created_by
            FROM workflow_history
            WHERE workflow_id = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (workflow_id,))
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def delete_old_versions(self, workflow_id: str, keep_count: int = 10):
        """Delete old versions, keeping only the most recent ones"""
        with self.conn:
            # First get the IDs to keep
            cursor = self.conn.execute('''
                SELECT id FROM workflow_history
                WHERE workflow_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (workflow_id, keep_count))
            
            ids_to_keep = [row['id'] for row in cursor.fetchall()]
            
            if ids_to_keep:
                # Delete all others
                placeholders = ','.join('?' * len(ids_to_keep))
                self.conn.execute(f'''
                    DELETE FROM workflow_history
                    WHERE workflow_id = ? AND id NOT IN ({placeholders})
                ''', [workflow_id] + ids_to_keep)

# Singleton instance
_workflows_db_instance = None

def get_workflows_database() -> WorkflowsDatabase:
    """Get singleton instance of workflows database"""
    global _workflows_db_instance
    if _workflows_db_instance is None:
        _workflows_db_instance = WorkflowsDatabase()
    return _workflows_db_instance