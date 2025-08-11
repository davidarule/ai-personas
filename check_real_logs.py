#!/usr/bin/env python3
"""
Check REAL logs in the database - NO TEST DATA
"""

import sys
sys.path.insert(0, 'src')

from database import get_log_database


def check_real_logs():
    """Show real logs from the database"""
    
    log_db = get_log_database()
    
    print("=== REAL LOGS IN DATABASE ===\n")
    
    # Get actual system logs
    print("System Logs (latest 20):")
    system_logs = log_db.get_system_logs(limit=20)
    for log in system_logs:
        print(f"{log['timestamp']} [{log['level'].upper()}] {log['message']}")
    
    print(f"\nTotal system logs in database: {len(log_db.get_system_logs(limit=1000))}")
    
    # Check for logs containing "Factory started" or "Factory stopped"
    factory_logs = log_db.search_logs("Factory", log_type="system")
    print(f"\nFound {len(factory_logs)} logs about Factory start/stop")
    
    # Check for Azure DevOps error logs
    azure_logs = log_db.search_logs("Azure DevOps", log_type="system")
    print(f"Found {len(azure_logs)} logs about Azure DevOps")


if __name__ == "__main__":
    check_real_logs()