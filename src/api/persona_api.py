#!/usr/bin/env python3
"""
Persona Management API Endpoints
Provides RESTful API for managing personas, MCP servers, and tools
"""

from flask import Blueprint, jsonify, request
import logging
from typing import Dict, Any, List

from ..personas.persona_manager import PersonaManager
from ..personas.types import PERSONA_TYPE_MAPPING

logger = logging.getLogger(__name__)

# Create blueprint
persona_api = Blueprint('persona_api', __name__)

# Initialize persona manager
persona_manager = PersonaManager()


# ====================== Persona Management Endpoints ======================

@persona_api.route('/api/personas/types', methods=['GET'])
def get_persona_types():
    """Get all available persona types"""
    try:
        types = persona_manager.get_available_persona_types()
        return jsonify({
            'status': 'success',
            'types': types,
            'count': len(types)
        })
    except Exception as e:
        logger.error(f"Error getting persona types: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/personas/instances', methods=['GET'])
def get_persona_instances():
    """Get all persona instances"""
    try:
        instances = []
        for instance in persona_manager.get_all_instances():
            instances.append({
                'instance_id': instance.instance_id,
                'persona_type': instance.persona_type,
                'display_name': instance.config.display_name,
                'full_name': instance.full_name,
                'email': instance.email,
                'is_active': instance.is_active,
                'work_items_processed': instance.work_items_processed,
                'created_at': instance.created_at.isoformat(),
                'last_active': instance.last_active.isoformat() if instance.last_active else None
            })
        
        return jsonify({
            'status': 'success',
            'instances': instances,
            'count': len(instances)
        })
    except Exception as e:
        logger.error(f"Error getting persona instances: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/personas/instances/<instance_id>', methods=['GET'])
def get_persona_instance(instance_id: str):
    """Get a specific persona instance"""
    try:
        instance = persona_manager.get_instance(instance_id)
        if not instance:
            return jsonify({
                'status': 'error',
                'message': f'Instance not found: {instance_id}'
            }), 404
        
        return jsonify({
            'status': 'success',
            'instance': {
                'instance_id': instance.instance_id,
                'persona_type': instance.persona_type,
                'display_name': instance.config.display_name,
                'full_name': instance.full_name,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'skills': instance.skills,
                'mcp_servers': instance.mcp_servers,
                'tools': instance.tools,
                'workflow_id': instance.config.workflow_id,
                'is_active': instance.is_active,
                'metrics': persona_manager.get_instance_metrics(instance_id)
            }
        })
    except Exception as e:
        logger.error(f"Error getting persona instance: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/personas/instances', methods=['POST'])
def create_persona_instance():
    """Create a new persona instance"""
    try:
        data = request.json
        
        # Validate required fields
        if not data.get('persona_type'):
            return jsonify({
                'status': 'error',
                'message': 'persona_type is required'
            }), 400
        
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
            return jsonify({
                'status': 'error',
                'message': 'Failed to create persona instance'
            }), 500
        
        return jsonify({
            'status': 'success',
            'instance_id': instance.instance_id,
            'message': f'Created persona: {instance.full_name}'
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating persona instance: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/personas/instances/<instance_id>', methods=['PUT'])
def update_persona_instance(instance_id: str):
    """Update a persona instance"""
    try:
        data = request.json
        
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
            return jsonify({
                'status': 'error',
                'message': f'Instance not found: {instance_id}'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': f'Updated persona instance: {instance_id}'
        })
        
    except Exception as e:
        logger.error(f"Error updating persona instance: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/personas/instances/<instance_id>', methods=['DELETE'])
def delete_persona_instance(instance_id: str):
    """Delete a persona instance"""
    try:
        success = persona_manager.delete_instance(instance_id)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': f'Instance not found: {instance_id}'
            }), 404
        
        return jsonify({
            'status': 'success',
            'message': f'Deleted persona instance: {instance_id}'
        })
        
    except Exception as e:
        logger.error(f"Error deleting persona instance: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/personas/instances/<instance_id>/toggle', methods=['POST'])
def toggle_persona_instance(instance_id: str):
    """Toggle active state of a persona instance"""
    try:
        success = persona_manager.toggle_instance_active(instance_id)
        
        if not success:
            return jsonify({
                'status': 'error',
                'message': f'Instance not found: {instance_id}'
            }), 404
        
        instance = persona_manager.get_instance(instance_id)
        return jsonify({
            'status': 'success',
            'is_active': instance.is_active,
            'message': f'Persona {"activated" if instance.is_active else "deactivated"}'
        })
        
    except Exception as e:
        logger.error(f"Error toggling persona instance: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ====================== MCP Server Endpoints ======================

@persona_api.route('/api/mcp-servers', methods=['GET'])
def get_mcp_servers():
    """Get all available MCP servers"""
    try:
        # TODO: Load from settings
        servers = [
            {
                'name': 'memory',
                'displayName': 'Memory',
                'description': 'Knowledge graph for persistent memory',
                'enabled': True,
                'in_use_by': len([i for i in persona_manager.get_all_instances() if 'memory' in i.mcp_servers])
            },
            {
                'name': 'filesystem',
                'displayName': 'File System',
                'description': 'File system operations',
                'enabled': True,
                'in_use_by': len([i for i in persona_manager.get_all_instances() if 'filesystem' in i.mcp_servers])
            },
            {
                'name': 'github',
                'displayName': 'GitHub',
                'description': 'GitHub repository operations',
                'enabled': True,
                'in_use_by': len([i for i in persona_manager.get_all_instances() if 'github' in i.mcp_servers])
            },
            {
                'name': 'postgres',
                'displayName': 'PostgreSQL',
                'description': 'PostgreSQL database operations',
                'enabled': True,
                'in_use_by': len([i for i in persona_manager.get_all_instances() if 'postgres' in i.mcp_servers])
            },
            {
                'name': 'context7',
                'displayName': 'Context7',
                'description': 'Documentation retrieval',
                'enabled': True,
                'in_use_by': len([i for i in persona_manager.get_all_instances() if 'context7' in i.mcp_servers])
            }
        ]
        
        return jsonify({
            'status': 'success',
            'servers': servers,
            'count': len(servers)
        })
    except Exception as e:
        logger.error(f"Error getting MCP servers: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/mcp-servers/<server_name>/toggle', methods=['POST'])
def toggle_mcp_server(server_name: str):
    """Toggle MCP server enabled state"""
    try:
        # TODO: Implement actual toggle in settings
        return jsonify({
            'status': 'success',
            'message': f'Toggled MCP server: {server_name}'
        })
    except Exception as e:
        logger.error(f"Error toggling MCP server: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ====================== Tools Endpoints ======================

@persona_api.route('/api/tools/categories', methods=['GET'])
def get_tool_categories():
    """Get all tool categories"""
    try:
        # TODO: Load from settings
        categories = [
            {
                'name': 'development',
                'displayName': 'Development Tools',
                'description': 'Code development and editing tools',
                'tool_count': 15
            },
            {
                'name': 'testing',
                'displayName': 'Testing Tools',
                'description': 'Testing and quality assurance tools',
                'tool_count': 12
            },
            {
                'name': 'ci_cd',
                'displayName': 'CI/CD Tools',
                'description': 'Continuous integration and deployment',
                'tool_count': 8
            },
            {
                'name': 'cloud',
                'displayName': 'Cloud Tools',
                'description': 'Cloud platform management',
                'tool_count': 10
            },
            {
                'name': 'collaboration',
                'displayName': 'Collaboration Tools',
                'description': 'Team collaboration and communication',
                'tool_count': 6
            }
        ]
        
        return jsonify({
            'status': 'success',
            'categories': categories,
            'count': len(categories)
        })
    except Exception as e:
        logger.error(f"Error getting tool categories: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/tools/category/<category_name>', methods=['GET'])
def get_tools_by_category(category_name: str):
    """Get tools in a specific category"""
    try:
        # TODO: Load from settings
        tools = []
        
        if category_name == 'development':
            tools = [
                {'name': 'git', 'displayName': 'Git', 'enabled': True},
                {'name': 'vscode', 'displayName': 'VS Code', 'enabled': True},
                {'name': 'debugger', 'displayName': 'Debugger', 'enabled': True}
            ]
        elif category_name == 'testing':
            tools = [
                {'name': 'jest', 'displayName': 'Jest', 'enabled': True},
                {'name': 'pytest', 'displayName': 'PyTest', 'enabled': True},
                {'name': 'selenium', 'displayName': 'Selenium', 'enabled': True}
            ]
        
        return jsonify({
            'status': 'success',
            'category': category_name,
            'tools': tools,
            'count': len(tools)
        })
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/tools/<tool_name>/toggle', methods=['POST'])
def toggle_tool(tool_name: str):
    """Toggle tool enabled state"""
    try:
        # TODO: Implement actual toggle in settings
        return jsonify({
            'status': 'success',
            'message': f'Toggled tool: {tool_name}'
        })
    except Exception as e:
        logger.error(f"Error toggling tool: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


# ====================== Export/Import Endpoints ======================

@persona_api.route('/api/personas/instances/<instance_id>/export', methods=['GET'])
def export_persona_instance(instance_id: str):
    """Export a persona instance configuration"""
    try:
        config = persona_manager.export_instance(instance_id)
        if not config:
            return jsonify({
                'status': 'error',
                'message': f'Instance not found: {instance_id}'
            }), 404
        
        return jsonify({
            'status': 'success',
            'config': config
        })
    except Exception as e:
        logger.error(f"Error exporting persona: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500


@persona_api.route('/api/personas/import', methods=['POST'])
def import_persona_instance():
    """Import a persona instance from configuration"""
    try:
        config = request.json
        instance = persona_manager.import_instance(config)
        
        if not instance:
            return jsonify({
                'status': 'error',
                'message': 'Failed to import persona'
            }), 500
        
        return jsonify({
            'status': 'success',
            'instance_id': instance.instance_id,
            'message': f'Imported persona: {instance.full_name}'
        }), 201
    except Exception as e:
        logger.error(f"Error importing persona: {e}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500