#!/usr/bin/env python3
"""
New Processor Factory for AI Personas
Creates and manages persona processor instances using the new persona type system
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path
import json

# Import the new persona system
from .types import PERSONA_TYPE_MAPPING, register_all_personas
from .models import PersonaInstance, PersonaRegistry, persona_registry

# Import existing processors for backward compatibility
from .processors.steve_processor import SteveProcessor
from .processors.kav_processor_enhanced import KavProcessorEnhanced
from .processors.base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class ProcessorFactory:
    """Factory class to create and manage persona processors using the new system"""
    
    # Legacy processor mapping for existing implementations
    LEGACY_PROCESSOR_MAPPING = {
        'software-architect': SteveProcessor,  # Steve is our Software Architect
        'qa-test-engineer': KavProcessorEnhanced,  # Kav is our QA/Test Engineer
    }
    
    def __init__(self, output_directory: str = "outputs", 
                 settings_path: str = "settings.json"):
        """Initialize the processor factory
        
        Args:
            output_directory: Base directory for processor outputs
            settings_path: Path to settings.json for configuration
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self.settings_path = settings_path
        
        # Register all persona types
        register_all_personas()
        
        # Get the global registry
        self.registry = persona_registry  # Use the global singleton
        
        # Track active instances
        self._processor_instances: Dict[str, BaseProcessor] = {}
        self._persona_instances: Dict[str, PersonaInstance] = {}
        
        # Load settings
        self._load_settings()
        
    def _load_settings(self):
        """Load settings from settings.json"""
        try:
            with open(self.settings_path, 'r') as f:
                self.settings = json.load(f)
        except Exception as e:
            logger.warning(f"Could not load settings: {e}")
            self.settings = {}
    
    def create_persona_instance(self, 
                               persona_type: str,
                               instance_id: Optional[str] = None,
                               first_name: Optional[str] = None,
                               last_name: Optional[str] = None,
                               email: Optional[str] = None,
                               skills: Optional[List[str]] = None,
                               mcp_servers: Optional[List[str]] = None,
                               tools: Optional[List[str]] = None) -> Optional[PersonaInstance]:
        """Create a new persona instance
        
        Args:
            persona_type: Type of persona (e.g., 'software-architect')
            instance_id: Unique ID for this instance (auto-generated if not provided)
            first_name: Override default first name
            last_name: Override default last name
            email: Override default email
            skills: Additional skills for this instance
            mcp_servers: Override MCP servers
            tools: Override tools
            
        Returns:
            PersonaInstance or None if type not found
        """
        # Get the persona type configuration
        persona_config = self.registry.get(persona_type)
        if not persona_config:
            logger.error(f"Unknown persona type: {persona_type}")
            return None
        
        # Create the instance
        instance = PersonaInstance.from_config(
            persona_config,
            instance_id=instance_id,
            first_name=first_name,
            last_name=last_name,
            email=email,
            skills=skills,
            mcp_servers=mcp_servers,
            tools=tools
        )
        
        if instance:
            self._persona_instances[instance.instance_id] = instance
            
            # Create legacy processor if available
            if persona_type and persona_type in self.LEGACY_PROCESSOR_MAPPING:
                self._create_legacy_processor(instance)
            
            logger.info(f"Created persona instance: {instance.instance_id} ({instance.full_name})")
        
        return instance
    
    def _create_legacy_processor(self, instance: PersonaInstance) -> Optional[BaseProcessor]:
        """Create a legacy processor for backward compatibility
        
        Args:
            instance: PersonaInstance to create processor for
            
        Returns:
            BaseProcessor or None
        """
        processor_class = self.LEGACY_PROCESSOR_MAPPING.get(instance.persona_type)
        if not processor_class:
            return None
        
        try:
            # Create processor with persona-specific output directory
            output_dir = self.output_directory / instance.first_name.lower()
            processor = processor_class(str(output_dir))
            self._processor_instances[instance.instance_id] = processor
            logger.info(f"Created legacy processor for {instance.instance_id}")
            return processor
        except Exception as e:
            logger.error(f"Failed to create legacy processor: {e}")
            return None
    
    def get_persona_instance(self, instance_id: str) -> Optional[PersonaInstance]:
        """Get a specific persona instance
        
        Args:
            instance_id: ID of the instance
            
        Returns:
            PersonaInstance or None
        """
        return self._persona_instances.get(instance_id)
    
    def get_all_instances(self) -> Dict[str, PersonaInstance]:
        """Get all active persona instances
        
        Returns:
            Dictionary of instance_id to PersonaInstance
        """
        return self._persona_instances.copy()
    
    def get_instances_by_type(self, persona_type: str) -> List[PersonaInstance]:
        """Get all instances of a specific persona type
        
        Args:
            persona_type: Type of persona
            
        Returns:
            List of PersonaInstance objects
        """
        return [
            instance for instance in self._persona_instances.values()
            if instance.persona_type == persona_type
        ]
    
    def get_processor(self, instance_id: str) -> Optional[BaseProcessor]:
        """Get the legacy processor for an instance (if available)
        
        Args:
            instance_id: ID of the persona instance
            
        Returns:
            BaseProcessor or None
        """
        return self._processor_instances.get(instance_id)
    
    def process_work_item(self, instance_id: str, work_item_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a work item with a specific persona instance
        
        Args:
            instance_id: ID of the persona instance
            work_item_data: Work item data to process
            
        Returns:
            Processing result
        """
        instance = self.get_persona_instance(instance_id)
        if not instance:
            return {
                'status': 'error',
                'message': f'Persona instance not found: {instance_id}'
            }
        
        # Update instance status
        instance.update_status("working", f"Processing work item {work_item_data.get('id', 'unknown')}")
        
        # Check for legacy processor
        processor = self.get_processor(instance_id)
        if processor:
            try:
                result = processor.process_work_item(work_item_data)
                return {
                    'status': 'success',
                    'instance_id': instance_id,
                    'persona_type': instance.persona_type,
                    'result': result
                }
            except Exception as e:
                logger.error(f"Error processing work item: {e}")
                return {
                    'status': 'error',
                    'message': str(e)
                }
        else:
            # For personas without legacy processors, return a simulated result
            return {
                'status': 'simulated',
                'instance_id': instance_id,
                'persona_type': instance.persona_type,
                'message': f'{instance.full_name} would process this work item'
            }
    
    def get_available_persona_types(self) -> List[Dict[str, Any]]:
        """Get information about all available persona types
        
        Returns:
            List of persona type information
        """
        types = []
        for persona_type in self.registry.list_all():
            config = self.registry.get(persona_type)
            if config:
                types.append({
                    'persona_type': persona_type,
                    'display_name': config.display_name,
                    'description': config.description,
                    'category': config.category,
                    'has_processor': persona_type in self.LEGACY_PROCESSOR_MAPPING,
                    'instance_count': len(self.get_instances_by_type(persona_type))
                })
        return sorted(types, key=lambda x: x['display_name'])
    
    def migrate_legacy_persona(self, legacy_name: str) -> Optional[PersonaInstance]:
        """Migrate a legacy persona (like 'steve') to the new system
        
        Args:
            legacy_name: Legacy persona name (e.g., 'steve', 'kav')
            
        Returns:
            PersonaInstance or None
        """
        # Mapping of legacy names to new persona types
        legacy_mapping = {
            'steve': 'software-architect',
            'kav': 'qa-test-engineer',
            'lachlan': 'devsecops-engineer',
            'dave': 'security-engineer',
            'jordan': 'backend-developer',
            'puck': 'developer-engineer',
            'moby': 'mobile-developer',
            'shaun': 'ui-ux-designer',
            'matt': 'frontend-developer',
            'laureen': 'technical-writer',
            'brumbie': 'project-manager',
            'ruley': 'requirements-analyst',
            'claude': 'ai-engineer'
        }
        
        persona_type = legacy_mapping.get(legacy_name.lower())
        if not persona_type:
            logger.error(f"Unknown legacy persona: {legacy_name}")
            return None
        
        # Create instance with legacy name as instance ID
        return self.create_persona_instance(
            persona_type=persona_type,
            instance_id=f"{legacy_name}-legacy"
        )
    
    def save_state(self):
        """Save the current state of all personas"""
        state = {
            'instances': {}
        }
        
        for instance_id, instance in self._persona_instances.items():
            state['instances'][instance_id] = {
                'persona_type': instance.persona_type,
                'first_name': instance.first_name,
                'last_name': instance.last_name,
                'email': instance.email,
                'skills': instance.skills,
                'mcp_servers': instance.mcp_servers,
                'tools': instance.tools,
                'metrics': {
                    'work_items_processed': instance.work_items_processed,
                    'created_at': instance.created_at.isoformat(),
                    'last_active': instance.last_activity.isoformat() if instance.last_activity else None
                }
            }
        
        # Save to file
        state_file = self.output_directory / 'persona_state.json'
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=2)
        
        logger.info(f"Saved state for {len(state['instances'])} personas")
    
    def load_state(self):
        """Load previously saved persona state"""
        state_file = self.output_directory / 'persona_state.json'
        if not state_file.exists():
            logger.info("No saved state found")
            return
        
        try:
            with open(state_file, 'r') as f:
                state = json.load(f)
            
            # Recreate instances
            for instance_id, data in state.get('instances', {}).items():
                instance = self.create_persona_instance(
                    persona_type=data['persona_type'],
                    instance_id=instance_id,
                    first_name=data.get('first_name'),
                    last_name=data.get('last_name'),
                    email=data.get('email'),
                    skills=data.get('skills'),
                    mcp_servers=data.get('mcp_servers'),
                    tools=data.get('tools')
                )
                
                # Restore metrics
                if instance and 'metrics' in data:
                    instance._work_items_processed = data['metrics'].get('work_items_processed', 0)
            
            logger.info(f"Loaded state for {len(self._persona_instances)} personas")
            
        except Exception as e:
            logger.error(f"Failed to load state: {e}")
    
    def shutdown_all(self):
        """Shutdown all processor instances and save state"""
        # Save state before shutdown
        self.save_state()
        
        # Shutdown legacy processors
        for instance_id, processor in self._processor_instances.items():
            logger.info(f"Shutting down processor for {instance_id}")
            # Add any cleanup if needed
        
        self._processor_instances.clear()
        self._persona_instances.clear()