#!/usr/bin/env python3
"""
Persona Models for AI Personas System
Defines the base classes for persona configuration and runtime instances
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class PersonaConfig:
    """Configuration for a persona type"""
    
    # Identity
    persona_type: str  # e.g., 'software-architect', 'devsecops-engineer'
    display_name: str  # e.g., 'Software Architect'
    description: str   # Brief description of the persona's role
    
    # Default instance values
    default_first_name: str
    default_last_name: str = "Bot"
    default_email_domain: str = "company.com"
    
    # Capabilities
    default_skills: List[str] = field(default_factory=list)
    default_mcp_servers: List[str] = field(default_factory=list)
    default_tools: List[str] = field(default_factory=list)
    
    # Workflow
    workflow_id: str = ""  # e.g., 'persona-software-architect-workflow'
    
    # Instructions
    claude_md_template: str = ""  # Template for persona-specific instructions
    
    # Prompt configuration
    prompt: str = ""  # Persona-specific prompt that builds on system prompt
    external_version: str = "1"  # Version of the persona prompt
    prompt_change_notes: str = ""  # Notes about what changed in the prompt
    prompt_last_updated: str = ""  # ISO timestamp of last prompt update
    
    # Metadata
    category: str = "general"  # e.g., 'development', 'operations', 'management'
    priority: int = 0  # For sorting in UI
    requires_custom_integration: bool = False  # Whether this persona needs custom processor
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'persona_type': self.persona_type,
            'display_name': self.display_name,
            'description': self.description,
            'default_first_name': self.default_first_name,
            'default_last_name': self.default_last_name,
            'default_email_domain': self.default_email_domain,
            'default_skills': self.default_skills,
            'default_mcp_servers': self.default_mcp_servers,
            'default_tools': self.default_tools,
            'workflow_id': self.workflow_id,
            'claude_md_template': self.claude_md_template,
            'prompt': self.prompt,
            'external_version': self.external_version,
            'prompt_change_notes': self.prompt_change_notes,
            'prompt_last_updated': self.prompt_last_updated,
            'category': self.category,
            'priority': self.priority,
            'requires_custom_integration': self.requires_custom_integration
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonaConfig':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class PersonaInstance:
    """Runtime instance of a persona"""
    
    # Identity
    instance_id: str  # Unique ID for this instance
    persona_type: str  # Reference to PersonaConfig
    first_name: str
    last_name: str
    email: str
    
    # Configuration
    skills: List[str] = field(default_factory=list)
    mcp_servers: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    claude_md: str = ""  # Customized instructions for this instance
    
    # Runtime state
    status: str = "idle"  # idle, working, error, disabled
    current_task: Optional[str] = None
    last_activity: Optional[datetime] = None
    
    # Metrics
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_processing_time: float = 0.0
    
    # Azure DevOps integration
    azure_devops_id: Optional[str] = None  # User ID in Azure DevOps
    assigned_projects: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Initialize runtime attributes"""
        if not self.email:
            # Default email domain - can't use email_domain property here as email is not set yet
            self.email = f"{self.first_name.lower()}.{self.last_name.lower()}@company.com"
        if not self.instance_id:
            self.instance_id = f"{self.persona_type}-{self.first_name.lower()}-{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    @property
    def display_name(self) -> str:
        """Get display name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def email_domain(self) -> str:
        """Extract email domain"""
        return self.email.split('@')[1] if '@' in self.email else 'company.com'
    
    @property
    def is_active(self) -> bool:
        """Check if instance is active"""
        return self.status not in ['disabled', 'error']
    
    @is_active.setter
    def is_active(self, value: bool):
        """Set active state"""
        self.status = 'idle' if value else 'disabled'
    
    @property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def work_items_processed(self) -> int:
        """Get total work items processed"""
        return self.tasks_completed + self.tasks_failed
    
    @property
    def created_at(self) -> datetime:
        """Get creation time - for now, use current time"""
        # TODO: Store actual creation time
        return datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            'instance_id': self.instance_id,
            'persona_type': self.persona_type,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'skills': self.skills,
            'mcp_servers': self.mcp_servers,
            'tools': self.tools,
            'claude_md': self.claude_md,
            'status': self.status,
            'current_task': self.current_task,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_processing_time': self.total_processing_time,
            'azure_devops_id': self.azure_devops_id,
            'assigned_projects': self.assigned_projects
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PersonaInstance':
        """Create from dictionary"""
        # Handle datetime conversion
        if data.get('last_activity'):
            data['last_activity'] = datetime.fromisoformat(data['last_activity'])
        return cls(**data)
    
    @classmethod
    def from_config(cls, config: PersonaConfig, **overrides) -> 'PersonaInstance':
        """Create instance from persona config with optional overrides"""
        # Generate default email if not provided
        default_email = ''
        if not overrides.get('email'):
            first_name = overrides.get('first_name', config.default_first_name)
            last_name = overrides.get('last_name', config.default_last_name)
            default_email = f"{first_name.lower()}.{last_name.lower()}@{config.default_email_domain}"
        
        instance_data = {
            'instance_id': overrides.get('instance_id', ''),  # Will be generated in __post_init__ if empty
            'persona_type': config.persona_type,
            'first_name': overrides.get('first_name', config.default_first_name),
            'last_name': overrides.get('last_name', config.default_last_name),
            'email': overrides.get('email', default_email),
            'skills': overrides.get('skills', config.default_skills.copy()),
            'mcp_servers': overrides.get('mcp_servers', config.default_mcp_servers.copy()),
            'tools': overrides.get('tools', config.default_tools.copy()),
            'claude_md': overrides.get('claude_md', config.claude_md_template)
        }
        
        # Merge any additional overrides
        for key, value in overrides.items():
            if key not in instance_data:
                instance_data[key] = value
        
        return cls(**instance_data)
    
    def update_status(self, status: str, task: Optional[str] = None):
        """Update persona status"""
        self.status = status
        self.current_task = task
        self.last_activity = datetime.now()
        logger.info(f"Persona {self.display_name} status updated to {status}")
    
    def complete_task(self, success: bool = True, processing_time: float = 0.0):
        """Record task completion"""
        if success:
            self.tasks_completed += 1
        else:
            self.tasks_failed += 1
        
        self.total_processing_time += processing_time
        self.update_status("idle")
        
        logger.info(f"Persona {self.display_name} completed task. "
                   f"Success: {success}, Time: {processing_time:.2f}s")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        total_tasks = self.tasks_completed + self.tasks_failed
        success_rate = (self.tasks_completed / total_tasks * 100) if total_tasks > 0 else 0
        avg_time = (self.total_processing_time / total_tasks) if total_tasks > 0 else 0
        
        return {
            'tasks_completed': self.tasks_completed,
            'tasks_failed': self.tasks_failed,
            'total_tasks': total_tasks,
            'success_rate': f"{success_rate:.1f}%",
            'total_processing_time': f"{self.total_processing_time:.2f}s",
            'average_task_time': f"{avg_time:.2f}s",
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }


class PersonaRegistry:
    """Registry for managing persona configurations"""
    
    def __init__(self):
        self._configs: Dict[str, PersonaConfig] = {}
        self._config_file = Path(__file__).parent.parent / "persona_configs.json"
        self.load_configs()
    
    def register(self, config: PersonaConfig):
        """Register a persona configuration"""
        self._configs[config.persona_type] = config
        logger.info(f"Registered persona type: {config.persona_type}")
    
    def get(self, persona_type: str) -> Optional[PersonaConfig]:
        """Get a persona configuration"""
        return self._configs.get(persona_type)
    
    def list_all(self) -> List[str]:
        """List all registered persona type names"""
        return list(self._configs.keys())
    
    def list_by_category(self, category: str) -> List[PersonaConfig]:
        """List personas by category"""
        return [c for c in self._configs.values() if c.category == category]
    
    def save_configs(self):
        """Save configurations to file"""
        data = {
            pt: config.to_dict() 
            for pt, config in self._configs.items()
        }
        
        with open(self._config_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved {len(data)} persona configurations")
    
    def load_configs(self):
        """Load configurations from file"""
        if not self._config_file.exists():
            logger.info("No persona configurations file found")
            return
        
        try:
            with open(self._config_file, 'r') as f:
                data = json.load(f)
            
            for persona_type, config_data in data.items():
                config = PersonaConfig.from_dict(config_data)
                self._configs[persona_type] = config
            
            logger.info(f"Loaded {len(self._configs)} persona configurations")
        
        except Exception as e:
            logger.error(f"Failed to load persona configurations: {e}")
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return sorted(list(set(c.category for c in self._configs.values())))


# Global registry instance
persona_registry = PersonaRegistry()