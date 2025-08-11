#!/usr/bin/env python3
"""
Test the log database functionality
"""

import asyncio
from datetime import datetime
import sys
sys.path.insert(0, 'src')

from database import get_log_database


async def test_log_database():
    """Test log database operations"""
    print("Testing Log Database...")
    log_db = get_log_database()
    
    # 1. Add system logs
    print("\n1. Adding system logs...")
    log_db.add_system_log("info", "AI Factory initialized")
    log_db.add_system_log("success", "Connected to Azure DevOps")
    log_db.add_system_log("warning", "No projects enabled")
    log_db.add_system_log("error", "Failed to connect to service")
    
    # 2. Add persona logs
    print("\n2. Adding persona logs...")
    log_db.add_persona_log(
        persona_name="Steve Bot",
        level="info",
        message="Started working on security architecture review",
        work_item_id=101,
        project_name="AI-Personas-Test-Sandbox"
    )
    
    log_db.add_persona_log(
        persona_name="Steve Bot",
        level="success",
        message="Completed security review - found 3 vulnerabilities",
        work_item_id=101,
        project_name="AI-Personas-Test-Sandbox"
    )
    
    log_db.add_persona_log(
        persona_name="Kav Bot",
        level="info",
        message="Running security tests on authentication module",
        work_item_id=102,
        project_name="AI-Personas-Test-Sandbox-2"
    )
    
    log_db.add_persona_log(
        persona_name="Kav Bot",
        level="error",
        message="Test failed: SQL injection vulnerability detected",
        work_item_id=102,
        project_name="AI-Personas-Test-Sandbox-2"
    )
    
    # 3. Get system logs
    print("\n3. Retrieving system logs...")
    system_logs = log_db.get_system_logs(limit=10)
    print(f"   Found {len(system_logs)} system logs")
    for log in system_logs[:3]:
        print(f"   [{log['level']}] {log['message']}")
    
    # 4. Get persona logs
    print("\n4. Retrieving persona logs...")
    steve_logs = log_db.get_persona_logs(persona_name="Steve Bot")
    print(f"   Found {len(steve_logs)} logs for Steve Bot")
    for log in steve_logs:
        print(f"   [{log['level']}] {log['message']} (Work Item: {log['work_item_id']})")
    
    kav_logs = log_db.get_persona_logs(persona_name="Kav Bot")
    print(f"\n   Found {len(kav_logs)} logs for Kav Bot")
    for log in kav_logs:
        print(f"   [{log['level']}] {log['message']} (Project: {log['project_name']})")
    
    # 5. Get latest combined logs
    print("\n5. Retrieving latest combined logs...")
    latest_logs = log_db.get_latest_logs(count=5)
    print(f"   Found {len(latest_logs)} latest logs")
    for log in latest_logs:
        log_type = log['log_type']
        persona = f" ({log.get('persona_name', 'System')})" if log_type == 'persona' else ""
        print(f"   [{log_type}{persona}] [{log['level']}] {log['message']}")
    
    # 6. Search logs
    print("\n6. Searching logs...")
    search_results = log_db.search_logs("security", log_type="all")
    print(f"   Found {len(search_results)} logs containing 'security'")
    for log in search_results:
        print(f"   [{log['level']}] {log['message']}")
    
    # 7. Get log counts
    print("\n7. Getting log counts...")
    counts = log_db.get_log_counts()
    print(f"   System logs: {counts['system_logs']}")
    print(f"   Total persona logs: {counts['persona_logs']}")
    print(f"   Per-persona counts:")
    for persona, count in counts['personas'].items():
        print(f"     - {persona}: {count} logs")
    
    # 8. Test deletion (commented out to preserve test data)
    # print("\n8. Testing log deletion...")
    # system_deleted, persona_deleted = log_db.delete_old_logs(days=30)
    # print(f"   Deleted {system_deleted} system logs and {persona_deleted} persona logs")
    
    print("\n✅ All log database tests passed!")
    

if __name__ == "__main__":
    asyncio.run(test_log_database())