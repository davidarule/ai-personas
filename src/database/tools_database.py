"""
Tools Database for AI Personas
Manages tool categories and tools configuration in SQLite
"""

import sqlite3
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class ToolsDatabase:
    """Manages tools configuration in SQLite database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = Path(__file__).parent.parent.parent / 'database' / 'tools.db'
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Tool categories table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Tools table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category_id INTEGER NOT NULL,
                    name TEXT UNIQUE NOT NULL,
                    display_name TEXT NOT NULL,
                    description TEXT,
                    enabled BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (category_id) REFERENCES tool_categories(id) ON DELETE CASCADE
                )
            """)
            
            # Create indexes for performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tools_category ON tools(category_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tools_name ON tools(name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_tools_enabled ON tools(enabled)")
            
            # Tool configurations table (for future use)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tool_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tool_id INTEGER NOT NULL,
                    config_key TEXT NOT NULL,
                    config_value TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (tool_id) REFERENCES tools(id) ON DELETE CASCADE,
                    UNIQUE(tool_id, config_key)
                )
            """)
            
            conn.commit()
            logger.info("Tools database initialized")
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def import_from_md(self, md_content: str) -> Dict[str, int]:
        """Import tools from markdown content"""
        categories_imported = 0
        tools_imported = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Parse markdown
            categories = self._parse_md_content(md_content)
            
            for category in categories:
                # Insert or update category
                cursor.execute("""
                    INSERT OR REPLACE INTO tool_categories (name, display_name, description)
                    VALUES (?, ?, ?)
                """, (category['name'], category['display_name'], category.get('description', '')))
                
                category_id = cursor.lastrowid
                if not category_id:
                    # Get existing category id
                    cursor.execute("SELECT id FROM tool_categories WHERE name = ?", (category['name'],))
                    category_id = cursor.fetchone()['id']
                
                categories_imported += 1
                
                # Insert or update tools
                for tool in category['tools']:
                    # Check if tool exists
                    cursor.execute("SELECT id, enabled FROM tools WHERE name = ?", (tool['name'],))
                    existing = cursor.fetchone()
                    
                    if existing:
                        # Update existing tool but preserve enabled state
                        cursor.execute("""
                            UPDATE tools 
                            SET display_name = ?, description = ?, category_id = ?, updated_at = CURRENT_TIMESTAMP
                            WHERE id = ?
                        """, (tool['display_name'], tool['description'], category_id, existing['id']))
                    else:
                        # Insert new tool
                        cursor.execute("""
                            INSERT INTO tools (category_id, name, display_name, description, enabled)
                            VALUES (?, ?, ?, ?, ?)
                        """, (category_id, tool['name'], tool['display_name'], tool['description'], tool.get('enabled', False)))
                    
                    tools_imported += 1
        
        logger.info(f"Imported {categories_imported} categories and {tools_imported} tools")
        return {'categories': categories_imported, 'tools': tools_imported}
    
    def import_from_json(self, settings: Dict[str, Any]) -> Dict[str, int]:
        """Import tools from settings.json format"""
        categories_imported = 0
        tools_imported = 0
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            categories = settings.get('tools', {}).get('categories', [])
            
            for category in categories:
                # Insert or update category
                cursor.execute("""
                    INSERT OR REPLACE INTO tool_categories (name, display_name, description)
                    VALUES (?, ?, ?)
                """, (category['name'], category['displayName'], category.get('description', '')))
                
                category_id = cursor.lastrowid
                if not category_id:
                    cursor.execute("SELECT id FROM tool_categories WHERE name = ?", (category['name'],))
                    category_id = cursor.fetchone()['id']
                
                categories_imported += 1
                
                # Import tools with their enabled state
                for tool in category.get('tools', []):
                    cursor.execute("""
                        INSERT OR REPLACE INTO tools (category_id, name, display_name, description, enabled)
                        VALUES (?, ?, ?, ?, ?)
                    """, (category_id, tool['name'], tool['displayName'], tool['description'], tool.get('enabled', False)))
                    tools_imported += 1
        
        logger.info(f"Imported {categories_imported} categories and {tools_imported} tools from JSON")
        return {'categories': categories_imported, 'tools': tools_imported}
    
    def export_to_md(self) -> str:
        """Export current database state to markdown format"""
        md_content = "# Tool Categories\n\n"
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all categories
            cursor.execute("SELECT * FROM tool_categories ORDER BY display_name")
            categories = cursor.fetchall()
            
            for category in categories:
                md_content += f"### {category['display_name']}\n"
                if category['description']:
                    md_content += f"{category['description']}\n\n"
                
                # Get tools for this category
                cursor.execute("""
                    SELECT * FROM tools 
                    WHERE category_id = ? 
                    ORDER BY display_name
                """, (category['id'],))
                tools = cursor.fetchall()
                
                for tool in tools:
                    status = "[enabled]" if tool['enabled'] else "[disabled]"
                    md_content += f"- {tool['display_name']} {status}\n"
                
                md_content += "\n"
        
        return md_content
    
    def get_all_categories(self) -> List[Dict[str, Any]]:
        """Get all tool categories with tool counts"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    c.id, c.name, c.display_name, c.description,
                    COUNT(t.id) as tool_count,
                    SUM(CASE WHEN t.enabled THEN 1 ELSE 0 END) as enabled_count
                FROM tool_categories c
                LEFT JOIN tools t ON c.id = t.category_id
                GROUP BY c.id
                ORDER BY c.display_name
            """)
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_tools_by_category(self, category_name: str) -> List[Dict[str, Any]]:
        """Get all tools in a category"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT t.* 
                FROM tools t
                JOIN tool_categories c ON t.category_id = c.id
                WHERE c.name = ?
                ORDER BY t.display_name
            """, (category_name,))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def add_tool(self, category_name: str, tool_name: str, display_name: str, 
                 description: str = '', enabled: bool = False) -> bool:
        """Add a new tool to a category
        
        Args:
            category_name: Name of the category to add the tool to
            tool_name: Internal name of the tool (slug)
            display_name: Display name of the tool
            description: Tool description
            enabled: Whether the tool is enabled by default
            
        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            try:
                # Get category ID
                category = conn.execute(
                    "SELECT id FROM tool_categories WHERE name = ?",
                    (category_name,)
                ).fetchone()
                
                if not category:
                    return False
                
                # Insert the tool
                conn.execute("""
                    INSERT INTO tools (category_id, name, display_name, description, enabled)
                    VALUES (?, ?, ?, ?, ?)
                """, (category['id'], tool_name, display_name, description, enabled))
                
                return True
            except sqlite3.IntegrityError:
                # Tool already exists
                return False
            except Exception as e:
                logger.error(f"Error adding tool: {e}")
                return False
    
    def get_tool(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get a single tool by name
        
        Args:
            tool_name: Name of the tool to retrieve
            
        Returns:
            Tool dict or None if not found
        """
        with self._get_connection() as conn:
            tool = conn.execute("""
                SELECT t.name, t.display_name, t.description, t.enabled,
                       c.name as category_name
                FROM tools t
                JOIN tool_categories c ON t.category_id = c.id
                WHERE t.name = ?
            """, (tool_name,)).fetchone()
            
            if tool:
                return {
                    'name': tool['name'],
                    'display_name': tool['display_name'],
                    'description': tool['description'],
                    'enabled': bool(tool['enabled']),
                    'category': tool['category_name']
                }
            return None
    
    def update_tool(self, tool_name: str, display_name: Optional[str] = None,
                    description: Optional[str] = None, enabled: Optional[bool] = None) -> bool:
        """Update a tool's properties
        
        Args:
            tool_name: Name of the tool to update
            display_name: New display name (optional)
            description: New description (optional)
            enabled: New enabled state (optional)
            
        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            # Build dynamic update query based on provided fields
            updates = []
            params = []
            
            if display_name is not None:
                updates.append("display_name = ?")
                params.append(display_name)
            
            if description is not None:
                updates.append("description = ?")
                params.append(description)
                
            if enabled is not None:
                updates.append("enabled = ?")
                params.append(enabled)
            
            if not updates:
                return True  # Nothing to update
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(tool_name)
            
            query = f"UPDATE tools SET {', '.join(updates)} WHERE name = ?"
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            return cursor.rowcount > 0
    
    def delete_tool(self, tool_name: str) -> bool:
        """Delete a tool from the database
        
        Args:
            tool_name: Name of the tool to delete
            
        Returns:
            True if successful, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM tools WHERE name = ?", (tool_name,))
            return cursor.rowcount > 0
    
    def toggle_tool(self, tool_name: str, enabled: Optional[bool] = None) -> bool:
        """Toggle a single tool's enabled state"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if enabled is None:
                # Toggle current state
                cursor.execute("""
                    UPDATE tools 
                    SET enabled = NOT enabled, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (tool_name,))
            else:
                # Set specific state
                cursor.execute("""
                    UPDATE tools 
                    SET enabled = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (enabled, tool_name))
            
            return cursor.rowcount > 0
    
    def bulk_toggle_tools(self, tool_names: List[str], enabled: bool) -> Dict[str, Any]:
        """Toggle multiple tools atomically"""
        succeeded = []
        failed = []
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            for tool_name in tool_names:
                cursor.execute("""
                    UPDATE tools 
                    SET enabled = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE name = ?
                """, (enabled, tool_name))
                
                if cursor.rowcount > 0:
                    succeeded.append(tool_name)
                else:
                    failed.append(tool_name)
        
        return {
            'succeeded': succeeded,
            'failed': failed,
            'total': len(succeeded)
        }
    
    def toggle_category_tools(self, category_name: str, enabled: bool) -> Dict[str, Any]:
        """Toggle all tools in a category atomically"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all tool names in category first
            cursor.execute("""
                SELECT t.name 
                FROM tools t
                JOIN tool_categories c ON t.category_id = c.id
                WHERE c.name = ?
            """, (category_name,))
            
            tool_names = [row['name'] for row in cursor.fetchall()]
            
            # Update all tools
            cursor.execute("""
                UPDATE tools 
                SET enabled = ?, updated_at = CURRENT_TIMESTAMP
                WHERE category_id = (SELECT id FROM tool_categories WHERE name = ?)
            """, (enabled, category_name))
            
            affected = cursor.rowcount
            
            return {
                'category': category_name,
                'tools_affected': affected,
                'tool_names': tool_names,
                'enabled': enabled
            }
    
    def _parse_md_content(self, md_content: str) -> List[Dict[str, Any]]:
        """Parse markdown content into categories and tools"""
        categories = []
        current_category = None
        current_tools = []
        
        lines = md_content.split('\n')
        for line in lines:
            line = line.strip()
            
            # Check for category header (### Category Name)
            if line.startswith('### '):
                # Save previous category if exists
                if current_category:
                    categories.append({
                        'name': self._create_slug(current_category),
                        'display_name': current_category,
                        'tools': current_tools
                    })
                
                # Start new category
                current_category = line[4:].strip()
                current_tools = []
                
            # Check for tool item (- Tool Name)
            elif line.startswith('- ') and current_category:
                tool_line = line[2:].strip()
                if tool_line:
                    # Check if enabled/disabled is specified
                    enabled = False
                    if '[enabled]' in tool_line:
                        tool_line = tool_line.replace('[enabled]', '').strip()
                        enabled = True
                    elif '[disabled]' in tool_line:
                        tool_line = tool_line.replace('[disabled]', '').strip()
                        enabled = False
                    
                    tool_name = tool_line
                    current_tools.append({
                        'name': self._create_tool_slug(tool_name),
                        'display_name': tool_name,
                        'description': self._get_tool_description(tool_name),
                        'enabled': enabled
                    })
        
        # Don't forget the last category
        if current_category:
            categories.append({
                'name': self._create_slug(current_category),
                'display_name': current_category,
                'tools': current_tools
            })
        
        return categories
    
    def _create_slug(self, name: str) -> str:
        """Create a slug from category name"""
        # Remove parentheses and their contents
        name = re.sub(r'\([^)]*\)', '', name)
        # Convert to lowercase and replace spaces/special chars with underscores
        slug = re.sub(r'[^a-z0-9]+', '_', name.lower())
        # Remove leading/trailing underscores
        return slug.strip('_')
    
    def _create_tool_slug(self, name: str) -> str:
        """Create a slug from tool name"""
        # Convert to lowercase and replace spaces/special chars with hyphens
        slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
        # Remove leading/trailing hyphens
        return slug.strip('-')
    
    def _get_tool_description(self, tool_name: str) -> str:
        """Generate a basic description for the tool"""
        if 'API' in tool_name:
            return 'API management and development tool'
        elif 'Test' in tool_name or 'test' in tool_name:
            return 'Testing and quality assurance tool'
        elif 'CI' in tool_name or 'CD' in tool_name:
            return 'Continuous integration and deployment tool'
        elif 'Database' in tool_name or 'DB' in tool_name:
            return 'Database management tool'
        elif 'Cloud' in tool_name:
            return 'Cloud platform or service'
        elif 'Monitor' in tool_name:
            return 'Monitoring and observability tool'
        elif 'Security' in tool_name:
            return 'Security and compliance tool'
        else:
            return f'{tool_name} tool for development and operations'


# Singleton instance
_tools_db_instance = None

def get_tools_database() -> ToolsDatabase:
    """Get or create the tools database instance"""
    global _tools_db_instance
    if _tools_db_instance is None:
        _tools_db_instance = ToolsDatabase()
    return _tools_db_instance