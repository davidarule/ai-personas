"""
Persona Types Module
Import all persona type classes
"""

from .base_persona_type import BasePersonaType
from .software_architect import SoftwareArchitectPersona
from .devsecops_engineer import DevSecOpsEngineerPersona
from .security_engineer import SecurityEngineerPersona
from .developer_engineer import DeveloperEngineerPersona
from .frontend_developer import FrontendDeveloperPersona
from .backend_developer import BackendDeveloperPersona
from .mobile_developer import MobileDeveloperPersona
from .qa_test_engineer import QATestEngineerPersona
from .business_analyst import BusinessAnalystPersona
from .technical_writer import TechnicalWriterPersona
from .product_owner import ProductOwnerPersona
from .requirements_analyst import RequirementsAnalystPersona
from .ui_ux_designer import UIUXDesignerPersona
from .data_engineer import DataEngineerPersona
from .cloud_architect import CloudArchitectPersona
from .ai_engineer import AIEngineerPersona
from .scrum_master import ScrumMasterPersona
from .site_reliability_engineer import SiteReliabilityEngineerPersona
from .engineering_manager import EngineeringManagerPersona
from .database_administrator import DatabaseAdministratorPersona
from .project_manager import ProjectManagerPersona
from .security_architect import SecurityArchitectPersona
from .configuration_release_engineer import ConfigurationReleaseEngineerPersona
from .integration_engineer import IntegrationEngineerPersona
from .systems_architect import SystemsArchitectPersona

# List of all persona type classes
PERSONA_TYPES = [
    SoftwareArchitectPersona,
    DevSecOpsEngineerPersona,
    SecurityEngineerPersona,
    DeveloperEngineerPersona,
    FrontendDeveloperPersona,
    BackendDeveloperPersona,
    MobileDeveloperPersona,
    QATestEngineerPersona,
    BusinessAnalystPersona,
    TechnicalWriterPersona,
    ProductOwnerPersona,
    RequirementsAnalystPersona,
    UIUXDesignerPersona,
    DataEngineerPersona,
    CloudArchitectPersona,
    AIEngineerPersona,
    ScrumMasterPersona,
    SiteReliabilityEngineerPersona,
    EngineeringManagerPersona,
    DatabaseAdministratorPersona,
    ProjectManagerPersona,
    SecurityArchitectPersona,
    ConfigurationReleaseEngineerPersona,
    IntegrationEngineerPersona,
    SystemsArchitectPersona,
]

# Dictionary mapping persona type string to class
PERSONA_TYPE_MAPPING = {
    'software-architect': SoftwareArchitectPersona,
    'devsecops-engineer': DevSecOpsEngineerPersona,
    'security-engineer': SecurityEngineerPersona,
    'developer-engineer': DeveloperEngineerPersona,
    'frontend-developer': FrontendDeveloperPersona,
    'backend-developer': BackendDeveloperPersona,
    'mobile-developer': MobileDeveloperPersona,
    'qa-test-engineer': QATestEngineerPersona,
    'business-analyst': BusinessAnalystPersona,
    'technical-writer': TechnicalWriterPersona,
    'product-owner': ProductOwnerPersona,
    'requirements-analyst': RequirementsAnalystPersona,
    'ui-ux-designer': UIUXDesignerPersona,
    'data-engineer': DataEngineerPersona,
    'cloud-architect': CloudArchitectPersona,
    'ai-engineer': AIEngineerPersona,
    'scrum-master': ScrumMasterPersona,
    'site-reliability-engineer': SiteReliabilityEngineerPersona,
    'engineering-manager': EngineeringManagerPersona,
    'database-administrator': DatabaseAdministratorPersona,
    'project-manager': ProjectManagerPersona,
    'security-architect': SecurityArchitectPersona,
    'configuration-release-engineer': ConfigurationReleaseEngineerPersona,
    'integration-engineer': IntegrationEngineerPersona,
    'systems-architect': SystemsArchitectPersona,
}

def register_all_personas():
    """Register all persona types with the global registry"""
    for persona_class in PERSONA_TYPES:
        persona = persona_class()
        persona.register()

__all__ = [
    'BasePersonaType',
    'SoftwareArchitectPersona',
    'DevSecOpsEngineerPersona', 
    'SecurityEngineerPersona',
    'DeveloperEngineerPersona',
    'FrontendDeveloperPersona',
    'BackendDeveloperPersona',
    'MobileDeveloperPersona',
    'QATestEngineerPersona',
    'BusinessAnalystPersona',
    'TechnicalWriterPersona',
    'ProductOwnerPersona',
    'RequirementsAnalystPersona',
    'UIUXDesignerPersona',
    'DataEngineerPersona',
    'CloudArchitectPersona',
    'AIEngineerPersona',
    'ScrumMasterPersona',
    'SiteReliabilityEngineerPersona',
    'EngineeringManagerPersona',
    'DatabaseAdministratorPersona',
    'ProjectManagerPersona',
    'SecurityArchitectPersona',
    'ConfigurationReleaseEngineerPersona',
    'IntegrationEngineerPersona',
    'SystemsArchitectPersona',
    'PERSONA_TYPES',
    'PERSONA_TYPE_MAPPING',
    'register_all_personas'
]