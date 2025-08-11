#!/usr/bin/env python3
"""
Prompts Database Module
Handles system prompts and prompt templates with version control
"""

import sqlite3
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class PromptsDatabase:
    """Manages system prompts and prompt templates in SQLite database"""
    
    def __init__(self, db_path: str = None):
        """Initialize the prompts database
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use project root for database
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "prompts.db"
        
        self.db_path = str(db_path)
        self._init_database()
        self._initialize_system_prompt()
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # System prompt table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_prompt (
                    id INTEGER PRIMARY KEY,
                    prompt TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # System prompt history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_prompt_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    change_notes TEXT
                )
            """)
            
            # Prompt templates library
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS prompt_templates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    category TEXT NOT NULL,
                    description TEXT,
                    prompt TEXT NOT NULL,
                    tags TEXT,  -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_prompt_templates_category 
                ON prompt_templates(category)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_prompt_history_version 
                ON system_prompt_history(version)
            """)
            
            conn.commit()
            logger.info(f"Prompts database initialized at {self.db_path}")
    
    def _initialize_system_prompt(self):
        """One-time initialization of system prompt from CLAUDE.md"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if system prompt already exists
            cursor.execute("SELECT COUNT(*) FROM system_prompt")
            count = cursor.fetchone()[0]
            
            if count == 0:
                # First time - import from CLAUDE.md
                claude_md_path = os.path.expanduser("~/.claude/CLAUDE.md")
                
                try:
                    if os.path.exists(claude_md_path):
                        with open(claude_md_path, 'r') as f:
                            initial_prompt = f.read()
                        
                        # Make it provider-agnostic by removing Claude-specific references
                        initial_prompt = self._make_provider_agnostic(initial_prompt)
                        
                        # Insert as version 1
                        cursor.execute("""
                            INSERT INTO system_prompt (prompt, version, is_active)
                            VALUES (?, 1, TRUE)
                        """, (initial_prompt,))
                        
                        # Also save to history
                        cursor.execute("""
                            INSERT INTO system_prompt_history (prompt, version, created_by, change_notes)
                            VALUES (?, 1, 'system', 'Initial import from CLAUDE.md')
                        """, (initial_prompt,))
                        
                        conn.commit()
                        logger.info("System prompt initialized from CLAUDE.md")
                    else:
                        # No CLAUDE.md file - use a default prompt
                        default_prompt = self._get_default_system_prompt()
                        
                        cursor.execute("""
                            INSERT INTO system_prompt (prompt, version, is_active)
                            VALUES (?, 1, TRUE)
                        """, (default_prompt,))
                        
                        cursor.execute("""
                            INSERT INTO system_prompt_history (prompt, version, created_by, change_notes)
                            VALUES (?, 1, 'system', 'Default system prompt - no CLAUDE.md found')
                        """, (default_prompt,))
                        
                        conn.commit()
                        logger.info("System prompt initialized with default")
                        
                except Exception as e:
                    logger.error(f"Error initializing system prompt: {e}")
                    # Use default on error
                    default_prompt = self._get_default_system_prompt()
                    
                    cursor.execute("""
                        INSERT INTO system_prompt (prompt, version, is_active)
                        VALUES (?, 1, TRUE)
                    """, (default_prompt,))
                    
                    cursor.execute("""
                        INSERT INTO system_prompt_history (prompt, version, created_by, change_notes)
                        VALUES (?, 1, 'system', f'Default system prompt - error reading CLAUDE.md: {str(e)}')
                    """, (default_prompt,))
                    
                    conn.commit()
    
    def _make_provider_agnostic(self, prompt: str) -> str:
        """Remove provider-specific references from prompt"""
        # Replace Claude-specific terms with generic ones
        replacements = {
            "Claude": "AI Assistant",
            "Anthropic": "AI Provider",
            "claude.md": "system_prompt.md",
            "Claude Code": "AI System"
        }
        
        for old, new in replacements.items():
            prompt = prompt.replace(old, new)
        
        return prompt
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt if CLAUDE.md is not available"""
        return """# AI Assistant Engineering Standards and Configuration

## Core Identity and Purpose
You are a **Senior Principal Engineer** with 15 years of experience who writes production-ready code with no shortcuts.

## Engineering Principles

### The Three Laws of Implementation
1. **First Law**: If you cannot implement it properly, you MUST ask for help
2. **Second Law**: A working mock is not working software  
3. **Third Law**: Every piece of code is production code

