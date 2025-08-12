#!/usr/bin/env python3
"""Clear database entries with has_api_key=1 but no encrypted_api_key"""

import sqlite3

conn = sqlite3.connect('database/agents.db')
cursor = conn.cursor()

# Clear entries where has_api_key=1 but encrypted_api_key is NULL
cursor.execute("""
    UPDATE provider_configs 
    SET has_api_key = 0, api_key_hint = ''
    WHERE has_api_key = 1 AND encrypted_api_key IS NULL
""")

affected = cursor.rowcount
conn.commit()
conn.close()

print(f"Cleared {affected} invalid API key entries")