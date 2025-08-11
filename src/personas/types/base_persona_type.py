#!/usr/bin/env python3
"""
Base Persona Type
All persona types inherit from this base class
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from ..models import PersonaConfig


class BasePersonaType(ABC):
    """Base class for all persona types"""
    
    @abstractmethod
    def get_config(self) -> PersonaConfig:
        """Return the persona configuration"""
        pass
    
    @property
    def persona_type(self) -> str:
        """Get the persona type identifier"""
        return self.get_config().persona_type
    
    @property
    def display_name(self) -> str:
        """Get the display name"""
        return self.get_config().display_name
    
    def get_default_skills(self) -> List[str]:
        """Get default skills - can be overridden"""
        return self.get_config().default_skills
    
    def get_default_tools(self) -> List[str]:
        """Get default tools - can be overridden"""
        return self.get_config().default_tools
    
    def get_default_mcp_servers(self) -> List[str]:
        """Get default MCP servers - can be overridden"""
        return self.get_config().default_mcp_servers
    
    def get_claude_md_template(self) -> str:
        """Get Claude.md template - can be overridden"""
        return self.get_config().claude_md_template
    
    def validate_config(self) -> bool:
        """Validate the persona configuration"""
        config = self.get_config()
        
        # Basic validation
        if not config.persona_type:
            return False
        if not config.display_name:
            return False
        if not config.default_first_name:
            return False
        if not config.workflow_id:
            return False
        
        return True
    
    def get_workflow_triggers(self) -> List[Dict[str, Any]]:
        """Get workflow triggers for this persona type"""
        # Default implementation - can be overridden
        return [
            {
                'type': 'work_item_tag',
                'tags': [self.persona_type.replace('-', '_')]
            },
            {
                'type': 'work_item_assignment',
                'assigned_to': self.persona_type
            }
        ]
    
    def get_specializations(self) -> Dict[str, List[str]]:
        """Get specialization areas for this persona"""
        # Default implementation - can be overridden
        return {
            'primary': [],
            'secondary': []
        }
    
    def register(self):
        """Register this persona type with the global registry"""
        from ..models import persona_registry
        persona_registry.register(self.get_config())