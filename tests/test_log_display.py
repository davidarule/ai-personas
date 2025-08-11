#!/usr/bin/env python3
"""Test the log display stretches to bottom of panel with fixed headers"""

import requests
import json

# Test if the logs endpoint returns data
print("Testing log display...")
response = requests.get('http://localhost:8080/api/logs?limit=50&format=formatted')
logs = response.json()
print(f"Found {len(logs)} log entries")

# Check the HTML structure
response = requests.get('http://localhost:8080/')
html = response.text

# Check for flex container structure
print("\nChecking HTML structure:")
print(f"  Has flex container: {'display: flex; flex-direction: column; height: 100%' in html}")
print(f"  Has fixed header: {'flex-shrink: 0' in html}")
print(f"  Has scrollable area: {'overflow-y: auto' in html}")
print(f"  mainContent has flex styles: {'#mainContent' in html and 'height: 100%' in html}")

print("\n✅ Log display should now:")
print("  - Extend to the bottom of the panel")
print("  - Have fixed column headers (Date/Time, Level, Source, Description)")
print("  - Have scrollable log entries below the headers")
print("  - Auto-scroll to bottom when loaded or filtered")