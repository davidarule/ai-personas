#!/usr/bin/env python3
"""
Quick script to help identify remaining workflows to convert
"""

workflows = [
    {"id": "wf0", "name": "Feature Development Workflow", "status": "✓ completed"},
    {"id": "wf1", "name": "Bug Fix Workflow", "status": "✓ completed"},
    {"id": "wf2", "name": "Hotfix Workflow", "status": "✓ completed"},
    {"id": "wf3", "name": "Branch Creation Workflow", "status": "✓ completed"},
    {"id": "wf4", "name": "Code Commit Workflow", "status": "✓ completed"},
    {"id": "wf5", "name": "Pull Request Creation Workflow", "status": "✓ completed"},
    {"id": "wf6", "name": "Merge Workflow", "status": "✓ completed"},
    {"id": "wf7", "name": "Post-Merge Monitoring Workflow", "status": "pending"},
    {"id": "wf8", "name": "Conflict Resolution Workflow", "status": "pending"},
    {"id": "wf9", "name": "Rollback Workflow", "status": "pending"},
    {"id": "wf10", "name": "Work Item Update Workflow", "status": "pending"},
    {"id": "wf11", "name": "PR Readiness Check Workflow", "status": "pending"},
]

print("Workflow Conversion Status:")
print("-" * 50)
for wf in workflows:
    print(f"{wf['id']}: {wf['name']} - {wf['status']}")

print("\nRemaining workflows to convert:")
remaining = [wf for wf in workflows if wf['status'] == 'pending']
for wf in remaining:
    print(f"- {wf['id']}: {wf['name']}")