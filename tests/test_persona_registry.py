#!/usr/bin/env python3
"""Test persona registry to debug issues"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from src.personas.types import register_all_personas
from src.personas.models import persona_registry

# Register all personas
print("Registering all personas...")
register_all_personas()

# Check what's in the registry
print(f"\nPersona types registered: {len(persona_registry.list_all())}")
print("\nAvailable persona types:")
for persona_type in persona_registry.list_all():
    config = persona_registry.get(persona_type)
    if config:
        print(f"  - {persona_type}: {config.display_name}")
    else:
        print(f"  - {persona_type}: ERROR - No config found")

# Test getting persona types like the API does
from src.personas.persona_manager import PersonaManager

print("\nTesting PersonaManager.get_available_persona_types()...")
try:
    manager = PersonaManager()
    types = manager.get_available_persona_types()
    print(f"Found {len(types)} persona types")
    for t in types[:3]:  # Show first 3
        print(f"  - {t['type']}: {t['display_name']}")
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()