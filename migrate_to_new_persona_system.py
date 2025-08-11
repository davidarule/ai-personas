#!/usr/bin/env python3
"""
Migration script to set up the new dynamic persona system
"""

import json
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.personas.processor_factory_new import ProcessorFactory
from src.personas.persona_manager import PersonaManager

def main():
    print("=== AI Personas System Migration ===")
    print("Migrating to new dynamic persona system...")
    
    # 1. Create config directory
    config_dir = Path("/opt/ai-personas/config")
    config_dir.mkdir(exist_ok=True)
    print(f"✓ Created config directory: {config_dir}")
    
    # 2. Initialize persona manager (will create personas.json)
    persona_manager = PersonaManager()
    print("✓ Initialized persona manager")
    
    # 3. Create default persona instances for Steve and Kav
    print("\nCreating default persona instances:")
    
    steve = persona_manager.create_instance(
        persona_type="software-architect",
        first_name="Steve",
        last_name="Bot",
        email="steve@company.com",
        skills=["System Architecture", "Security Architecture", "Threat Modeling", "Cloud Design"],
        mcp_servers=["memory", "filesystem", "github", "context7"],
        tools=["git", "vscode", "docker", "terraform"]
    )
    if steve:
        print(f"✓ Created Steve (Software Architect): {steve.instance_id}")
    
    kav = persona_manager.create_instance(
        persona_type="qa-test-engineer",
        first_name="Kav",
        last_name="Bot", 
        email="kav@company.com",
        skills=["Security Testing", "SAST", "DAST", "Test Automation"],
        mcp_servers=["memory", "filesystem", "github"],
        tools=["jest", "pytest", "selenium", "burpsuite"]
    )
    if kav:
        print(f"✓ Created Kav (QA/Test Engineer): {kav.instance_id}")
    
    # 4. Create example instances for other persona types
    print("\nCreating example instances for demonstration:")
    
    examples = [
        {
            "persona_type": "devsecops-engineer",
            "first_name": "Deso",
            "skills": ["CI/CD", "Container Security", "Infrastructure as Code"],
            "mcp_servers": ["memory", "filesystem", "github", "postgres"],
            "tools": ["jenkins", "docker", "kubernetes", "terraform"]
        },
        {
            "persona_type": "frontend-developer",
            "first_name": "Frendy",
            "skills": ["React", "TypeScript", "UI Development", "Web Performance"],
            "mcp_servers": ["memory", "filesystem", "github", "context7"],
            "tools": ["vscode", "webpack", "jest", "chrome-devtools"]
        },
        {
            "persona_type": "backend-developer",
            "first_name": "Backy",
            "skills": ["Python", "Node.js", "API Design", "Database Design"],
            "mcp_servers": ["memory", "filesystem", "github", "postgres", "context7"],
            "tools": ["vscode", "postman", "docker", "pytest"]
        }
    ]
    
    for ex in examples:
        instance = persona_manager.create_instance(
            persona_type=ex["persona_type"],
            first_name=ex["first_name"],
            last_name="Bot",
            email=f"{ex['first_name'].lower()}@company.com",
            skills=ex["skills"],
            mcp_servers=ex["mcp_servers"],
            tools=ex["tools"]
        )
        if instance:
            print(f"✓ Created {ex['first_name']} ({instance.persona_type}): {instance.instance_id}")
    
    # 5. Update settings_extended.json if it doesn't exist
    settings_path = Path("/opt/ai-personas/settings_extended.json")
    if not settings_path.exists():
        print("\nCreating settings_extended.json...")
        
        # Load existing settings.json
        old_settings_path = Path("/opt/ai-personas/settings.json")
        if old_settings_path.exists():
            with open(old_settings_path, 'r') as f:
                old_settings = json.load(f)
        else:
            old_settings = {}
        
        # Create extended settings
        extended_settings = {
            "version": "2.0",
            **old_settings,  # Include all old settings
            "personas": {
                "enabled": True,
                "defaultEmailDomain": "company.com",
                "instances": []  # Will be populated by persona_manager
            },
            "mcp_servers": {
                "available": [
                    {
                        "name": "memory",
                        "displayName": "Memory",
                        "description": "Knowledge graph for persistent memory",
                        "enabled": True,
                        "config": {}
                    },
                    {
                        "name": "filesystem",
                        "displayName": "File System",
                        "description": "File system operations",
                        "enabled": True,
                        "config": {}
                    },
                    {
                        "name": "github",
                        "displayName": "GitHub",
                        "description": "GitHub repository operations",
                        "enabled": True,
                        "config": {}
                    },
                    {
                        "name": "postgres",
                        "displayName": "PostgreSQL",
                        "description": "PostgreSQL database operations",
                        "enabled": True,
                        "config": {
                            "connectionString": ""
                        }
                    },
                    {
                        "name": "context7",
                        "displayName": "Context7",
                        "description": "Documentation retrieval",
                        "enabled": True,
                        "config": {}
                    },
                    {
                        "name": "serena",
                        "displayName": "Serena",
                        "description": "Code analysis and navigation",
                        "enabled": True,
                        "config": {}
                    }
                ]
            },
            "tools": {
                "categories": [
                    {
                        "name": "development",
                        "displayName": "Development Tools",
                        "tools": [
                            {"name": "git", "displayName": "Git", "description": "Version control", "enabled": True},
                            {"name": "vscode", "displayName": "VS Code", "description": "Code editor", "enabled": True},
                            {"name": "debugger", "displayName": "Debugger", "description": "Code debugging", "enabled": True}
                        ]
                    },
                    {
                        "name": "testing",
                        "displayName": "Testing Tools",
                        "tools": [
                            {"name": "jest", "displayName": "Jest", "description": "JavaScript testing", "enabled": True},
                            {"name": "pytest", "displayName": "PyTest", "description": "Python testing", "enabled": True},
                            {"name": "selenium", "displayName": "Selenium", "description": "Browser automation", "enabled": True},
                            {"name": "burpsuite", "displayName": "Burp Suite", "description": "Security testing", "enabled": True}
                        ]
                    },
                    {
                        "name": "ci_cd",
                        "displayName": "CI/CD Tools",
                        "tools": [
                            {"name": "jenkins", "displayName": "Jenkins", "description": "CI/CD automation", "enabled": True},
                            {"name": "github_actions", "displayName": "GitHub Actions", "description": "GitHub CI/CD", "enabled": True},
                            {"name": "docker", "displayName": "Docker", "description": "Containerization", "enabled": True},
                            {"name": "kubernetes", "displayName": "Kubernetes", "description": "Container orchestration", "enabled": True}
                        ]
                    },
                    {
                        "name": "cloud",
                        "displayName": "Cloud Tools",
                        "tools": [
                            {"name": "aws", "displayName": "AWS CLI", "description": "AWS management", "enabled": True},
                            {"name": "azure", "displayName": "Azure CLI", "description": "Azure management", "enabled": True},
                            {"name": "terraform", "displayName": "Terraform", "description": "Infrastructure as Code", "enabled": True}
                        ]
                    },
                    {
                        "name": "collaboration",
                        "displayName": "Collaboration Tools",
                        "tools": [
                            {"name": "jira", "displayName": "Jira", "description": "Issue tracking", "enabled": True},
                            {"name": "confluence", "displayName": "Confluence", "description": "Documentation", "enabled": True},
                            {"name": "slack", "displayName": "Slack", "description": "Team communication", "enabled": True}
                        ]
                    }
                ]
            },
            "workflows": {
                "baseDirectory": "/opt/ai-personas/src/workflows/definitions",
                "categories": {
                    "master": {
                        "displayName": "Master Workflows",
                        "description": "High-level orchestration workflows",
                        "workflows": ["wf0", "wf1", "wf2"]
                    },
                    "core": {
                        "displayName": "Core Workflows",
                        "description": "Core processing workflows",
                        "workflows": ["wf3", "wf4", "wf5", "wf6", "wf7", "wf8"]
                    },
                    "support": {
                        "displayName": "Support Workflows",
                        "description": "Supporting utility workflows",
                        "workflows": ["wf9", "wf10", "wf11", "wf12", "wf13", "wf14", "wf15", "wf16", "wf17"]
                    },
                    "personas": {
                        "displayName": "Persona Workflows",
                        "description": "Persona-specific workflows",
                        "workflows": []
                    }
                }
            }
        }
        
        with open(settings_path, 'w') as f:
            json.dump(extended_settings, f, indent=2)
        print(f"✓ Created {settings_path}")
    
    # 6. Create templates directory for claude.md files
    templates_dir = Path("/opt/ai-personas/templates")
    templates_dir.mkdir(exist_ok=True)
    print(f"\n✓ Created templates directory: {templates_dir}")
    
    # 7. Summary
    print("\n=== Migration Complete ===")
    print(f"✓ Created {len(persona_manager.get_all_instances())} persona instances")
    print("✓ Settings updated to version 2.0")
    print("✓ New persona API endpoints available")
    print("\nNext steps:")
    print("1. Restart the API server: python3 src/api/real_factory_api.py")
    print("2. Access the dashboard at http://localhost:3000/index.html")
    print("3. Use the Settings > Personas tab to manage persona instances")
    print("4. Create new personas with the '+' button in the left panel")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())