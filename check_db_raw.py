#!/usr/bin/env python3
"""Check raw database contents"""

import sqlite3

conn = sqlite3.connect('database/agents.db')
cursor = conn.cursor()

cursor.execute("SELECT provider_id, has_api_key, encrypted_api_key, api_key_hint FROM provider_configs")
rows = cursor.fetchall()

print("Raw database contents:")
print("provider_id | has_api_key | encrypted_api_key | api_key_hint")
print("-" * 60)
for row in rows:
    provider_id, has_api_key, encrypted_api_key, api_key_hint = row
    encrypted_preview = (encrypted_api_key[:20] + "...") if encrypted_api_key else "NULL"
    print(f"{provider_id:12} | {has_api_key:11} | {encrypted_preview:17} | {api_key_hint}")

conn.close()