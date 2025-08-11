#!/usr/bin/env python3
"""
Workflow Categories Database Module
Handles workflow category management with full CRUD operations
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class WorkflowCategoriesDatabase:
    """Manages workflow categories in SQLite database"""
    
    def __init__(self, db_path: str = None):
        """Initialize the workflow categories database
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use project root for database
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "workflow_categories.db"
        
        self.db_path = str(db_path)
        self._init_database()
        self._initialize_default_categories()
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Workflow categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_categories (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    display_order INTEGER DEFAULT 999,
                    is_system BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for ordering
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_workflow_categories_order 
                ON workflow_categories(display_order, name)
            """)
            
            conn.commit()
            logger.info(f"Workflow categories database initialized at {self.db_path}")
    
    def _initialize_default_categories(self):
        """Initialize default system categories if they don't exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if we have any categories
            cursor.execute("SELECT COUNT(*) FROM workflow_categories")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Insert default categories
                default_categories = [
                    {
                        'id': 'master',
                        'name': 'Master (Orchestration)',
                        'description': 'High-level orchestration workflows that coordinate other workflows',
                        'display_order': 1,
                        'is_system': True
                    },
                    {
                        'id': 'core',
                        'name': 'Core (Primary Tasks)',
                        'description': 'Core business logic and primary task workflows',
                        'display_order': 2,
                        'is_system': True
                    },
                    {
                        'id': 'support',
                        'name': 'Support (Utility)',
                        'description': 'Supporting and utility workflows for specific tasks',
                        'display_order': 3,
                        'is_system': True
                    }
                ]
                
                for category in default_categories:
                    cursor.execute("""
                        INSERT INTO workflow_categories 
                        (id, name, description, display_order, is_system)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        category['id'],
                        category['name'],
                        category['description'],
                        category['display_order'],
                        category['is_system']
                    ))
                
                conn.commit()
                logger.info("Default workflow categories initialized")
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all workflow categories ordered by display_order"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, display_order, is_system,
                       created_at, updated_at
                FROM workflow_categories
                ORDER BY display_order, name
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_category(self, category_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific category by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, description, display_order, is_system,
                       created_at, updated_at
                FROM workflow_categories
                WHERE id = ?
            """, (category_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def create_category(self, category_id: str, name: str, 
                       description: str = None) -> Dict[str, Any]:
        """Create a new workflow category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if ID already exists
            cursor.execute("SELECT id FROM workflow_categories WHERE id = ?", (category_id,))
            if cursor.fetchone():
                raise ValueError(f"Category with ID '{category_id}' already exists")
            
            # Get next display order
            cursor.execute("SELECT MAX(display_order) FROM workflow_categories")
            max_order = cursor.fetchone()[0] or 0
            display_order = max_order + 1
            
            # Insert new category
            cursor.execute("""
                INSERT INTO workflow_categories 
                (id, name, description, display_order, is_system)
                VALUES (?, ?, ?, ?, FALSE)
            """, (category_id, name, description, display_order))
            
            conn.commit()
            
            return {
                'id': category_id,
                'name': name,
                'description': description,
                'display_order': display_order,
                'is_system': False,
                'message': f'Category "{name}" created successfully'
            }
    
    def update_category(self, category_id: str, **kwargs) -> Dict[str, Any]:
        """Update an existing category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if category exists
            cursor.execute("SELECT is_system FROM workflow_categories WHERE id = ?", (category_id,))
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Category '{category_id}' not found")
            
            # Don't allow updating system categories
            if row[0]:  # is_system is True
                raise ValueError("System categories cannot be modified")
            
            # Build update query
            updates = []
            values = []
            
            for field in ['name', 'description', 'display_order']:
                if field in kwargs:
                    updates.append(f"{field} = ?")
                    values.append(kwargs[field])
            
            if not updates:
                return {'message': 'No updates provided'}
            
            # Add updated_at
            updates.append("updated_at = CURRENT_TIMESTAMP")
            
            # Add category_id for WHERE clause
            values.append(category_id)
            
            query = f"""
                UPDATE workflow_categories
                SET {', '.join(updates)}
                WHERE id = ?
            """
            
            cursor.execute(query, values)
            conn.commit()
            
            return {
                'id': category_id,
                'message': f'Category "{category_id}" updated successfully'
            }
    
    def delete_category(self, category_id: str) -> Dict[str, Any]:
        """Delete a category"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if category exists and is not a system category
            cursor.execute("""
                SELECT name, is_system 
                FROM workflow_categories 
                WHERE id = ?
            """, (category_id,))
            
            row = cursor.fetchone()
            if not row:
                raise ValueError(f"Category '{category_id}' not found")
            
            name, is_system = row
            if is_system:
                raise ValueError("System categories cannot be deleted")
            
            # Delete the category
            cursor.execute("DELETE FROM workflow_categories WHERE id = ?", (category_id,))
            conn.commit()
            
            return {
                'id': category_id,
                'name': name,
                'message': f'Category "{name}" deleted successfully'
            }
    
    def reorder_categories(self, category_order: List[str]) -> Dict[str, Any]:
        """Update the display order of categories"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Update each category's display order
            for index, category_id in enumerate(category_order):
                cursor.execute("""
                    UPDATE workflow_categories
                    SET display_order = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (index + 1, category_id))
            
            conn.commit()
            
            return {
                'message': 'Category order updated successfully',
                'updated_count': len(category_order)
            }


# Singleton instance
_workflow_categories_db = None

def get_workflow_categories_database() -> WorkflowCategoriesDatabase:
    """Get the singleton workflow categories database instance"""
    global _workflow_categories_db
    if _workflow_categories_db is None:
        _workflow_categories_db = WorkflowCategoriesDatabase()
    return _workflow_categories_db