#!/usr/bin/env python3
"""
Update persona types with default tools and skills from MD files
"""

import re
from pathlib import Path

# Parse the persona-tool-recommendations.md file
def parse_tool_recommendations():
    tools_file = Path("/opt/ai-personas/src/workflows/definitions/personas/persona-tool-recommendations.md")
    with open(tools_file, 'r') as f:
        content = f.read()
    
    persona_tools = {}
    current_persona = None
    current_tools = []
    
    lines = content.split('\n')
    for line in lines:
        # Match persona headers like "## 1. DevSecOps Engineer"
        match = re.match(r'^## \d+\. (.+)$', line)
        if match:
            if current_persona:
                persona_tools[current_persona] = current_tools
            current_persona = match.group(1).strip()
            current_tools = []
        # Match tool lines like "- **CI/CD:** Jenkins, GitLab CI, GitHub Actions"
        elif line.startswith('- **') and current_persona:
            # Extract tools from the line
            parts = line.split(':', 1)
            if len(parts) == 2:
                tools_str = parts[1].strip()
                # Split by comma and clean up
                tools = [t.strip() for t in tools_str.split(',')]
                current_tools.extend(tools)
    
    # Don't forget the last persona
    if current_persona:
        persona_tools[current_persona] = current_tools
    
    return persona_tools

# Parse the persona-skills.md file
def parse_skills():
    skills_file = Path("/opt/ai-personas/src/workflows/definitions/personas/persona-skills.md")
    with open(skills_file, 'r') as f:
        content = f.read()
    
    persona_skills = {}
    current_persona = None
    current_skills = []
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        # Match persona headers like "DevSecOps Engineer (25 skills)"
        match = re.match(r'^(.+) \(\d+ skills\)$', line)
        if match:
            if current_persona:
                persona_skills[current_persona] = current_skills
            current_persona = match.group(1).strip()
            current_skills = []
        elif current_persona and line.strip() and not line.strip().startswith('Comprehensive'):
            # This is a skill line
            skill = line.strip()
            if skill:
                current_skills.append(skill)
    
    # Don't forget the last persona
    if current_persona:
        persona_skills[current_persona] = current_skills
    
    return persona_skills

# Map persona names to file names
PERSONA_MAPPING = {
    "DevSecOps Engineer": "devsecops_engineer.py",
    "Software Architect": "software_architect.py",
    "Developer/Software Engineer": "developer_engineer.py",
    "Front End Developer": "frontend_developer.py",
    "Back End Developer": "backend_developer.py",
    "Mobile Developer": "mobile_developer.py",
    "QA/Test Engineer": "qa_test_engineer.py",
    "Product Owner": "product_owner.py",
    "Technical Writer": "technical_writer.py",
    "Business Analyst": "business_analyst.py",
    "Requirements Analyst": "requirements_analyst.py",
    "AI Engineer": "ai_engineer.py",
    "Engineering Manager": "engineering_manager.py",
    "Scrum Master": "scrum_master.py",
    "Site Reliability Engineer": "site_reliability_engineer.py",
    "Security Engineer": "security_engineer.py",
    "Cloud Engineer": "cloud_architect.py",
    "Data Engineer/Database Administrator": "data_engineer.py",
    "Systems Architect": "systems_architect.py",
    "Security Architect": "security_architect.py",
    "UI/UX Designer": "ui_ux_designer.py",
    "Test Engineer": "qa_test_engineer.py",
    "Configuration & Release Engineer": "configuration_release_engineer.py",
    "Software QA": "qa_test_engineer.py",
    "Integration Engineer": "integration_engineer.py"
}

def update_persona_file(filename, tools, skills):
    """Update a persona file with tools and skills"""
    file_path = Path(f"/opt/ai-personas/src/personas/types/{filename}")
    if not file_path.exists():
        print(f"Warning: {filename} not found")
        return
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Update default_skills
    if skills:
        # Format skills list
        skills_str = ",\n                ".join([f'"{skill}"' for skill in skills[:20]])  # Limit to 20 skills
        content = re.sub(
            r'(default_skills=\[)[^\]]*(\])',
            f'\\1\n                {skills_str}\n            \\2',
            content
        )
    
    # Update default_tools
    if tools:
        # Clean and deduplicate tools
        clean_tools = []
        seen = set()
        for tool in tools[:30]:  # Limit to 30 tools
            # Convert tool names to lowercase identifiers
            tool_id = tool.lower().replace(' ', '-').replace('/', '-').replace('(', '').replace(')', '')
            if tool_id not in seen:
                seen.add(tool_id)
                clean_tools.append(tool_id)
        
        tools_str = ",\n                ".join([f'"{tool}"' for tool in clean_tools])
        content = re.sub(
            r'(default_tools=\[)[^\]]*(\])',
            f'\\1\n                {tools_str}\n            \\2',
            content
        )
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"Updated {filename} with {len(skills)} skills and {len(tools)} tools")

def main():
    print("Parsing tool recommendations...")
    persona_tools = parse_tool_recommendations()
    
    print("Parsing skills...")
    persona_skills = parse_skills()
    
    print("\nUpdating persona files...")
    
    # Update each persona
    for persona_name, filename in PERSONA_MAPPING.items():
        tools = persona_tools.get(persona_name, [])
        skills = persona_skills.get(persona_name, [])
        
        if tools or skills:
            update_persona_file(filename, tools, skills)
        else:
            print(f"No data found for {persona_name}")
    
    # Handle special cases
    # Database Administrator uses Data Engineer data
    if "Data Engineer/Database Administrator" in persona_tools:
        update_persona_file(
            "database_administrator.py",
            persona_tools["Data Engineer/Database Administrator"],
            persona_skills.get("Data Engineer/Database Administrator", [])
        )
    
    # Project Manager doesn't have specific entries in the files
    print("\nNote: Project Manager persona has no specific tools/skills in the provided files")
    
    print("\nUpdate complete!")

if __name__ == "__main__":
    main()