### ALWAYS Behaviors (Required Standards)
- Write self-documenting code with clear variable names
- Document design decisions in comments - explain WHY not WHAT
- Handle errors gracefully with proper error messages
- Consider edge cases and validate inputs
- Test with real data in real scenarios
- Follow the task sequence: Understand → Design → Implement → Test → Document → Verify
- Request user verification: "I've implemented [task]. Please verify it meets your requirements."

### NEVER Behaviors (Automatic Failure)
- Use mock, stub, placeholder, temporary, or "TODO: implement later"
- Claim something works without testing it
- Claim a task is completed - always ask user to verify
- Move to next task until current is tested, documented, and verified
- Implement workarounds without explicit permission
- Hide errors, warnings, or uncertainties
- Copy-paste code without understanding every line
- Assume user requirements - ask for clarification
- Skip error handling, logging, or edge cases

## Communication Standards

### Task Verification (Never claim completion)
I've implemented [specific task]. Here's what I did and why:
- [Design decision 1] because [reasoning]
- [Design decision 2] because [reasoning]

Tested with [test cases] and handled [edge cases].

Please verify this meets your requirements.

### Requesting Help
I need your help with [specific issue]. 
The problem is [clear description]. 
I've considered [approaches tried], but encountering [specific blocker].
What would you recommend?

## Quality Gates Checklist

Before requesting verification of ANY task:
- [ ] Handles all edge cases
- [ ] Comprehensive error handling  
- [ ] New developer would understand in 30 seconds
- [ ] Documented WHY this approach chosen
- [ ] Tested with real-world data
- [ ] Committed with meaningful message

## The Golden Rules

1. **"Real or Nothing"** - No mocks, only production code
2. **"Ask, Don't Assume"** - When in doubt, always ask
3. **"Test, Don't Hope"** - Hope is not a strategy
4. **"Document the WHY"** - Code shows what, comments explain why
5. **"You Verify, Not Me"** - Only user determines completion
6. **"One Thing Well"** - Complete one task before starting another
7. **"Commit Like It's History"** - Because it is

