#!/usr/bin/env python3
"""
Check workflow diagrams in the database
"""

import sqlite3
import json
from pathlib import Path

def check_diagrams():
    """Check what diagrams are stored in the database"""
    
    # Database path
    db_path = Path(__file__).parent / "workflow_diagrams.db"
    
    if not db_path.exists():
        print("❌ Database file not found at:", db_path)
        print("   The database should be created when the API starts")
        return
    
    print(f"✅ Database found at: {db_path}")
    print("-" * 60)
    
    # Connect to database
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Check all diagrams
    cursor.execute("""
        SELECT workflow_id, diagram_type, format, metadata, updated_at
        FROM workflow_diagrams
        ORDER BY workflow_id, diagram_type
    """)
    
    diagrams = cursor.fetchall()
    
    if not diagrams:
        print("❌ No diagrams found in database")
        return
    
    print(f"Found {len(diagrams)} diagrams in database:\n")
    
    # Group by workflow
    workflows = {}
    for diagram in diagrams:
        wf_id = diagram['workflow_id']
        if wf_id not in workflows:
            workflows[wf_id] = []
        workflows[wf_id].append(diagram)
    
    # Display results
    for wf_id, wf_diagrams in workflows.items():
        print(f"📁 Workflow: {wf_id}")
        for diagram in wf_diagrams:
            metadata = json.loads(diagram['metadata']) if diagram['metadata'] else {}
            print(f"   • {diagram['diagram_type']:<15} ({diagram['format']:<8}) - {metadata.get('title', 'No title')}")
        print()
    
    # Check for expected diagrams
    print("-" * 60)
    print("Verification:")
    
    expected = {
        'wf0': ['orchestration', 'interaction', 'raci'],
        'wf1': ['orchestration', 'interaction', 'raci'],
        'wf2': ['orchestration', 'interaction', 'raci']
    }
    
    all_good = True
    for wf_id, expected_types in expected.items():
        cursor.execute("""
            SELECT diagram_type FROM workflow_diagrams
            WHERE workflow_id = ?
        """, (wf_id,))
        
        actual_types = [row['diagram_type'] for row in cursor.fetchall()]
        
        if set(actual_types) == set(expected_types):
            print(f"✅ {wf_id}: All expected diagrams present")
        else:
            print(f"❌ {wf_id}: Missing diagrams")
            missing = set(expected_types) - set(actual_types)
            if missing:
                print(f"   Missing: {', '.join(missing)}")
            all_good = False
    
    print()
    if all_good:
        print("✅ All workflow diagrams are properly initialized!")
    else:
        print("❌ Some diagrams are missing. Try restarting the API.")
    
    conn.close()

if __name__ == "__main__":
    check_diagrams()