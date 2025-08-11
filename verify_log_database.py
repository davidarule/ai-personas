#!/usr/bin/env python3
"""
Verify that logs are being stored in and retrieved from the database
"""

import sys
import requests
import time
sys.path.insert(0, 'src')

from database import get_log_database


def verify_logs():
    """Verify logs are in database and API retrieves from database"""
    
    print("=== LOG DATABASE VERIFICATION ===\n")
    
    # 1. Check database directly
    log_db = get_log_database()
    counts = log_db.get_log_counts()
    
    print("1. Database Contents:")
    print(f"   System logs: {counts['system_logs']}")
    print(f"   Persona logs: {counts['persona_logs']}")
    print(f"   Per-persona breakdown:")
    for persona, count in counts['personas'].items():
        print(f"     - {persona}: {count} logs")
    
    # 2. Get latest logs from database
    print("\n2. Latest 5 Logs from Database (Formatted):")
    latest_logs = log_db.get_latest_logs(count=5)
    for log in latest_logs:
        formatted = log_db.format_log_entry(log)
        print(f"   {formatted}")
    
    # 3. Test API retrieval (if API is running)
    print("\n3. Testing API Endpoints:")
    try:
        # Test system logs endpoint
        response = requests.get('http://localhost:8080/api/logs?type=system&limit=5')
        if response.status_code == 200:
            api_logs = response.json()
            print(f"   ✓ API returned {len(api_logs)} system logs")
        else:
            print(f"   ✗ API error: {response.status_code}")
            
        # Test persona logs endpoint
        response = requests.get('http://localhost:8080/api/logs?type=persona&limit=5')
        if response.status_code == 200:
            api_logs = response.json()
            print(f"   ✓ API returned {len(api_logs)} persona logs")
        else:
            print(f"   ✗ API error: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("   ⚠ API is not running. Start it with: python3 src/api/real_factory_api.py")
    
    # 4. Add a test log and verify it appears
    print("\n4. Adding Test Log:")
    test_message = f"Verification test at {time.strftime('%Y-%m-%d %H:%M:%S')}"
    log_id = log_db.add_system_log("info", test_message)
    print(f"   Added test log with ID: {log_id}")
    
    # Verify it was added
    latest = log_db.get_system_logs(limit=1)
    if latest and latest[0]['message'] == test_message:
        print("   ✓ Test log successfully stored and retrieved!")
    else:
        print("   ✗ Test log not found")
    
    # 5. Show how to view logs in real-time
    print("\n5. To Monitor Logs in Real-Time:")
    print("   - Start the API: python3 src/api/real_factory_api.py")
    print("   - Open dashboard: http://localhost:3000 (or your dashboard URL)")
    print("   - Or use curl: curl http://localhost:8080/api/logs?limit=10")
    print("   - For specific persona: curl http://localhost:8080/api/personas/steve/logs")
    
    print("\n✅ Verification complete!")


if __name__ == "__main__":
    verify_logs()
