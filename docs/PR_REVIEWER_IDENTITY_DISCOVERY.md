
# Azure DevOps PR Reviewer Identity Discovery

## Problem
Azure DevOps uses different identity IDs for PR reviewer context vs Graph API Origin IDs.

## Discovery Process
1. **Graph API Origin IDs**: These are user IDs from `/_apis/graph/users`
   - Kav Bot Origin ID: eb61c9a5-9ebe-48da-be0e-56c608603dfb
   - Lachlan Bot Origin ID: 51f491b1-9c2d-4e4a-946e-982e33a35375

2. **PR Reviewer Identity IDs**: These are used in actual PR reviewer assignments
   - Kav Bot PR ID: 5d101cce-1cdd-624b-9853-b391d8185c92 ✅ (confirmed via manual addition)
   - Lachlan Bot PR ID: ??? (needs manual discovery)

## Solution Pattern
For each bot:
1. Manually add them as a reviewer through Azure DevOps web interface
2. Query the PR data via API to capture their PR-specific identity ID
3. Map email → PR identity ID in Steve Bot's processor
4. Use PR identity ID in API calls for automatic reviewer assignment

## API Pattern That Works
```python
reviewer_url = f"https://dev.azure.com/{org}/{project}/_apis/git/repositories/{repo_id}/pullrequests/{pr_id}/reviewers/{pr_identity_id}?api-version=7.1"

reviewer_data = {
    'vote': 0,
    'isRequired': True,  # or False
    'isFlagged': False
}

response = requests.put(reviewer_url, headers=headers, json=reviewer_data)
```

## Backup System
The file-based review task system already works as a reliable fallback.
    