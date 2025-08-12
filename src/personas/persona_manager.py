#!/usr/bin/env python3
"""
Persona Manager - Handles persona instance lifecycle and configuration
"""

import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime

from .models import PersonaInstance, PersonaRegistry
from .types import PERSONA_TYPE_MAPPING

logger = logging.getLogger(__name__)


class PersonaManager:
    """Manages persona instances and their configurations"""
    
    def __init__(self, config_path: str = "config/personas.json"):
        """Initialize the Persona Manager
        
        Args:
            config_path: Path to personas configuration file
        """
        self.config_path = Path(config_path)
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Register all persona types first
        from .types import register_all_personas
        register_all_personas()
        
        # Get the global registry (don't create a new one!)
        from .models import persona_registry
        self.registry = persona_registry
        
        # Log registered persona types for debugging
        logger.info(f"Persona types registered: {list(self.registry._configs.keys())}")
        
        # Load any saved persona type configurations
        self.load_persona_types()
        
        # Active instances
        self.instances: Dict[str, PersonaInstance] = {}
        
        # Load saved configuration
        self.load_config()
    
    def load_config(self):
        """Load persona configurations from file"""
        if not self.config_path.exists():
            logger.info(f"No persona config found at {self.config_path}")
            return
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Load persona instances
            for instance_data in config.get('instances', []):
                self.create_instance_from_config(instance_data)
            
            logger.info(f"Loaded {len(self.instances)} persona instances")
            
        except Exception as e:
            logger.error(f"Failed to load persona config: {e}")
    
    def save_config(self):
        """Save current persona configurations to file"""
        config = {
            'version': '2.0',
            'updated_at': datetime.now().isoformat(),
            'instances': []
        }
        
        # Save all instances
        for instance in self.instances.values():
            config['instances'].append({
                'instance_id': instance.instance_id,
                'persona_type': instance.persona_type,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'skills': instance.skills,
                'mcp_servers': instance.mcp_servers,
                'tools': instance.tools,
                'enabled': instance.is_active,
                'created_at': instance.created_at.isoformat(),
                'metrics': {
                    'work_items_processed': instance.work_items_processed,
                    'last_active': instance.last_activity.isoformat() if instance.last_activity else None
                }
            })
        
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved configuration for {len(self.instances)} personas")
        except Exception as e:
            logger.error(f"Failed to save persona config: {e}")
    
    def create_instance_from_config(self, config: Dict[str, Any]) -> Optional[PersonaInstance]:
        """Create a persona instance from configuration data
        
        Args:
            config: Configuration dictionary
            
        Returns:
            PersonaInstance or None
        """
        try:
            # Get the persona config from registry
            persona_config = self.registry.get(config['persona_type'])
            if not persona_config:
                logger.error(f"Unknown persona type: {config['persona_type']}")
                return None
                
            # Create instance from config with overrides
            # Filter out fields that aren't part of PersonaInstance
            allowed_fields = {'instance_id', 'first_name', 'last_name', 'email', 
                            'skills', 'mcp_servers', 'tools', 'claude_md'}
            overrides = {k: v for k, v in config.items() if k in allowed_fields}
            instance = PersonaInstance.from_config(persona_config, **overrides)
            
            if instance:
                # Restore metrics if available
                if 'metrics' in config:
                    # work_items_processed is a property, update the internal counter
                    instance._work_items_processed = config['metrics'].get('work_items_processed', 0)
                
                # Set enabled state
                if 'enabled' in config:
                    instance.is_active = config['enabled']
                
                self.instances[instance.instance_id] = instance
                return instance
                
        except Exception as e:
            logger.error(f"Failed to create instance from config: {e}")
            return None
    
    def create_instance(self,
                       persona_type: str,
                       first_name: Optional[str] = None,
                       last_name: Optional[str] = None,
                       email: Optional[str] = None,
                       skills: Optional[List[str]] = None,
                       mcp_servers: Optional[List[str]] = None,
                       tools: Optional[List[str]] = None) -> Optional[PersonaInstance]:
        """Create a new persona instance
        
        Args:
            persona_type: Type of persona
            first_name: Override first name
            last_name: Override last name  
            email: Override email
            skills: Additional skills
            mcp_servers: Override MCP servers
            tools: Override tools
            
        Returns:
            PersonaInstance or None
        """
        # Get the persona config from registry
        config = self.registry.get(persona_type)
        if not config:
            logger.error(f"Unknown persona type: {persona_type}")
            return None
            
        # Create instance from config with overrides
        overrides = {}
        if first_name:
            overrides['first_name'] = first_name
        if last_name:
            overrides['last_name'] = last_name
        if email:
            overrides['email'] = email
        if skills is not None:
            overrides['skills'] = skills
        if mcp_servers is not None:
            overrides['mcp_servers'] = mcp_servers
        if tools is not None:
            overrides['tools'] = tools
            
        instance = PersonaInstance.from_config(config, **overrides)
        
        if instance:
            self.instances[instance.instance_id] = instance
            self.save_config()  # Auto-save
            logger.info(f"Created persona: {instance.full_name} ({instance.instance_id})")
        
        return instance
    
    def update_instance(self,
                       instance_id: str,
                       first_name: Optional[str] = None,
                       last_name: Optional[str] = None,
                       email: Optional[str] = None,
                       skills: Optional[List[str]] = None,
                       mcp_servers: Optional[List[str]] = None,
                       tools: Optional[List[str]] = None) -> bool:
        """Update an existing persona instance
        
        Args:
            instance_id: ID of instance to update
            first_name: New first name
            last_name: New last name
            email: New email
            skills: New skills list
            mcp_servers: New MCP servers list
            tools: New tools list
            
        Returns:
            True if updated successfully
        """
        instance = self.instances.get(instance_id)
        if not instance:
            logger.error(f"Instance not found: {instance_id}")
            return False
        
        # Update fields
        if first_name is not None:
            instance.first_name = first_name
        if last_name is not None:
            instance.last_name = last_name
        if email is not None:
            instance.email = email
        if skills is not None:
            instance.skills = skills
        if mcp_servers is not None:
            instance.mcp_servers = mcp_servers
        if tools is not None:
            instance.tools = tools
        
        self.save_config()  # Auto-save
        logger.info(f"Updated persona: {instance.full_name}")
        return True
    
    def delete_instance(self, instance_id: str) -> bool:
        """Delete a persona instance
        
        Args:
            instance_id: ID of instance to delete
            
        Returns:
            True if deleted successfully
        """
        if instance_id in self.instances:
            instance = self.instances[instance_id]
            del self.instances[instance_id]
            self.save_config()  # Auto-save
            logger.info(f"Deleted persona: {instance.full_name}")
            return True
        
        logger.error(f"Instance not found: {instance_id}")
        return False
    
    def get_instance(self, instance_id: str) -> Optional[PersonaInstance]:
        """Get a specific persona instance
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            PersonaInstance or None
        """
        return self.instances.get(instance_id)
    
    def get_all_instances(self) -> List[PersonaInstance]:
        """Get all persona instances
        
        Returns:
            List of PersonaInstance objects
        """
        return list(self.instances.values())
    
    def get_instances_by_type(self, persona_type: str) -> List[PersonaInstance]:
        """Get all instances of a specific type
        
        Args:
            persona_type: Type of persona
            
        Returns:
            List of matching PersonaInstance objects
        """
        return [
            instance for instance in self.instances.values()
            if instance.persona_type == persona_type
        ]
    
    def get_active_instances(self) -> List[PersonaInstance]:
        """Get all active persona instances
        
        Returns:
            List of active PersonaInstance objects
        """
        return [
            instance for instance in self.instances.values()
            if instance.is_active
        ]
    
    def toggle_instance_active(self, instance_id: str) -> bool:
        """Toggle the active state of a persona instance
        
        Args:
            instance_id: ID of instance to toggle
            
        Returns:
            True if toggled successfully
        """
        instance = self.instances.get(instance_id)
        if not instance:
            logger.error(f"Instance not found: {instance_id}")
            return False
        
        instance.is_active = not instance.is_active
        self.save_config()  # Auto-save
        logger.info(f"Toggled {instance.full_name} active state to: {instance.is_active}")
        return True
    
    def get_instance_metrics(self, instance_id: str) -> Dict[str, Any]:
        """Get metrics for a specific instance
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            Dictionary of metrics
        """
        instance = self.instances.get(instance_id)
        if not instance:
            return {}
        
        return {
            'work_items_processed': instance.work_items_processed,
            'created_at': instance.created_at.isoformat(),
            'last_active': instance.last_activity.isoformat() if instance.last_activity else None,
            'is_active': instance.is_active,
            'uptime_hours': (datetime.now() - instance.created_at).total_seconds() / 3600
        }
    
    def get_available_persona_types(self) -> List[Dict[str, Any]]:
        """Get information about all available persona types
        
        Returns:
            List of persona type information
        """
        types = []
        try:
            for persona_type in self.registry.list_all():
                config = self.registry.get(persona_type)
                if config:
                    types.append({
                        'type': persona_type,
                        'display_name': config.display_name,
                        'description': config.description,
                        'category': config.category,
                        'default_first_name': config.default_first_name,
                        'default_last_name': config.default_last_name,
                        'default_skills': config.default_skills,
                        'default_tools': config.default_tools,
                        'default_mcp_servers': config.default_mcp_servers,
                        'default_email_domain': config.default_email_domain,
                        'prompt': getattr(config, 'prompt', ''),
                        'external_version': getattr(config, 'external_version', '1'),
                        'prompt_change_notes': getattr(config, 'prompt_change_notes', ''),
                        'prompt_last_updated': getattr(config, 'prompt_last_updated', ''),
                        'instance_count': len(self.get_instances_by_type(persona_type))
                    })
        except Exception as e:
            logger.error(f"Error getting persona types: {e}")
            # Return a simplified response
            return []
        return sorted(types, key=lambda x: x['display_name'])
    
    def get_mcp_servers_in_use(self) -> List[str]:
        """Get a list of all MCP servers currently in use
        
        Returns:
            List of unique MCP server names
        """
        servers = set()
        for instance in self.instances.values():
            servers.update(instance.mcp_servers)
        return sorted(list(servers))
    
    def get_tools_in_use(self) -> List[str]:
        """Get a list of all tools currently in use
        
        Returns:
            List of unique tool names
        """
        tools = set()
        for instance in self.instances.values():
            tools.update(instance.tools)
        return sorted(list(tools))
    
    def export_instance(self, instance_id: str) -> Optional[Dict[str, Any]]:
        """Export a persona instance configuration
        
        Args:
            instance_id: ID of instance to export
            
        Returns:
            Configuration dictionary or None
        """
        instance = self.instances.get(instance_id)
        if not instance:
            return None
        
        # Get the workflow_id from the PersonaConfig
        config = self.registry.get(instance.persona_type)
        workflow_id = config.workflow_id if config else ""
        
        return {
            'persona_type': instance.persona_type,
            'first_name': instance.first_name,
            'last_name': instance.last_name,
            'email': instance.email,
            'skills': instance.skills,
            'mcp_servers': instance.mcp_servers,
            'tools': instance.tools,
            'workflow_id': workflow_id,
            'claude_md': instance.claude_md
        }
    
    def import_instance(self, config: Dict[str, Any]) -> Optional[PersonaInstance]:
        """Import a persona instance from configuration
        
        Args:
            config: Configuration dictionary
            
        Returns:
            PersonaInstance or None
        """
        return self.create_instance(
            persona_type=config.get('persona_type'),
            first_name=config.get('first_name'),
            last_name=config.get('last_name'),
            email=config.get('email'),
            skills=config.get('skills'),
            mcp_servers=config.get('mcp_servers'),
            tools=config.get('tools')
        )
    
    def create_persona_type(self, persona_type: str, display_name: str, **kwargs) -> bool:
        """Create a new persona type configuration
        
        Args:
            persona_type: Type identifier (e.g., 'data_scientist')
            display_name: Display name (e.g., 'Data Scientist')
            **kwargs: Additional configuration fields
            
        Returns:
            bool: True if successful, False if type already exists
        """
        if persona_type in self.registry._configs:
            logger.error(f"Persona type already exists: {persona_type}")
            return False
        
        try:
            # Create new persona config
            from .models import PersonaConfig
            
            logger.info(f"Creating PersonaConfig with persona_type={persona_type}, display_name={display_name}")
            logger.info(f"Additional kwargs: {kwargs}")
            
            config = PersonaConfig(
                persona_type=persona_type,
                display_name=display_name,
                description=kwargs.get('description', f'{display_name} persona'),
                category=kwargs.get('category', 'custom'),
                default_first_name=kwargs.get('default_first_name', display_name.split()[0]),
                default_last_name=kwargs.get('default_last_name', 'Bot'),
                default_email_domain=kwargs.get('default_email_domain', 'company.com'),
                default_skills=kwargs.get('default_skills', []),
                prompt=kwargs.get('prompt', f'You are a {display_name}.'),
                external_version=str(kwargs.get('external_version', '1')),
                prompt_change_notes=kwargs.get('prompt_change_notes', 'Initial version'),
                prompt_last_updated=kwargs.get('prompt_last_updated', datetime.utcnow().isoformat()),
                default_tools=kwargs.get('default_tools', []),
                default_mcp_servers=kwargs.get('default_mcp_servers', [])
            )
            
            # Register the new persona type
            self.registry.register(config)
            
            # Save to configuration
            self.save_persona_types()
            
            logger.info(f"Created new persona type: {persona_type}")
            return True
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to create persona type: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            return False
    
    def delete_persona_type(self, persona_type: str) -> bool:
        """Delete a persona type configuration
        
        Args:
            persona_type: Type identifier to delete
            
        Returns:
            bool: True if successful, False if type not found
        """
        if persona_type not in self.registry._configs:
            logger.error(f"Persona type not found: {persona_type}")
            return False
        
        try:
            # Remove from registry
            del self.registry._configs[persona_type]
            
            # Save to configuration
            self.save_persona_types()
            
            logger.info(f"Deleted persona type: {persona_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete persona type {persona_type}: {e}")
            return False
    
    def update_persona_type(self, persona_type: str, **kwargs) -> bool:
        """Update persona type configuration
        
        Args:
            persona_type: Type identifier
            **kwargs: Fields to update
            
        Returns:
            bool: True if successful, False if type not found
        """
        if persona_type not in self.registry._configs:
            logger.error(f"Persona type not found: {persona_type}")
            return False
        
        try:
            # Get the persona config
            config = self.registry._configs[persona_type]
            
            # Update fields that were provided
            if 'display_name' in kwargs and kwargs['display_name'] is not None:
                config.display_name = kwargs['display_name']
            if 'prompt' in kwargs and kwargs['prompt'] is not None:
                config.prompt = kwargs['prompt']
            if 'external_version' in kwargs and kwargs['external_version'] is not None:
                config.external_version = kwargs['external_version']
            if 'prompt_change_notes' in kwargs and kwargs['prompt_change_notes'] is not None:
                config.prompt_change_notes = kwargs['prompt_change_notes']
            if 'prompt_last_updated' in kwargs and kwargs['prompt_last_updated'] is not None:
                config.prompt_last_updated = kwargs['prompt_last_updated']
            if 'default_skills' in kwargs and kwargs['default_skills'] is not None:
                config.default_skills = kwargs['default_skills']
            if 'default_tools' in kwargs and kwargs['default_tools'] is not None:
                config.default_tools = kwargs['default_tools']
            if 'default_mcp_servers' in kwargs and kwargs['default_mcp_servers'] is not None:
                config.default_mcp_servers = kwargs['default_mcp_servers']
            if 'category' in kwargs and kwargs['category'] is not None:
                config.category = kwargs['category']
            if 'description' in kwargs and kwargs['description'] is not None:
                config.description = kwargs['description']
            if 'default_first_name' in kwargs and kwargs['default_first_name'] is not None:
                config.default_first_name = kwargs['default_first_name']
            if 'default_last_name' in kwargs and kwargs['default_last_name'] is not None:
                config.default_last_name = kwargs['default_last_name']
            if 'default_email_domain' in kwargs and kwargs['default_email_domain'] is not None:
                config.default_email_domain = kwargs['default_email_domain']
            if 'requires_custom_integration' in kwargs and kwargs['requires_custom_integration'] is not None:
                config.requires_custom_integration = kwargs['requires_custom_integration']
            
            # Save to a persona types config file
            self.save_persona_types()
            
            logger.info(f"Updated persona type: {persona_type}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update persona type {persona_type}: {e}")
            return False
    
    def save_persona_types(self):
        """Save persona types configuration to file"""
        types_config_path = Path("config/persona_types.json")
        types_config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config = {
            'version': '1.0',
            'updated_at': datetime.now().isoformat(),
            'persona_types': {}
        }
        
        # Export all persona types
        for type_name, type_config in self.registry._configs.items():
            config['persona_types'][type_name] = {
                'display_name': type_config.display_name,
                'prompt': getattr(type_config, 'prompt', ''),
                'external_version': getattr(type_config, 'external_version', '1'),
                'prompt_change_notes': getattr(type_config, 'prompt_change_notes', ''),
                'prompt_last_updated': getattr(type_config, 'prompt_last_updated', ''),
                'category': type_config.category,
                'description': type_config.description,
                'default_first_name': type_config.default_first_name,
                'default_last_name': type_config.default_last_name,
                'default_email_domain': getattr(type_config, 'default_email_domain', '@company.com'),
                'default_skills': type_config.default_skills,
                'default_tools': type_config.default_tools,
                'default_mcp_servers': type_config.default_mcp_servers,
                'requires_custom_integration': type_config.requires_custom_integration,
                'workflow_id': type_config.workflow_id
            }
        
        try:
            with open(types_config_path, 'w') as f:
                json.dump(config, f, indent=2)
            logger.info(f"Saved configuration for {len(config['persona_types'])} persona types")
        except Exception as e:
            logger.error(f"Failed to save persona types config: {e}")
    
    def load_persona_types(self):
        """Load persona types configuration from file"""
        types_config_path = Path("config/persona_types.json")
        
        if not types_config_path.exists():
            logger.info("No saved persona types config found")
            return
        
        try:
            with open(types_config_path, 'r') as f:
                config = json.load(f)
            
            # Load all persona types from saved configuration
            for type_name, type_data in config.get('persona_types', {}).items():
                if type_name in self.registry._configs:
                    # Update existing persona type
                    persona_config = self.registry._configs[type_name]
                    # Update with saved values
                    for key, value in type_data.items():
                        if hasattr(persona_config, key) and value is not None:
                            setattr(persona_config, key, value)
                    logger.info(f"Updated persona type {type_name} from saved config")
                else:
                    # Create new persona type from saved data
                    from .models import PersonaConfig
                    
                    # Build PersonaConfig from saved data
                    config_data = {
                        'persona_type': type_name,
                        'display_name': type_data.get('display_name', type_name),
                        'description': type_data.get('description', f'{type_name} persona'),
                        'category': type_data.get('category', 'custom'),
                        'default_first_name': type_data.get('default_first_name', type_name),
                        'default_last_name': type_data.get('default_last_name', 'Bot'),
                        'default_email_domain': type_data.get('default_email_domain', 'company.com'),
                        'default_skills': type_data.get('default_skills', []),
                        'default_tools': type_data.get('default_tools', []),
                        'default_mcp_servers': type_data.get('default_mcp_servers', []),
                        'workflow_id': type_data.get('workflow_id', ''),
                        'prompt': type_data.get('prompt', ''),
                        'external_version': type_data.get('external_version', '1'),
                        'prompt_change_notes': type_data.get('prompt_change_notes', ''),
                        'prompt_last_updated': type_data.get('prompt_last_updated', ''),
                        'priority': type_data.get('priority', 0),
                        'requires_custom_integration': type_data.get('requires_custom_integration', False)
                    }
                    
                    new_config = PersonaConfig(**config_data)
                    self.registry.register(new_config)
                    logger.info(f"Loaded custom persona type {type_name} from saved config")
            
            logger.info(f"Loaded persona type configurations from {types_config_path}")
            
        except Exception as e:
            import traceback
            logger.error(f"Failed to load persona types config: {e}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
        
        # Log available persona types for debugging
        logger.info(f"Available persona types in registry: {list(self.registry._configs.keys())}")
    
    def get_agent_settings(self) -> Dict[str, Any]:
        """Get agent settings from the database
        
        Returns:
            Dictionary containing agent configuration
        """
        try:
            # Import here to avoid circular dependency
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from database import get_agents_database
            
            agents_db = get_agents_database()
            return agents_db.get_all_settings()
        except Exception as e:
            logger.error(f"Error getting agent settings: {str(e)}")
            # Return empty settings on error
            return {'providers': {}, 'customProviders': []}
    
    def update_agent_settings(self, settings: Dict[str, Any]) -> bool:
        """Update agent settings in the database
        
        Args:
            settings: Dictionary containing providers and customProviders
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Import here to avoid circular dependency
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from database import get_agents_database
            
            # The database will handle encryption, so just pass the settings through
            agents_db = get_agents_database()
            return agents_db.update_settings(settings)
        except Exception as e:
            logger.error(f"Error updating agent settings: {str(e)}")
            return False
    
    def get_provider_api_key(self, provider_id: str) -> Optional[str]:
        """Get the decrypted API key for a provider (for internal use only)
        
        Args:
            provider_id: The provider ID (e.g., 'openai', 'anthropic')
            
        Returns:
            Decrypted API key or None if not available
        """
        try:
            # Import here to avoid circular dependency
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            from database import get_agents_database
            
            agents_db = get_agents_database()
            return agents_db.get_decrypted_api_key(provider_id)
        except Exception as e:
            logger.error(f"Error getting provider API key: {str(e)}")
            return None