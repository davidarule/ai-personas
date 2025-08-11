# AI Personas Project Entrypoints

## Main Test Scripts (Root Level)

### Persona Testing
```bash
# Test Steve (Security Architect)
python test_steve_work_item_265.py
python test_steve_architecture_direct.py

# Test Review Mechanism
python test_enhanced_review_mechanism.py
python test_review_validation_simple.py

# Test Kav Review
python execute_kav_review.py
```

### PR Management
```bash
# Create PR with PAT
python create_pr_with_pat.py

# Create PR with Azure CLI
python create_pr_with_azure_cli.py

# Assign reviewers
python assign_reviewers_to_pr.py

# Check PR status
python pr_review_status.py
```

### Task Creation
```bash
# Create review tasks
python create_review_tasks_for_personas.py

# Create architecture task
python create_system_architecture_task.py

# Create Steve trivia task
python create_steve_trivia_architecture_task.py
```

### Utilities
```bash
# List Azure DevOps users
python list_azure_devops_users.py

# Check project access
python check_project_access.py

# Simulate PR reviews
python simulate_pr_reviews.py
```

## Running Patterns

### Async Scripts
Most scripts use asyncio and should be run directly:
```python
async def main():
    # Main logic
    pass

if __name__ == "__main__":
    asyncio.run(main())
```

### Configuration
Scripts typically read from:
- Environment variables for secrets
- test_config.json for Azure DevOps settings
- Hardcoded test values for development

### Common Parameters
- Work Item ID
- Azure DevOps Organization
- Project Name
- Repository Name
- Personal Access Token (PAT)