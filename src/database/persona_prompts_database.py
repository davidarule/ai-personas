#!/usr/bin/env python3
"""
Persona Prompts Database Module
Handles persona-specific prompts with version control and history tracking
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class PersonaPromptsDatabase:
    """Manages persona prompts with version history in SQLite database"""
    
    def __init__(self, db_path: str = None):
        """Initialize the persona prompts database
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use project root for database
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "database" / "persona_prompts.db"
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(str(self.db_path)) as conn:
            cursor = conn.cursor()
            
            # Persona prompts table - stores current prompts
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persona_prompts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_type TEXT NOT NULL UNIQUE,
                    prompt TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_by TEXT DEFAULT 'system'
                )
            """)
            
            # Persona prompt history table - stores all versions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persona_prompt_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_type TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT DEFAULT 'system',
                    change_notes TEXT,
                    UNIQUE(persona_type, version)
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_persona_prompts_type 
                ON persona_prompts(persona_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompt_history_type 
                ON persona_prompt_history(persona_type)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompt_history_version 
                ON persona_prompt_history(version)
            """)
            
            conn.commit()
            logger.info(f"Persona prompts database initialized at {self.db_path}")
    
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
    
    def save_prompt(self, persona_type: str, prompt: str, 
                   created_by: str = 'user', change_notes: str = None) -> Dict[str, Any]:
        """Save or update a persona prompt, creating version history
        
        Args:
            persona_type: Type of persona (e.g., 'security_architect')
            prompt: The prompt text
            created_by: User/system that made the change
            change_notes: Optional notes about what changed
            
        Returns:
            Dictionary with version info
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if prompt exists for this persona
            cursor.execute("""
                SELECT id, version, prompt FROM persona_prompts 
                WHERE persona_type = ?
            """, (persona_type,))
            
            existing = cursor.fetchone()
            
            if existing:
                # Update existing prompt
                current_version = existing['version']
                new_version = current_version + 1
                
                # Only create new version if prompt actually changed
                if existing['prompt'] != prompt:
                    # Update current prompt
                    cursor.execute("""
                        UPDATE persona_prompts 
                        SET prompt = ?, version = ?, updated_at = CURRENT_TIMESTAMP, 
                            updated_by = ?
                        WHERE persona_type = ?
                    """, (prompt, new_version, created_by, persona_type))
                    
                    # Add to history
                    cursor.execute("""
                        INSERT INTO persona_prompt_history 
                        (persona_type, prompt, version, created_by, change_notes)
                        VALUES (?, ?, ?, ?, ?)
                    """, (persona_type, prompt, new_version, created_by, change_notes))
                    
                    conn.commit()
                    
                    return {
                        'persona_type': persona_type,
                        'version': new_version,
                        'message': f'Prompt updated to version {new_version}'
                    }
                else:
                    return {
                        'persona_type': persona_type,
                        'version': current_version,
                        'message': 'No changes detected'
                    }
            else:
                # Create new prompt
                cursor.execute("""
                    INSERT INTO persona_prompts 
                    (persona_type, prompt, version, updated_by)
                    VALUES (?, ?, 1, ?)
                """, (persona_type, prompt, created_by))
                
                # Add first version to history
                cursor.execute("""
                    INSERT INTO persona_prompt_history 
                    (persona_type, prompt, version, created_by, change_notes)
                    VALUES (?, ?, 1, ?, ?)
                """, (persona_type, prompt, created_by, change_notes or 'Initial version'))
                
                conn.commit()
                
                return {
                    'persona_type': persona_type,
                    'version': 1,
                    'message': 'Prompt created'
                }
    
    def get_prompt(self, persona_type: str) -> Optional[Dict[str, Any]]:
        """Get the current prompt for a persona type
        
        Args:
            persona_type: Type of persona
            
        Returns:
            Dictionary with prompt info or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT persona_type, prompt, version, created_at, updated_at, updated_by
                FROM persona_prompts
                WHERE persona_type = ?
            """, (persona_type,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def get_prompt_history(self, persona_type: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get version history for a persona prompt
        
        Args:
            persona_type: Type of persona
            limit: Maximum number of versions to return
            
        Returns:
            List of version records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, persona_type, version, created_at, created_by, 
                       change_notes, LENGTH(prompt) as prompt_length
                FROM persona_prompt_history
                WHERE persona_type = ?
                ORDER BY version DESC
                LIMIT ?
            """, (persona_type, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_prompt_version(self, persona_type: str, version: int) -> Optional[Dict[str, Any]]:
        """Get a specific version of a persona prompt
        
        Args:
            persona_type: Type of persona
            version: Version number to retrieve
            
        Returns:
            Prompt record or None
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT persona_type, prompt, version, created_at, created_by, change_notes
                FROM persona_prompt_history
                WHERE persona_type = ? AND version = ?
            """, (persona_type, version))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def revert_to_version(self, persona_type: str, version: int, 
                         created_by: str = 'user') -> Dict[str, Any]:
        """Revert a persona prompt to a specific version
        
        Args:
            persona_type: Type of persona
            version: Version to revert to
            created_by: User performing the revert
            
        Returns:
            Dictionary with version info
        """
        # Get the old version
        old_version = self.get_prompt_version(persona_type, version)
        if not old_version:
            raise ValueError(f"Version {version} not found for {persona_type}")
        
        # Create new version with old content
        change_notes = f"Reverted to version {version}"
        return self.save_prompt(
            persona_type, 
            old_version['prompt'], 
            created_by, 
            change_notes
        )
    
    def get_all_persona_prompts(self) -> List[Dict[str, Any]]:
        """Get current prompts for all personas
        
        Returns:
            List of all current persona prompts
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT persona_type, prompt, version, created_at, updated_at, updated_by
                FROM persona_prompts
                ORDER BY persona_type
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def delete_prompt_history(self, persona_type: str) -> int:
        """Delete all history for a persona prompt (keeps current)
        
        Args:
            persona_type: Type of persona
            
        Returns:
            Number of history records deleted
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM persona_prompt_history
                WHERE persona_type = ?
            """, (persona_type,))
            
            deleted = cursor.rowcount
            conn.commit()
            
            logger.info(f"Deleted {deleted} history records for {persona_type}")
            return deleted
    
    def export_prompt(self, persona_type: str, include_history: bool = False) -> Dict[str, Any]:
        """Export a persona prompt with optional history
        
        Args:
            persona_type: Type of persona
            include_history: Whether to include version history
            
        Returns:
            Export data dictionary
        """
        current = self.get_prompt(persona_type)
        if not current:
            return None
        
        export_data = {
            'persona_type': current['persona_type'],
            'current_prompt': current['prompt'],
            'current_version': current['version'],
            'last_updated': current['updated_at'],
            'updated_by': current['updated_by']
        }
        
        if include_history:
            history = self.get_prompt_history(persona_type)
            export_data['history'] = history
        
        return export_data
    
    def import_prompt(self, import_data: Dict[str, Any], 
                     created_by: str = 'import') -> Dict[str, Any]:
        """Import a persona prompt from export data
        
        Args:
            import_data: Dictionary with prompt data
            created_by: User performing the import
            
        Returns:
            Import result
        """
        if 'persona_type' not in import_data or 'current_prompt' not in import_data:
            raise ValueError("Invalid import data: missing required fields")
        
        return self.save_prompt(
            import_data['persona_type'],
            import_data['current_prompt'],
            created_by,
            'Imported from external source'
        )


# Singleton instance
_persona_prompts_db = None

def get_persona_prompts_database() -> PersonaPromptsDatabase:
    """Get the singleton persona prompts database instance"""
    global _persona_prompts_db
    if _persona_prompts_db is None:
        _persona_prompts_db = PersonaPromptsDatabase()
    return _persona_prompts_db