---
*Every line of code is a reflection of professional standards. Make it count.*
"""
    
    # System Prompt Operations
    
    def get_system_prompt(self) -> Dict[str, Any]:
        """Get the current active system prompt"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, prompt, created_at, updated_at, version
                FROM system_prompt
                WHERE is_active = TRUE
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row['id'],
                    'prompt': row['prompt'],
                    'created_at': row['created_at'],
                    'updated_at': row['updated_at'],
                    'version': row['version']
                }
            return None
    
    def update_system_prompt(self, prompt: str, created_by: str = 'user', 
                           change_notes: str = None) -> Dict[str, Any]:
        """Update system prompt, creating a new version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current version
            cursor.execute("SELECT MAX(version) FROM system_prompt")
            current_version = cursor.fetchone()[0] or 0
            new_version = current_version + 1
            
            # Deactivate current prompt
            cursor.execute("UPDATE system_prompt SET is_active = FALSE WHERE is_active = TRUE")
            
            # Insert new prompt
            cursor.execute("""
                INSERT INTO system_prompt (prompt, version, is_active)
                VALUES (?, ?, TRUE)
            """, (prompt, new_version))
            
            prompt_id = cursor.lastrowid
            
            # Add to history
            cursor.execute("""
                INSERT INTO system_prompt_history (prompt, version, created_by, change_notes)
                VALUES (?, ?, ?, ?)
            """, (prompt, new_version, created_by, change_notes))
            
            conn.commit()
            
            return {
                'id': prompt_id,
                'version': new_version,
                'message': f'System prompt updated to version {new_version}'
            }
    
    def get_prompt_history(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get system prompt version history"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, version, created_at, created_by, change_notes,
                       LENGTH(prompt) as prompt_length
                FROM system_prompt_history
                ORDER BY version DESC
                LIMIT ?
            """, (limit,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_prompt_version(self, version: int) -> Optional[Dict[str, Any]]:
        """Get a specific version of the system prompt"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT prompt, version, created_at, created_by, change_notes
                FROM system_prompt_history
                WHERE version = ?
            """, (version,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    
    def revert_to_version(self, version: int, created_by: str = 'user') -> Dict[str, Any]:
        """Revert system prompt to a specific version"""
        # Get the old version
        old_version = self.get_prompt_version(version)
        if not old_version:
            raise ValueError(f"Version {version} not found")
        
        # Create new version with old content
        change_notes = f"Reverted to version {version}"
        return self.update_system_prompt(
            old_version['prompt'], 
            created_by, 
            change_notes
        )
    
    # Prompt Template Operations
    
    def create_template(self, title: str, category: str, prompt: str,
                       description: str = None, tags: List[str] = None) -> int:
        """Create a new prompt template"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            tags_json = json.dumps(tags) if tags else '[]'
            
            cursor.execute("""
                INSERT INTO prompt_templates (title, category, description, prompt, tags)
                VALUES (?, ?, ?, ?, ?)
            """, (title, category, description, prompt, tags_json))
            
            template_id = cursor.lastrowid
            conn.commit()
            
            return template_id
    
    def get_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """Get all templates, optionally filtered by category"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if category:
                cursor.execute("""
                    SELECT id, title, category, description, prompt, tags,
                           created_at, updated_at
                    FROM prompt_templates
                    WHERE category = ?
                    ORDER BY title
                """, (category,))
            else:
                cursor.execute("""
                    SELECT id, title, category, description, prompt, tags,
                           created_at, updated_at
                    FROM prompt_templates
                    ORDER BY category, title
                """)
            
            templates = []
            for row in cursor.fetchall():
                template = dict(row)
                template['tags'] = json.loads(template['tags'])
                templates.append(template)
            
            return templates
    
    def get_template(self, template_id: int) -> Optional[Dict[str, Any]]:
        """Get a specific template"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, title, category, description, prompt, tags,
                       created_at, updated_at
                FROM prompt_templates
                WHERE id = ?
            """, (template_id,))
            
            row = cursor.fetchone()
            if row:
                template = dict(row)
                template['tags'] = json.loads(template['tags'])
                return template
            return None
    
    def update_template(self, template_id: int, **kwargs) -> bool:
        """Update a template"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build update query dynamically
            updates = []
            values = []
            
            for field in ['title', 'category', 'description', 'prompt']:
                if field in kwargs:
                    updates.append(f"{field} = ?")
                    values.append(kwargs[field])
            
            if 'tags' in kwargs:
                updates.append("tags = ?")
                values.append(json.dumps(kwargs['tags']))
            
            if not updates:
                return False
            
            # Add updated_at
            updates.append("updated_at = CURRENT_TIMESTAMP")
            
            # Add template_id for WHERE clause
            values.append(template_id)
            
            query = f"""
                UPDATE prompt_templates
                SET {', '.join(updates)}
                WHERE id = ?
            """
            
            cursor.execute(query, values)
            conn.commit()
            
            return cursor.rowcount > 0
    
    def delete_template(self, template_id: int) -> bool:
        """Delete a template"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM prompt_templates WHERE id = ?", (template_id,))
            conn.commit()
            
            return cursor.rowcount > 0
    
    def get_categories(self) -> List[Dict[str, Any]]:
        """Get all template categories with counts"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT category, COUNT(*) as template_count
                FROM prompt_templates
                GROUP BY category
                ORDER BY category
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def search_templates(self, query: str) -> List[Dict[str, Any]]:
        """Search templates by title, description, or content"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Use LIKE for simple search
            search_pattern = f"%{query}%"
            
            cursor.execute("""
                SELECT id, title, category, description, prompt, tags,
                       created_at, updated_at
                FROM prompt_templates
                WHERE title LIKE ? OR description LIKE ? OR prompt LIKE ?
                ORDER BY 
                    CASE 
                        WHEN title LIKE ? THEN 1
                        WHEN description LIKE ? THEN 2
                        ELSE 3
                    END,
                    title
            """, (search_pattern, search_pattern, search_pattern,
                  search_pattern, search_pattern))
            
            templates = []
            for row in cursor.fetchall():
                template = dict(row)
                template['tags'] = json.loads(template['tags'])
                templates.append(template)
            
            return templates
    
    def import_templates(self, templates_data: List[Dict[str, Any]]) -> Dict[str, int]:
        """Import multiple templates"""
        imported = 0
        skipped = 0
        
        for template in templates_data:
            try:
                self.create_template(
                    title=template.get('title'),
                    category=template.get('category', 'general'),
                    prompt=template.get('prompt'),
                    description=template.get('description'),
                    tags=template.get('tags', [])
                )
                imported += 1
            except Exception as e:
                logger.error(f"Error importing template: {e}")
                skipped += 1
        
        return {'imported': imported, 'skipped': skipped}
    
    def export_templates(self, category: str = None) -> List[Dict[str, Any]]:
        """Export templates for backup/sharing"""
        templates = self.get_templates(category)
        
        # Remove database-specific fields
        for template in templates:
            del template['id']
            del template['created_at']
            del template['updated_at']
        
        return templates


# Singleton instance
_prompts_db = None

def get_prompts_database() -> PromptsDatabase:
    """Get the singleton prompts database instance"""
    global _prompts_db
    if _prompts_db is None:
        _prompts_db = PromptsDatabase()
    return _prompts_db