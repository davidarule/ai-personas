#!/usr/bin/env python3
"""
Import tools from tool-categories.md into settings_extended.json
All imported tools will be disabled by default as requested.
"""

import json
import re
from pathlib import Path


def parse_md_file(md_path):
    """Parse the tool-categories.md file and extract categories and tools."""
    categories = []
    current_category = None
    current_tools = []
    
    with open(md_path, 'r') as f:
        lines = f.readlines()
    
    for line in lines:
        line = line.strip()
        
        # Check for category header (### Category Name)
        if line.startswith('### '):
            # Save previous category if exists
            if current_category:
                categories.append({
                    'name': create_slug(current_category),
                    'displayName': current_category,
                    'tools': current_tools
                })
            
            # Start new category
            current_category = line[4:].strip()
            current_tools = []
            
        # Check for tool item (- Tool Name)
        elif line.startswith('- ') and current_category:
            tool_name = line[2:].strip()
            if tool_name:  # Ignore empty lines
                current_tools.append({
                    'name': create_tool_slug(tool_name),
                    'displayName': tool_name,
                    'description': get_tool_description(tool_name),
                    'enabled': False  # All tools disabled by default
                })
    
    # Don't forget the last category
    if current_category:
        categories.append({
            'name': create_slug(current_category),
            'displayName': current_category,
            'tools': current_tools
        })
    
    return categories


def create_slug(name):
    """Create a slug from category name."""
    # Remove parentheses and their contents
    name = re.sub(r'\([^)]*\)', '', name)
    # Convert to lowercase and replace spaces/special chars with underscores
    slug = re.sub(r'[^a-z0-9]+', '_', name.lower())
    # Remove leading/trailing underscores
    slug = slug.strip('_')
    return slug


def create_tool_slug(name):
    """Create a slug from tool name."""
    # Handle special cases
    name = name.replace('/', '_')
    name = name.replace('.', '_')
    # Convert to lowercase and replace spaces/special chars with hyphens
    slug = re.sub(r'[^a-z0-9]+', '-', name.lower())
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    return slug


def get_tool_description(tool_name):
    """Generate a basic description for the tool."""
    # Simple descriptions based on tool name patterns
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


def update_settings_file(categories):
    """Update the settings_extended.json file with new tools."""
    settings_path = Path('/opt/ai-personas/settings_extended.json')
    
    # Load existing settings
    with open(settings_path, 'r') as f:
        settings = json.load(f)
    
    # Replace tools section with new categories
    settings['tools'] = {
        'categories': categories
    }
    
    # Save updated settings
    with open(settings_path, 'w') as f:
        json.dump(settings, f, indent=2)
    
    return len(categories), sum(len(cat['tools']) for cat in categories)


def main():
    """Main function to import tools."""
    md_path = Path('/opt/ai-personas/src/workflows/definitions/personas/tool-categories.md')
    
    print("Parsing tool-categories.md...")
    categories = parse_md_file(md_path)
    
    print(f"Found {len(categories)} categories")
    
    # Print summary
    total_tools = sum(len(cat['tools']) for cat in categories)
    print(f"Total tools: {total_tools}")
    
    # Show first few categories as preview
    print("\nPreview of categories:")
    for cat in categories[:5]:
        print(f"  - {cat['displayName']} ({cat['name']}): {len(cat['tools'])} tools")
    print("  ...")
    
    # Update settings file
    print("\nUpdating settings_extended.json...")
    num_cats, num_tools = update_settings_file(categories)
    
    print(f"\nSuccessfully imported {num_cats} categories with {num_tools} tools!")
    print("All tools have been set to disabled by default.")


if __name__ == '__main__':
    main()