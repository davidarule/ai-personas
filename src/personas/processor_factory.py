#!/usr/bin/env python3
"""
Processor Factory for AI Personas
Creates and manages persona processor instances
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

# Import all available processors
from .processors.steve_processor import SteveProcessor
from .processors.kav_processor_enhanced import KavProcessorEnhanced
from .processors.base_processor import BaseProcessor

logger = logging.getLogger(__name__)


class ProcessorFactory:
    """Factory class to create and manage persona processors"""
    
    # Mapping of persona names to their processor classes
    PROCESSOR_MAPPING = {
        'steve': SteveProcessor,
        'kav': KavProcessorEnhanced,
        # TODO: Add other processors as they are implemented
        # 'lachlan': LachlanProcessor,
        # 'dave': DaveProcessor,
        # 'jordan': JordanProcessor,
        # 'puck': PuckProcessor,
        # 'moby': MobyProcessor,
        # 'shaun': ShaunProcessor,
        # 'matt': MattProcessor,
        # 'laureen': LaureenProcessor,
        # 'brumbie': BrumbieProcessor,
        # 'ruley': RuleyProcessor,
        # 'claude': ClaudeProcessor
    }
    
    # Persona information for those without processors yet
    PERSONA_INFO = {
        'steve': {
            'name': 'Steve Bot',
            'role': 'System Architect',
            'skills': 'System design and technical architecture, including security',
            'status': 'active'
        },
        'kav': {
            'name': 'Kav Bot',
            'role': 'Test Engineer',
            'skills': 'Quality assurance and test planning',
            'status': 'active'
        },
        'lachlan': {
            'name': 'Lachlan Bot',
            'role': 'DevSecOps Engineer',
            'skills': 'Deployment and infrastructure',
            'status': 'not_implemented'
        },
        'dave': {
            'name': 'Dave Bot',
            'role': 'Security Engineer',
            'skills': 'Security specific implementation guidance',
            'status': 'not_implemented'
        },
        'jordan': {
            'name': 'Jordan Bot',
            'role': 'Backend Developer',
            'skills': 'Backend implementation',
            'status': 'not_implemented'
        },
        'puck': {
            'name': 'Puck Bot',
            'role': 'Developer',
            'skills': 'Core implementation specifications',
            'status': 'not_implemented'
        },
        'moby': {
            'name': 'Moby Bot',
            'role': 'Mobile Developer',
            'skills': 'Mobile-specific implementation guidance',
            'status': 'not_implemented'
        },
        'shaun': {
            'name': 'Shaun Bot',
            'role': 'UI/UX Designer',
            'skills': 'Interface design and user experience',
            'status': 'not_implemented'
        },
        'matt': {
            'name': 'Matt Bot',
            'role': 'Frontend Developer',
            'skills': 'Frontend implementation',
            'status': 'not_implemented'
        },
        'laureen': {
            'name': 'Laureen Bot',
            'role': 'Technical Writer',
            'skills': 'Documentation',
            'status': 'not_implemented'
        },
        'brumbie': {
            'name': 'Brumbie Bot',
            'role': 'Project Manager',
            'skills': 'Product management & Project coordination',
            'status': 'not_implemented'
        },
        'ruley': {
            'name': 'Ruley Bot',
            'role': 'Requirements Analyst',
            'skills': 'Requirements analysis and validation',
            'status': 'not_implemented'
        },
        'claude': {
            'name': 'Claude Bot',
            'role': 'AI Integration',
            'skills': 'AI feature integration planning',
            'status': 'not_implemented'
        }
    }
    
    def __init__(self, output_directory: str = "/tmp/ai_factory_outputs"):
        """Initialize the processor factory
        
        Args:
            output_directory: Base directory for processor outputs
        """
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(parents=True, exist_ok=True)
        self._processor_instances: Dict[str, BaseProcessor] = {}
        
    def create_processor(self, persona_type: str) -> Optional[BaseProcessor]:
        """Create a processor instance for the given persona type
        
        Args:
            persona_type: Type of persona (e.g., 'steve', 'kav')
            
        Returns:
            Processor instance or None if not implemented
        """
        persona_type = persona_type.lower()
        
        # Return existing instance if already created
        if persona_type in self._processor_instances:
            return self._processor_instances[persona_type]
        
        # Check if processor class exists
        processor_class = self.PROCESSOR_MAPPING.get(persona_type)
        if not processor_class:
            logger.warning(f"No processor implementation for persona type: {persona_type}")
            return None
        
        try:
            # Create processor instance
            output_dir = self.output_directory / persona_type
            processor = processor_class(str(output_dir))
            self._processor_instances[persona_type] = processor
            logger.info(f"Created {persona_type} processor instance")
            return processor
            
        except Exception as e:
            logger.error(f"Failed to create processor for {persona_type}: {e}")
            return None
    
    def get_processor_info(self, persona_type: str) -> Dict[str, Any]:
        """Get information about a persona processor
        
        Args:
            persona_type: Type of persona
            
        Returns:
            Dictionary with persona information
        """
        persona_type = persona_type.lower()
        
        # Get base info
        info = self.PERSONA_INFO.get(persona_type, {
            'name': f'{persona_type.title()} Bot',
            'role': 'Unknown',
            'skills': 'Not defined',
            'status': 'unknown'
        }).copy()
        
        # Check if processor is implemented
        if persona_type in self.PROCESSOR_MAPPING:
            info['status'] = 'active'
            info['has_processor'] = True
        else:
            info['has_processor'] = False
        
        # Add instance status
        info['is_instantiated'] = persona_type in self._processor_instances
        
        return info
    
    def get_all_personas(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all personas
        
        Returns:
            Dictionary mapping persona types to their info
        """
        all_personas = {}
        for persona_type in self.PERSONA_INFO:
            all_personas[persona_type] = self.get_processor_info(persona_type)
        return all_personas
    
    def get_active_personas(self) -> Dict[str, BaseProcessor]:
        """Get all currently instantiated personas
        
        Returns:
            Dictionary of active processor instances
        """
        return self._processor_instances.copy()
    
    def shutdown_all(self):
        """Shutdown all processor instances"""
        for persona_type, processor in self._processor_instances.items():
            logger.info(f"Shutting down {persona_type} processor")
            # Add any cleanup if needed
        self._processor_instances.clear()