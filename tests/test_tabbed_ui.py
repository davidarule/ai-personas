#!/usr/bin/env python3
"""Test the tabbed settings UI"""

import requests
import time

# Test saving system settings only
print("Testing system settings save...")
response = requests.post('http://localhost:8080/api/settings', json={
    'systemLogRetentionDays': 14,
    'personaLogRetentionDays': 30
})
print(f"Response: {response.status_code}")
print(f"Body: {response.json()}")

# Check if settings were saved
time.sleep(1)
response = requests.get('http://localhost:8080/api/settings')
settings = response.json()
print(f"\nCurrent settings:")
print(f"  System retention: {settings.get('systemLogRetentionDays')}")
print(f"  Persona retention: {settings.get('personaLogRetentionDays')}")
print(f"  Org URL: {settings.get('orgUrl')}")
print(f"  Has PAT: {settings.get('hasPatToken')}")

# Verify the tabbed UI elements exist
response = requests.get('http://localhost:8080/')
html = response.text

print("\nChecking UI elements:")
print(f"  Has Azure DevOps tab: {'Azure DevOps</button>' in html}")
print(f"  Has System tab: {'System</button>' in html}")
print(f"  Has switchSettingsTab function: {'function switchSettingsTab' in html}")
print(f"  Has saveSystemSettings function: {'function saveSystemSettings' in html}")
print(f"  Has separate save buttons: {'saveSystemSettingsBtn' in html}")
print(f"  Has log retention inputs: {'systemLogRetentionDays' in html}")

print("\n✅ All tests complete!")