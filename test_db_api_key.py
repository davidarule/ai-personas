#!/usr/bin/env python3
"""Test database API key retrieval"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from database import get_agents_database

# Get the database instance
agents_db = get_agents_database()

# Get all settings to see what's stored
settings = agents_db.get_all_settings()
print("All settings:")
print(settings)
print()

# Try to get decrypted API key for OpenAI
print("Attempting to get OpenAI API key...")
api_key = agents_db.get_decrypted_api_key('openai')
print(f"API key retrieved: {'Yes' if api_key else 'No'}")
if api_key:
    print(f"API key length: {len(api_key)}")
    print(f"API key starts with: {api_key[:10]}...")