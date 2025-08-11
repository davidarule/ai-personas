#!/usr/bin/env python3
"""
One-time migration script to import tools from settings_extended.json to database
"""

import json
import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_tools_database


def migrate_tools():
    """Migrate tools from settings_extended.json to database"""
    tools_db = get_tools_database()
    
    # Check if tools already exist in database
    categories = tools_db.get_all_categories()
    if categories:
        print(f"Database already contains {len(categories)} categories. Skipping migration.")
        return
    
    # Load settings file
    settings_path = Path(__file__).parent.parent.parent / 'settings_extended.json'
    if not settings_path.exists():
        print("No settings_extended.json found. Nothing to migrate.")
        return
    
    print(f"Loading tools from {settings_path}")
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    # Import tools
    result = tools_db.import_from_json(settings)
    print(f"Migrated {result['categories']} categories and {result['tools']} tools to database")
    
    # Optionally remove tools section from settings file
    # tools_section = settings.pop('tools', None)
    # if tools_section:
    #     with open(settings_path, 'w') as f:
    #         json.dump(settings, f, indent=2)
    #     print("Removed tools section from settings_extended.json")


if __name__ == '__main__':
    migrate_tools()