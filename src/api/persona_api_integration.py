#!/usr/bin/env python3
"""
Integration layer for Persona API with aiohttp
Provides async wrappers for the Flask-based persona API
"""

import json
import logging
from datetime import datetime
from aiohttp import web
import aiohttp
import sys
import os
# Add the parent directory to the path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from personas.persona_manager import PersonaManager
from personas.processor_factory_new import ProcessorFactory
from database import get_tools_database
from database.repository_database import RepositoryDatabase
from database.workflow_history_database import get_workflow_history_database

logger = logging.getLogger(__name__)

# Create shared instances
persona_manager = PersonaManager()
processor_factory = ProcessorFactory()
tools_db = get_tools_database()
repository_db = RepositoryDatabase()
workflow_history_db = get_workflow_history_database()

# Persona Management Endpoints

async def get_persona_types(request):
    """GET /api/personas/types"""
    try:
        types = persona_manager.get_available_persona_types()
        return web.json_response({
            'status': 'success',
            'types': types,
            'count': len(types)
        })
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_persona_instances(request):
    """GET /api/personas/instances"""
    try:
        instances = []
        for instance in persona_manager.get_all_instances():
            # Get display name from registry
            config = persona_manager.registry.get(instance.persona_type)
            display_name = config.display_name if config else instance.persona_type
            
            instances.append({
                'instance_id': instance.instance_id,
                'persona_type': instance.persona_type,
                'display_name': display_name,
                'full_name': instance.full_name,
                'email': instance.email,
                'is_active': instance.is_active,
                'work_items_processed': instance.work_items_processed,
                'created_at': instance.created_at.isoformat(),
                'last_active': instance.last_activity.isoformat() if instance.last_activity else None
            })
        
        return web.json_response({
            'status': 'success',
            'instances': instances,
            'count': len(instances)
        })
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_persona_instance(request):
    """GET /api/personas/instances/{instance_id}"""
    try:
        instance_id = request.match_info['instance_id']
        instance = persona_manager.get_instance(instance_id)
        
        if not instance:
            return web.json_response({
                'status': 'error',
                'message': f'Instance not found: {instance_id}'
            }, status=404)
        
        # Get config from registry
        config = persona_manager.registry.get(instance.persona_type)
        display_name = config.display_name if config else instance.persona_type
        workflow_id = config.workflow_id if config else ''
        
        return web.json_response({
            'status': 'success',
            'instance': {
                'instance_id': instance.instance_id,
                'persona_type': instance.persona_type,
                'display_name': display_name,
                'full_name': instance.full_name,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'skills': instance.skills,
                'mcp_servers': instance.mcp_servers,
                'tools': instance.tools,
                'workflow_id': workflow_id,
                'is_active': instance.is_active,
                'metrics': persona_manager.get_instance_metrics(instance_id)
            }
        })
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def create_persona_instance(request):
    """POST /api/personas/instances"""
    try:
        data = await request.json()
        
        # Validate required fields
        if not data.get('persona_type'):
            return web.json_response({
                'status': 'error',
                'message': 'persona_type is required'
            }, status=400)
        
        # Create instance
        instance = persona_manager.create_instance(
            persona_type=data['persona_type'],
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            skills=data.get('skills'),
            mcp_servers=data.get('mcp_servers'),
            tools=data.get('tools')
        )
        
        if not instance:
            return web.json_response({
                'status': 'error',
                'message': 'Failed to create persona instance'
            }, status=500)
        
        # Also create in processor factory for processing
        processor_factory.create_persona_instance(
            persona_type=data['persona_type'],
            instance_id=instance.instance_id,
            first_name=instance.first_name,
            last_name=instance.last_name,
            email=instance.email,
            skills=instance.skills,
            mcp_servers=instance.mcp_servers,
            tools=instance.tools
        )
        
        return web.json_response({
            'status': 'success',
            'instance_id': instance.instance_id,
            'message': f'Created persona: {instance.full_name}'
        }, status=201)
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_persona_instance(request):
    """PUT /api/personas/instances/{instance_id}"""
    try:
        instance_id = request.match_info['instance_id']
        data = await request.json()
        
        # Update instance
        success = persona_manager.update_instance(
            instance_id=instance_id,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            email=data.get('email'),
            skills=data.get('skills'),
            mcp_servers=data.get('mcp_servers'),
            tools=data.get('tools')
        )
        
        if not success:
            return web.json_response({
                'status': 'error',
                'message': f'Instance not found: {instance_id}'
            }, status=404)
        
        return web.json_response({
            'status': 'success',
            'message': f'Updated persona instance: {instance_id}'
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def delete_persona_instance(request):
    """DELETE /api/personas/instances/{instance_id}"""
    try:
        instance_id = request.match_info['instance_id']
        success = persona_manager.delete_instance(instance_id)
        
        if not success:
            return web.json_response({
                'status': 'error',
                'message': f'Instance not found: {instance_id}'
            }, status=404)
        
        return web.json_response({
            'status': 'success',
            'message': f'Deleted persona instance: {instance_id}'
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def toggle_persona_instance(request):
    """POST /api/personas/instances/{instance_id}/toggle"""
    try:
        instance_id = request.match_info['instance_id']
        success = persona_manager.toggle_instance_active(instance_id)
        
        if not success:
            return web.json_response({
                'status': 'error',
                'message': f'Instance not found: {instance_id}'
            }, status=404)
        
        instance = persona_manager.get_instance(instance_id)
        return web.json_response({
            'status': 'success',
            'is_active': instance.is_active,
            'message': f'Persona {"activated" if instance.is_active else "deactivated"}'
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# MCP Server Endpoints

async def get_mcp_servers(request):
    """GET /api/mcp-servers"""
    try:
        # Load from settings_extended.json
        import json
        from pathlib import Path
        
        settings_path = Path(__file__).parent.parent.parent / 'settings_extended.json'
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)
                servers = settings.get('mcp_servers', {}).get('available', [])
        else:
            # Default MCP servers
            servers = [
                {
                    'name': 'memory',
                    'displayName': 'Memory',
                    'description': 'Knowledge graph for persistent memory',
                    'enabled': True
                },
                {
                    'name': 'filesystem',
                    'displayName': 'File System',
                    'description': 'File system operations',
                    'enabled': True
                },
                {
                    'name': 'github',
                    'displayName': 'GitHub',
                    'description': 'GitHub repository operations',
                    'enabled': True
                },
                {
                    'name': 'postgres',
                    'displayName': 'PostgreSQL',
                    'description': 'PostgreSQL database operations',
                    'enabled': True
                },
                {
                    'name': 'context7',
                    'displayName': 'Context7',
                    'description': 'Documentation retrieval',
                    'enabled': True
                },
                {
                    'name': 'serena',
                    'displayName': 'Serena',
                    'description': 'Code analysis and navigation',
                    'enabled': True
                }
            ]
        
        # Add usage count
        for server in servers:
            server['in_use_by'] = len([i for i in persona_manager.get_all_instances() 
                                      if server['name'] in i.mcp_servers])
        
        return web.json_response({
            'status': 'success',
            'servers': servers,
            'count': len(servers)
        })
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def toggle_mcp_server(request):
    """POST /api/mcp-servers/{server_name}/toggle"""
    try:
        server_name = request.match_info['server_name']
        
        # Load settings, toggle server, save
        import json
        from pathlib import Path
        
        settings_path = Path(__file__).parent.parent.parent / 'settings_extended.json'
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)
            
            # Find and toggle server
            servers = settings.get('mcp_servers', {}).get('available', [])
            for server in servers:
                if server['name'] == server_name:
                    server['enabled'] = not server.get('enabled', True)
                    break
            
            # Save settings
            with open(settings_path, 'w') as f:
                json.dump(settings, f, indent=2)
        
        return web.json_response({
            'status': 'success',
            'message': f'Toggled MCP server: {server_name}'
        })
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Tools Endpoints

async def get_tool_categories(request):
    """GET /api/tools/categories"""
    try:
        # Get categories from database
        categories = tools_db.get_all_categories()
        
        # Transform to API format
        api_categories = []
        for cat in categories:
            api_categories.append({
                'name': cat['name'],
                'displayName': cat['display_name'],
                'description': cat.get('description', ''),
                'tool_count': cat['tool_count'],
                'enabled_count': cat.get('enabled_count', 0)
            })
        
        return web.json_response({
            'status': 'success',
            'categories': api_categories,
            'count': len(api_categories)
        })
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_tools_by_category(request):
    """GET /api/tools/category/{category_name}"""
    try:
        category_name = request.match_info['category_name']
        
        # Get tools from database
        tools = tools_db.get_tools_by_category(category_name)
        
        # Transform to API format
        api_tools = []
        for tool in tools:
            api_tools.append({
                'name': tool['name'],
                'displayName': tool['display_name'],
                'description': tool['description'],
                'enabled': bool(tool['enabled'])
            })
        
        return web.json_response({
            'status': 'success',
            'category': category_name,
            'tools': api_tools,
            'count': len(api_tools)
        })
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def toggle_tool(request):
    """POST /api/tools/{tool_name}/toggle"""
    try:
        tool_name = request.match_info['tool_name']
        
        # Get optional enabled state from request body
        enabled = None
        try:
            data = await request.json()
            enabled = data.get('enabled')
        except:
            pass  # No JSON body or invalid JSON, will toggle
        
        # Toggle in database
        success = tools_db.toggle_tool(tool_name, enabled)
        
        if success:
            return web.json_response({
                'status': 'success',
                'message': f'Toggled tool: {tool_name}'
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': f'Tool not found: {tool_name}'
            }, status=404)
            
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Tool Category CRUD Operations

async def create_tool_category(request):
    """POST /api/tools/category"""
    try:
        data = await request.json()
        
        # Validate required fields
        if not data.get('displayName'):
            return web.json_response({
                'status': 'error',
                'message': 'displayName is required'
            }, status=400)
        
        # Generate name from displayName
        import re
        name = re.sub(r'[^a-z0-9]+', '_', data['displayName'].lower()).strip('_')
        
        # Load settings
        import json
        from pathlib import Path
        
        settings_path = Path(__file__).parent.parent.parent / 'settings_extended.json'
        if settings_path.exists():
            with open(settings_path, 'r') as f:
                settings = json.load(f)
        else:
            settings = {'tools': {'categories': []}}
        
        # Check if category already exists
        categories = settings.get('tools', {}).get('categories', [])
        for cat in categories:
            if cat['name'] == name:
                return web.json_response({
                    'status': 'error',
                    'message': f'Category already exists: {name}'
                }, status=400)
        
        # Create new category
        new_category = {
            'name': name,
            'displayName': data['displayName'],
            'description': data.get('description', ''),
            'tools': []
        }
        
        categories.append(new_category)
        settings.setdefault('tools', {})['categories'] = categories
        
        # Save settings
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        return web.json_response({
            'status': 'success',
            'message': f'Created category: {data["displayName"]}',
            'category': {
                'name': name,
                'displayName': new_category['displayName'],
                'description': new_category['description'],
                'tool_count': 0
            }
        }, status=201)
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_tool_category(request):
    """PUT /api/tools/category/{category_name}"""
    try:
        category_name = request.match_info['category_name']
        data = await request.json()
        
        # Load settings
        import json
        from pathlib import Path
        
        settings_path = Path(__file__).parent.parent.parent / 'settings_extended.json'
        if not settings_path.exists():
            return web.json_response({
                'status': 'error',
                'message': 'Settings file not found'
            }, status=404)
        
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        # Find and update category
        categories = settings.get('tools', {}).get('categories', [])
        found = False
        for cat in categories:
            if cat['name'] == category_name:
                if 'displayName' in data:
                    cat['displayName'] = data['displayName']
                if 'description' in data:
                    cat['description'] = data['description']
                found = True
                break
        
        if not found:
            return web.json_response({
                'status': 'error',
                'message': f'Category not found: {category_name}'
            }, status=404)
        
        # Save settings
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        return web.json_response({
            'status': 'success',
            'message': f'Updated category: {category_name}'
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def delete_tool_category(request):
    """DELETE /api/tools/category/{category_name}"""
    try:
        category_name = request.match_info['category_name']
        
        # Load settings
        import json
        from pathlib import Path
        
        settings_path = Path(__file__).parent.parent.parent / 'settings_extended.json'
        if not settings_path.exists():
            return web.json_response({
                'status': 'error',
                'message': 'Settings file not found'
            }, status=404)
        
        with open(settings_path, 'r') as f:
            settings = json.load(f)
        
        # Remove category
        categories = settings.get('tools', {}).get('categories', [])
        original_count = len(categories)
        categories = [cat for cat in categories if cat['name'] != category_name]
        
        if len(categories) == original_count:
            return web.json_response({
                'status': 'error',
                'message': f'Category not found: {category_name}'
            }, status=404)
        
        settings['tools']['categories'] = categories
        
        # Save settings
        with open(settings_path, 'w') as f:
            json.dump(settings, f, indent=2)
        
        return web.json_response({
            'status': 'success',
            'message': f'Deleted category: {category_name}'
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Individual Tool CRUD Operations

async def create_tool(request):
    """POST /api/tools"""
    try:
        data = await request.json()
        
        # Validate required fields
        if not data.get('displayName') or not data.get('category'):
            return web.json_response({
                'status': 'error',
                'message': 'displayName and category are required'
            }, status=400)
        
        # Generate name from displayName
        import re
        name = re.sub(r'[^a-z0-9]+', '-', data['displayName'].lower()).strip('-')
        
        # Check if tool already exists
        existing_tool = tools_db.get_tool(name)
        if existing_tool:
            return web.json_response({
                'status': 'error',
                'message': f'Tool already exists: {name}'
            }, status=400)
        
        # Check if category exists
        categories = tools_db.get_all_categories()
        category_exists = any(cat['name'] == data['category'] for cat in categories)
        
        if not category_exists:
            return web.json_response({
                'status': 'error',
                'message': f'Category not found: {data["category"]}'
            }, status=404)
        
        # Add new tool to database
        success = tools_db.add_tool(
            category_name=data['category'],
            tool_name=name,
            display_name=data['displayName'],
            description=data.get('description', ''),
            enabled=data.get('enabled', False)
        )
        
        if success:
            return web.json_response({
                'status': 'success',
                'message': f'Created tool: {data["displayName"]}',
                'tool': {
                    'name': name,
                    'displayName': data['displayName'],
                    'description': data.get('description', ''),
                    'enabled': data.get('enabled', False)
                }
            }, status=201)
        else:
            return web.json_response({
                'status': 'error',
                'message': 'Failed to create tool'
            }, status=500)
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_tool(request):
    """PUT /api/tools/{tool_name}"""
    try:
        tool_name = request.match_info['tool_name']
        data = await request.json()
        
        # Check if tool exists
        tool = tools_db.get_tool(tool_name)
        if not tool:
            return web.json_response({
                'status': 'error',
                'message': f'Tool not found: {tool_name}'
            }, status=404)
        
        # Update in database
        success = tools_db.update_tool(
            tool_name=tool_name,
            display_name=data.get('displayName'),
            description=data.get('description'),
            enabled=data.get('enabled')
        )
        
        if success:
            return web.json_response({
                'status': 'success',
                'message': f'Updated tool: {tool_name}'
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': f'Failed to update tool: {tool_name}'
            }, status=500)
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def delete_tool(request):
    """DELETE /api/tools/{tool_name}"""
    try:
        tool_name = request.match_info['tool_name']
        
        # Check if tool exists
        tool = tools_db.get_tool(tool_name)
        if not tool:
            return web.json_response({
                'status': 'error',
                'message': f'Tool not found: {tool_name}'
            }, status=404)
        
        # Delete from database
        success = tools_db.delete_tool(tool_name)
        
        if success:
            return web.json_response({
                'status': 'success',
                'message': f'Deleted tool: {tool_name}'
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': f'Failed to delete tool: {tool_name}'
            }, status=500)
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def import_tools_from_md(request):
    """POST /api/tools/import - Import tools from markdown content"""
    try:
        data = await request.json()
        content = data.get('content', '')
        filename = data.get('filename', 'imported.md')
        
        if not content:
            return web.json_response({
                'status': 'error',
                'message': 'No content provided'
            }, status=400)
        
        # Import to database
        result = tools_db.import_from_md(content)
        
        return web.json_response({
            'status': 'success',
            'message': f'Imported {result["categories"]} categories with {result["tools"]} tools from {filename}',
            'categoryCount': result['categories'],
            'toolCount': result['tools']
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def bulk_toggle_tools(request):
    """POST /api/tools/bulk-toggle - Toggle multiple tools atomically"""
    try:
        data = await request.json()
        tool_names = data.get('tools', [])
        enabled = data.get('enabled', True)
        
        if not tool_names:
            return web.json_response({
                'status': 'error',
                'message': 'No tools specified'
            }, status=400)
        
        # Toggle in database
        result = tools_db.bulk_toggle_tools(tool_names, enabled)
        
        return web.json_response({
            'status': 'success',
            'result': result,
            'message': f'{result["total"]} tools {"enabled" if enabled else "disabled"}'
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def toggle_category_tools(request):
    """POST /api/tools/category/{category_name}/toggle-all - Toggle all tools in a category"""
    try:
        category_name = request.match_info['category_name']
        data = await request.json()
        enabled = data.get('enabled', True)
        
        # Toggle in database
        result = tools_db.toggle_category_tools(category_name, enabled)
        
        if result['tools_affected'] > 0:
            return web.json_response({
                'status': 'success',
                'result': result,
                'message': f'{result["tools_affected"]} tools {"enabled" if enabled else "disabled"} in {category_name}'
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': f'Category not found: {category_name}'
            }, status=404)
            
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def export_tools_to_md(request):
    """GET /api/tools/export - Export current tool configuration to markdown"""
    try:
        # Export from database
        md_content = tools_db.export_to_md()
        
        return web.Response(
            text=md_content,
            content_type='text/markdown',
            headers={
                'Content-Disposition': 'attachment; filename="tools-export.md"'
            }
        )
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def create_persona_type(request):
    """POST /api/personas/types"""
    try:
        data = await request.json()
        logger.info(f"create_persona_type called with data: {data}")
        
        # Validate required fields
        if not data.get('type') or not data.get('display_name'):
            return web.json_response({
                'status': 'error',
                'message': 'type and display_name are required'
            }, status=400)
        
        # For now, let's bypass the check and just try to create
        logger.info(f"Attempting to create persona type: {data['type']}")
        
        # Create new persona type configuration
        success = persona_manager.create_persona_type(
            persona_type=data['type'],
            display_name=data['display_name']
        )
        
        if not success:
            return web.json_response({
                'status': 'error',
                'message': 'Failed to create persona type'
            }, status=500)
        
        return web.json_response({
            'status': 'success',
            'message': f'Created persona type: {data["type"]}'
        })
        
    except Exception as e:
        import traceback
        logger.error(f"Error in create_persona_type: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_persona_type(request):
    """PUT /api/personas/types/{type}"""
    try:
        persona_type = request.match_info['type']
        data = await request.json()
        
        # Update persona type configuration
        success = persona_manager.update_persona_type(
            persona_type=persona_type,
            display_name=data.get('display_name'),
            prompt=data.get('prompt'),
            external_version=data.get('external_version'),
            prompt_change_notes=data.get('prompt_change_notes'),
            prompt_last_updated=data.get('prompt_last_updated'),
            default_skills=data.get('default_skills'),
            default_tools=data.get('default_tools'),
            default_mcp_servers=data.get('default_mcp_servers'),
            category=data.get('category'),
            description=data.get('description'),
            default_first_name=data.get('default_first_name'),
            default_last_name=data.get('default_last_name'),
            default_email_domain=data.get('default_email_domain')
        )
        
        if not success:
            return web.json_response({
                'status': 'error',
                'message': f'Persona type not found: {persona_type}'
            }, status=404)
        
        return web.json_response({
            'status': 'success',
            'message': f'Updated persona type: {persona_type}'
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def delete_persona_type(request):
    """DELETE /api/personas/types/{type}"""
    try:
        persona_type = request.match_info['type']
        logger.info(f"delete_persona_type called for type: {persona_type}")
        
        # Check if persona type exists
        types = persona_manager.get_available_persona_types()
        type_exists = any(pt['type'] == persona_type for pt in types)
        
        if not type_exists:
            return web.json_response({
                'status': 'error',
                'message': f'Persona type not found: {persona_type}'
            }, status=404)
        
        # Check if there are any instances of this type
        instances = persona_manager.get_instances_by_type(persona_type)
        if instances:
            return web.json_response({
                'status': 'error',
                'message': f'Cannot delete persona type "{persona_type}" - {len(instances)} instance(s) exist. Delete all instances first.'
            }, status=400)
        
        # Delete the persona type
        success = persona_manager.delete_persona_type(persona_type)
        
        if success:
            return web.json_response({
                'status': 'success',
                'message': f'Deleted persona type: {persona_type}'
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': f'Failed to delete persona type: {persona_type}'
            }, status=500)
            
    except Exception as e:
        import traceback
        logger.error(f"Error in delete_persona_type: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_persona_type_prompt(request):
    """PUT /api/personas/types/{type}/prompt"""
    try:
        persona_type = request.match_info['type']
        data = await request.json()
        
        # Validate required fields
        if 'prompt' not in data:
            return web.json_response({
                'status': 'error',
                'message': 'Prompt is required'
            }, status=400)
        
        # Update only prompt-related fields
        success = persona_manager.update_persona_type(
            persona_type=persona_type,
            prompt=data['prompt'],
            external_version=data.get('external_version'),
            prompt_change_notes=data.get('prompt_change_notes'),
            prompt_last_updated=datetime.now().isoformat()
        )
        
        if not success:
            return web.json_response({
                'status': 'error',
                'message': f'Persona type not found: {persona_type}'
            }, status=404)
        
        return web.json_response({
            'status': 'success',
            'message': f'Updated prompt for persona type: {persona_type}',
            'version': data.get('external_version', '1.0')
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_persona_type_mcp_servers(request):
    """PUT /api/personas/types/{type}/mcp-servers"""
    try:
        persona_type = request.match_info['type']
        data = await request.json()
        
        # Validate required fields
        if 'mcp_servers' not in data:
            return web.json_response({
                'status': 'error',
                'message': 'mcp_servers array is required'
            }, status=400)
        
        # Update only MCP servers
        success = persona_manager.update_persona_type(
            persona_type=persona_type,
            default_mcp_servers=data['mcp_servers']
        )
        
        if not success:
            return web.json_response({
                'status': 'error',
                'message': f'Persona type not found: {persona_type}'
            }, status=404)
        
        return web.json_response({
            'status': 'success',
            'message': f'Updated MCP servers for persona type: {persona_type}',
            'mcp_servers': data['mcp_servers']
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def generate_persona_prompt(request):
    """POST /api/personas/types/{type}/generate-prompt"""
    try:
        persona_type = request.match_info['type']
        
        # Get persona type configuration
        types = persona_manager.get_available_persona_types()
        persona_config = None
        for pt in types:
            if pt['type'] == persona_type:
                persona_config = pt
                break
        
        if not persona_config:
            return web.json_response({
                'status': 'error',
                'message': f'Persona type not found: {persona_type}'
            }, status=404)
        
        # Generate prompt based on persona type
        prompts = {
            'devsecops-engineer': 'You are a DevSecOps Engineer specialized in security automation, CI/CD pipelines, and infrastructure as code. You ensure security is embedded throughout the development lifecycle. You work with tools like Docker, Kubernetes, Terraform, and security scanning tools. Your focus is on automating security checks, implementing secure deployment practices, and maintaining compliance.',
            'software-architect': 'You are a Software Architect responsible for designing robust, scalable systems. You create high-level architecture diagrams, define system components and their interactions, and ensure alignment with business requirements. You focus on design patterns, technology selection, and maintaining architectural integrity across the entire system.',
            'qa-test-engineer': 'You are a QA/Test Engineer focused on ensuring software quality through comprehensive testing strategies. You design test plans, implement automated tests, and perform security testing. You work with testing frameworks, CI/CD pipelines, and collaborate with developers to maintain high code quality.',
            'cloud-architect': 'You are a Cloud Architect specializing in designing and implementing cloud-native solutions. You work with AWS, Azure, or GCP to create scalable, resilient architectures. You focus on cloud migration strategies, cost optimization, security best practices, and leveraging managed services.',
            'platform-engineer': 'You are a Platform Engineer building and maintaining the infrastructure and tools that enable development teams. You create internal developer platforms, implement CI/CD pipelines, and ensure system reliability. You work with Kubernetes, service meshes, and observability tools.',
            'data-engineer': 'You are a Data Engineer responsible for building and maintaining data pipelines and infrastructure. You design ETL/ELT processes, implement data warehouses and lakes, and ensure data quality. You work with tools like Apache Spark, Airflow, and various data storage technologies.',
            'ml-engineer': 'You are a Machine Learning Engineer focused on deploying and maintaining ML models in production. You build ML pipelines, implement model monitoring, and ensure scalable inference. You work with frameworks like TensorFlow, PyTorch, and MLOps tools.',
            'security-engineer': 'You are a Security Engineer dedicated to protecting systems and data from threats. You implement security controls, perform vulnerability assessments, and respond to security incidents. You work with SIEM tools, security scanners, and develop security policies.',
            'sre-engineer': 'You are a Site Reliability Engineer ensuring system reliability and performance. You implement SLIs/SLOs, build monitoring and alerting systems, and perform incident response. You focus on automation, capacity planning, and improving system resilience.',
            'full-stack-developer': 'You are a Full Stack Developer capable of building end-to-end applications. You work with both frontend and backend technologies, design RESTful APIs, and implement responsive user interfaces. You focus on clean code, performance optimization, and user experience.',
            'backend-developer': 'You are a Backend Developer specializing in server-side application logic. You design and implement APIs, work with databases, and ensure system performance and security. You focus on scalability, data integrity, and integration with various services.',
            'frontend-developer': 'You are a Frontend Developer creating engaging user interfaces. You work with modern JavaScript frameworks, implement responsive designs, and ensure cross-browser compatibility. You focus on performance, accessibility, and user experience.',
            'mobile-developer': 'You are a Mobile Developer building native or cross-platform mobile applications. You work with iOS, Android, or frameworks like React Native and Flutter. You focus on performance optimization, offline capabilities, and platform-specific features.',
            'database-administrator': 'You are a Database Administrator managing and optimizing database systems. You design schemas, implement backup strategies, and ensure data integrity and performance. You work with various database technologies and focus on security and high availability.',
            'network-engineer': 'You are a Network Engineer designing and maintaining network infrastructure. You configure routers, switches, and firewalls, implement network security, and ensure reliable connectivity. You work with protocols, VPNs, and network monitoring tools.',
            'technical-writer': 'You are a Technical Writer creating clear, comprehensive documentation. You write API documentation, user guides, and technical specifications. You focus on clarity, accuracy, and making complex technical concepts accessible to various audiences.',
            'ui-ux-designer': 'You are a UI/UX Designer creating intuitive and visually appealing interfaces. You conduct user research, create wireframes and prototypes, and design user flows. You focus on usability, accessibility, and creating delightful user experiences.',
            'project-manager': 'You are a Project Manager coordinating technical projects and teams. You manage timelines, resources, and stakeholder communications. You use agile methodologies, track project metrics, and ensure successful project delivery.',
            'product-manager': 'You are a Product Manager defining product vision and strategy. You gather requirements, prioritize features, and work with engineering teams. You focus on user needs, market analysis, and delivering value to customers.',
            'scrum-master': 'You are a Scrum Master facilitating agile development processes. You organize sprints, remove impediments, and coach teams on agile practices. You focus on continuous improvement and helping teams deliver value efficiently.'
        }
        
        # Get the appropriate prompt or use a generic template
        prompt = prompts.get(persona_type, f'You are a {persona_config["display_name"]} with expertise in your domain. You follow best practices, write clean code, and focus on delivering high-quality solutions. You collaborate effectively with team members and maintain professional standards.')
        
        # Add skills if available
        if persona_config.get('default_skills'):
            skills_text = ', '.join(persona_config['default_skills'])
            prompt += f'\n\nYour key skills include: {skills_text}.'
        
        return web.json_response({
            'status': 'success',
            'prompt': prompt,
            'message': 'Generated prompt based on persona type'
        })
        
    except Exception as e:
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_mcp_settings(request):
    """GET /api/settings/mcp"""
    try:
        # Get MCP settings from persona manager or config
        settings = persona_manager.get_mcp_settings() if hasattr(persona_manager, 'get_mcp_settings') else {}
        
        return web.json_response({
            'status': 'success',
            'settings': settings
        })
        
    except Exception as e:
        logger.error(f"Error getting MCP settings: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_mcp_settings(request):
    """PUT /api/settings/mcp"""
    try:
        data = await request.json()
        
        # Update MCP settings
        success = persona_manager.update_mcp_settings(data) if hasattr(persona_manager, 'update_mcp_settings') else True
        
        if success:
            return web.json_response({
                'status': 'success',
                'message': 'MCP settings updated successfully'
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': 'Failed to update MCP settings'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error updating MCP settings: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_agent_settings(request):
    """GET /api/settings/agents"""
    try:
        # Get agent settings from persona manager or config
        settings = persona_manager.get_agent_settings() if hasattr(persona_manager, 'get_agent_settings') else {}
        
        return web.json_response({
            'status': 'success',
            'settings': settings
        })
        
    except Exception as e:
        logger.error(f"Error getting agent settings: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_agent_settings(request):
    """PUT /api/settings/agents"""
    try:
        data = await request.json()
        
        # Update agent settings
        success = persona_manager.update_agent_settings(data) if hasattr(persona_manager, 'update_agent_settings') else True
        
        if success:
            # Get the updated settings to return the hints
            updated_settings = persona_manager.get_agent_settings() if hasattr(persona_manager, 'get_agent_settings') else {}
            
            # Extract provider hints
            provider_hints = {}
            if 'providers' in updated_settings:
                for provider_id, config in updated_settings['providers'].items():
                    if config.get('apiKeyHint'):
                        provider_hints[provider_id] = {
                            'apiKeyHint': config['apiKeyHint']
                        }
            
            return web.json_response({
                'status': 'success',
                'message': 'Agent settings updated successfully',
                'data': {
                    'providers': provider_hints
                }
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': 'Failed to update agent settings'
            }, status=500)
            
    except Exception as e:
        logger.error(f"Error updating agent settings: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# AI Provider Test Connection Endpoints

async def test_openai_connection(request):
    """POST /api/test-connection/openai - Test OpenAI API connection"""
    try:
        data = await request.json()
        api_key = data.get('apiKey', '').strip()
        
        # Get existing key if not provided
        if not api_key:
            # Try to get from database
            try:
                api_key = persona_manager.get_provider_api_key('openai')
                logger.info(f"Retrieved API key from database: {'Yes' if api_key else 'No'}")
            except Exception as e:
                logger.error(f"Error retrieving API key: {str(e)}")
        
        if not api_key:
            logger.warning("No API key available for OpenAI test connection")
            return web.json_response({
                'status': 'error',
                'message': 'No API key available. Please enter an API key or save one first.'
            }, status=400)
        
        # Test OpenAI API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            
            # Try to list models as a simple test
            async with session.get('https://api.openai.com/v1/models', headers=headers) as resp:
                if resp.status == 200:
                    models = await resp.json()
                    return web.json_response({
                        'status': 'success',
                        'message': f'Connected successfully! Found {len(models.get("data", []))} models.',
                        'provider': 'OpenAI'
                    })
                elif resp.status == 401:
                    return web.json_response({
                        'status': 'error',
                        'message': 'Invalid API key'
                    }, status=401)
                else:
                    return web.json_response({
                        'status': 'error',
                        'message': f'API error: {resp.status}'
                    }, status=resp.status)
                    
    except Exception as e:
        logger.error(f"Error testing OpenAI connection: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def test_anthropic_connection(request):
    """POST /api/test-connection/anthropic - Test Anthropic API connection"""
    try:
        data = await request.json()
        api_key = data.get('apiKey', '').strip()
        
        # Get existing key if not provided
        if not api_key:
            try:
                api_key = persona_manager.get_provider_api_key('anthropic')
                logger.info(f"Retrieved Anthropic API key from database: {'Yes' if api_key else 'No'}")
            except Exception as e:
                logger.error(f"Error retrieving Anthropic API key: {str(e)}")
        
        if not api_key:
            logger.warning("No API key available for Anthropic test connection")
            return web.json_response({
                'status': 'error',
                'message': 'No API key available. Please enter an API key or save one first.'
            }, status=400)
        
        # Test Anthropic API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            headers = {
                'x-api-key': api_key,
                'anthropic-version': '2023-06-01',
                'Content-Type': 'application/json'
            }
            
            # Simple test - try to get account info or send minimal completion
            test_data = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": 1,
                "messages": [{"role": "user", "content": "Hi"}]
            }
            
            async with session.post('https://api.anthropic.com/v1/messages', 
                                  headers=headers, 
                                  json=test_data) as resp:
                if resp.status == 200:
                    return web.json_response({
                        'status': 'success',
                        'message': 'Connected successfully to Anthropic!',
                        'provider': 'Anthropic'
                    })
                elif resp.status == 401:
                    return web.json_response({
                        'status': 'error',
                        'message': 'Invalid API key'
                    }, status=401)
                else:
                    error_data = await resp.text()
                    return web.json_response({
                        'status': 'error',
                        'message': f'API error: {resp.status} - {error_data}'
                    }, status=resp.status)
                    
    except Exception as e:
        logger.error(f"Error testing Anthropic connection: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def test_gemini_connection(request):
    """POST /api/test-connection/gemini - Test Google Gemini API connection"""
    try:
        data = await request.json()
        api_key = data.get('apiKey', '').strip()
        
        # Get existing key if not provided
        if not api_key:
            try:
                api_key = persona_manager.get_provider_api_key('gemini')
                logger.info(f"Retrieved Gemini API key from database: {'Yes' if api_key else 'No'}")
            except Exception as e:
                logger.error(f"Error retrieving Gemini API key: {str(e)}")
        
        if not api_key:
            logger.warning("No API key available for Gemini test connection")
            return web.json_response({
                'status': 'error',
                'message': 'No API key available. Please enter an API key or save one first.'
            }, status=400)
        
        # Test Gemini API
        import aiohttp
        async with aiohttp.ClientSession() as session:
            # List models endpoint
            url = f'https://generativelanguage.googleapis.com/v1/models?key={api_key}'
            
            async with session.get(url) as resp:
                if resp.status == 200:
                    models = await resp.json()
                    return web.json_response({
                        'status': 'success',
                        'message': f'Connected successfully! Found {len(models.get("models", []))} models.',
                        'provider': 'Google Gemini'
                    })
                elif resp.status == 400 or resp.status == 403:
                    return web.json_response({
                        'status': 'error',
                        'message': 'Invalid API key'
                    }, status=401)
                else:
                    error_data = await resp.text()
                    return web.json_response({
                        'status': 'error',
                        'message': f'API error: {resp.status} - {error_data}'
                    }, status=resp.status)
                    
    except Exception as e:
        logger.error(f"Error testing Gemini connection: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Persona Workflow Endpoints

async def update_persona_workflow(request):
    """POST /api/personas/types/{type}/workflow"""
    try:
        persona_type = request.match_info['type']
        data = await request.json()
        
        # Validate required fields
        if 'workflow_yaml' not in data:
            return web.json_response({
                'status': 'error',
                'message': 'workflow_yaml is required'
            }, status=400)
        
        # Update persona type workflow
        success = persona_manager.update_persona_type(
            persona_type=persona_type,
            workflow_yaml=data['workflow_yaml'],
            workflow_version=data.get('workflow_version', '1.0'),
            workflow_last_updated=datetime.now().isoformat()
        )
        
        if not success:
            return web.json_response({
                'status': 'error',
                'message': f'Persona type not found: {persona_type}'
            }, status=404)
        
        # Save workflow history
        try:
            workflow_id = f"persona_{persona_type}"
            change_notes = data.get('change_notes', 'Updated via UI')
            created_by = data.get('created_by', 'user')
            
            version_number = workflow_history_db.add_workflow_version(
                workflow_id=workflow_id,
                yaml_content=data['workflow_yaml'],
                change_notes=change_notes,
                created_by=created_by
            )
            
            logger.info(f"Saved workflow history version {version_number} for {persona_type}")
        except Exception as e:
            logger.error(f"Failed to save workflow history: {str(e)}")
            # Continue even if history save fails
        
        return web.json_response({
            'status': 'success',
            'message': f'Workflow updated for {persona_type}',
            'version': data.get('workflow_version', '1.0')
        })
            
    except Exception as e:
        logger.error(f"Error updating workflow: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_persona_workflow_history(request):
    """GET /api/personas/types/{type}/workflow/history"""
    try:
        persona_type = request.match_info['type']
        workflow_id = f"persona_{persona_type}"
        
        # Get history from database
        history = workflow_history_db.get_workflow_history(workflow_id, limit=50)
        
        # Format the history for the frontend
        formatted_history = []
        for record in history:
            formatted_history.append({
                'id': record['id'],
                'version': record['version'],
                'change_notes': record['change_notes'] or 'No notes provided',
                'created_by': record['created_by'],
                'created_at': record['created_at'],
                'workflow_id': record['workflow_id']
            })
        
        return web.json_response({
            'status': 'success',
            'history': formatted_history
        })
        
    except Exception as e:
        logger.error(f"Error getting workflow history: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_persona_workflow_version(request):
    """GET /api/personas/types/{type}/workflow/history/{version_id}"""
    try:
        persona_type = request.match_info['type']
        version_id = request.match_info['version_id']
        workflow_id = f"persona_{persona_type}"
        
        # Get specific version from database
        try:
            version_number = int(version_id)
            version_data = workflow_history_db.get_workflow_version(workflow_id, version_number)
        except ValueError:
            return web.json_response({
                'status': 'error',
                'message': 'Invalid version ID - must be a number'
            }, status=400)
        if not version_data:
            return web.json_response({
                'status': 'error',
                'message': f'Version not found: {version_id}'
            }, status=404)
        
        return web.json_response(version_data)
        
    except Exception as e:
        logger.error(f"Error getting workflow version: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


# Repository Management Endpoints

async def get_repository_structure(request):
    """GET /api/repository/structure"""
    try:
        structure = repository_db.get_repository_structure()
        if structure:
            return web.json_response({
                'status': 'success',
                'structure': structure['structure'],
                'version': structure['version'],
                'updated_at': structure['updated_at']
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': 'No repository structure found'
            }, status=404)
    except Exception as e:
        logger.error(f"Error getting repository structure: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_repository_structure(request):
    """PUT /api/repository/structure"""
    try:
        data = await request.json()
        structure = data.get('structure')
        change_notes = data.get('changeNotes')
        
        if not structure:
            return web.json_response({
                'status': 'error',
                'message': 'structure is required'
            }, status=400)
        
        result = repository_db.update_repository_structure(
            structure=structure,
            created_by='system',
            change_notes=change_notes
        )
        
        return web.json_response({
            'status': 'success',
            'structure': result['structure'],
            'version': result['version'],
            'updated_at': result['updated_at']
        })
        
    except Exception as e:
        logger.error(f"Error updating repository structure: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_repository_structure_history(request):
    """GET /api/repository/structure/history"""
    try:
        limit = int(request.query.get('limit', 20))
        history = repository_db.get_repository_structure_history(limit)
        
        return web.json_response({
            'status': 'success',
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error getting repository structure history: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_repository_structure_version(request):
    """GET /api/repository/structure/version/{version}"""
    try:
        version = int(request.match_info['version'])
        structure = repository_db.get_repository_structure_by_version(version)
        
        if structure:
            return web.json_response({
                'status': 'success',
                'structure': structure
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': f'Version {version} not found'
            }, status=404)
            
    except Exception as e:
        logger.error(f"Error getting repository structure version: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_branching_strategy(request):
    """GET /api/repository/branching"""
    try:
        strategy = repository_db.get_branching_strategy()
        if strategy:
            return web.json_response({
                'status': 'success',
                'strategy': strategy['strategy'],
                'version': strategy['version'],
                'updated_at': strategy['updated_at']
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': 'No branching strategy found'
            }, status=404)
    except Exception as e:
        logger.error(f"Error getting branching strategy: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def update_branching_strategy(request):
    """PUT /api/repository/branching"""
    try:
        data = await request.json()
        strategy = data.get('strategy')
        change_notes = data.get('changeNotes')
        
        if not strategy:
            return web.json_response({
                'status': 'error',
                'message': 'strategy is required'
            }, status=400)
        
        result = repository_db.update_branching_strategy(
            strategy=strategy,
            created_by='system',
            change_notes=change_notes
        )
        
        return web.json_response({
            'status': 'success',
            'strategy': result['strategy'],
            'version': result['version'],
            'updated_at': result['updated_at']
        })
        
    except Exception as e:
        logger.error(f"Error updating branching strategy: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_branching_strategy_history(request):
    """GET /api/repository/branching/history"""
    try:
        limit = int(request.query.get('limit', 20))
        history = repository_db.get_branching_strategy_history(limit)
        
        return web.json_response({
            'status': 'success',
            'history': history
        })
        
    except Exception as e:
        logger.error(f"Error getting branching strategy history: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


async def get_branching_strategy_version(request):
    """GET /api/repository/branching/version/{version}"""
    try:
        version = int(request.match_info['version'])
        strategy = repository_db.get_branching_strategy_by_version(version)
        
        if strategy:
            return web.json_response({
                'status': 'success',
                'strategy': strategy
            })
        else:
            return web.json_response({
                'status': 'error',
                'message': f'Version {version} not found'
            }, status=404)
            
    except Exception as e:
        logger.error(f"Error getting branching strategy version: {str(e)}")
        return web.json_response({
            'status': 'error',
            'message': str(e)
        }, status=500)


def register_persona_routes(app):
    """Register all persona API routes with the aiohttp app"""
    # Persona management routes
    app.router.add_get('/api/personas/types', get_persona_types)
    app.router.add_post('/api/personas/types', create_persona_type)
    app.router.add_put('/api/personas/types/{type}', update_persona_type)
    app.router.add_delete('/api/personas/types/{type}', delete_persona_type)
    logger.info("Registered persona routes including POST /api/personas/types")
    app.router.add_put('/api/personas/types/{type}/prompt', update_persona_type_prompt)
    app.router.add_put('/api/personas/types/{type}/mcp-servers', update_persona_type_mcp_servers)
    app.router.add_post('/api/personas/types/{type}/generate-prompt', generate_persona_prompt)
    
    # Persona workflow routes
    app.router.add_post('/api/personas/types/{type}/workflow', update_persona_workflow)
    app.router.add_get('/api/personas/types/{type}/workflow/history', get_persona_workflow_history)
    app.router.add_get('/api/personas/types/{type}/workflow/history/{version_id}', get_persona_workflow_version)
    
    app.router.add_get('/api/personas/instances', get_persona_instances)
    app.router.add_get('/api/personas/instances/{instance_id}', get_persona_instance)
    app.router.add_post('/api/personas/instances', create_persona_instance)
    app.router.add_put('/api/personas/instances/{instance_id}', update_persona_instance)
    app.router.add_delete('/api/personas/instances/{instance_id}', delete_persona_instance)
    app.router.add_post('/api/personas/instances/{instance_id}/toggle', toggle_persona_instance)
    
    # MCP server routes
    app.router.add_get('/api/mcp-servers', get_mcp_servers)
    app.router.add_post('/api/mcp-servers/{server_name}/toggle', toggle_mcp_server)
    
    # Tools routes
    app.router.add_get('/api/tools/categories', get_tool_categories)
    app.router.add_get('/api/tools/category/{category_name}', get_tools_by_category)
    app.router.add_post('/api/tools/{tool_name}/toggle', toggle_tool)
    
    # Tool Category CRUD routes
    app.router.add_post('/api/tools/category', create_tool_category)
    app.router.add_put('/api/tools/category/{category_name}', update_tool_category)
    app.router.add_delete('/api/tools/category/{category_name}', delete_tool_category)
    
    # Individual Tool CRUD routes
    app.router.add_post('/api/tools', create_tool)
    app.router.add_put('/api/tools/{tool_name}', update_tool)
    app.router.add_delete('/api/tools/{tool_name}', delete_tool)
    
    # Import/Export tools routes
    app.router.add_post('/api/tools/import', import_tools_from_md)
    app.router.add_get('/api/tools/export', export_tools_to_md)
    
    # Bulk operations routes
    app.router.add_post('/api/tools/bulk-toggle', bulk_toggle_tools)
    
    # Settings routes
    app.router.add_get('/api/settings/mcp', get_mcp_settings)
    app.router.add_put('/api/settings/mcp', update_mcp_settings)
    app.router.add_get('/api/settings/agents', get_agent_settings)
    app.router.add_put('/api/settings/agents', update_agent_settings)
    app.router.add_post('/api/tools/category/{category_name}/toggle-all', toggle_category_tools)
    
    # AI Provider test connection routes
    app.router.add_post('/api/test-connection/openai', test_openai_connection)
    app.router.add_post('/api/test-connection/anthropic', test_anthropic_connection)
    app.router.add_post('/api/test-connection/gemini', test_gemini_connection)
    
    # Repository routes
    app.router.add_get('/api/repository/structure', get_repository_structure)
    app.router.add_put('/api/repository/structure', update_repository_structure)
    app.router.add_get('/api/repository/structure/history', get_repository_structure_history)
    app.router.add_get('/api/repository/structure/version/{version}', get_repository_structure_version)
    app.router.add_get('/api/repository/branching', get_branching_strategy)
    app.router.add_put('/api/repository/branching', update_branching_strategy)
    app.router.add_get('/api/repository/branching/history', get_branching_strategy_history)
    app.router.add_get('/api/repository/branching/version/{version}', get_branching_strategy_version)