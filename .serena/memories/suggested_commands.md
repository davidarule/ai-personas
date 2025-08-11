# AI Personas Development Commands

## Testing Commands
```bash
# Run all tests
pytest

# Run specific test file
pytest test_steve_processor.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run async tests
pytest -v test_enhanced_review_mechanism.py
```

## Code Quality Commands
```bash
# Format code with Black
black src/

# Check formatting without changing
black --check src/

# Lint with flake8
flake8 src/

# Type checking with mypy
mypy src/

# Run all quality checks
black src/ && flake8 src/ && mypy src/
```

## Git Commands
```bash
# Create feature branch
git checkout -b feature/wi-{work_item_id}-{persona}-{timestamp}

# Stage changes
git add -A

# Commit with message
git commit -m "feat: {description}"

# Push to remote
git push -u origin {branch_name}
```

## Running Specific Personas
```bash
# Test Steve processor
python test_steve_work_item_265.py

# Run persona review
python task_personas_review_pr.py

# Execute Kav review
python execute_kav_review.py
```

## System Commands
```bash
# Check Python version
python --version

# Install dependencies
pip install -r requirements.txt  # (if exists)
pip install -e .  # Install package in development mode

# Virtual environment
source venv/bin/activate  # or .venv/bin/activate

# List processes
ps aux | grep python

# Check disk space
df -h
```

## Azure DevOps Commands
```bash
# List users (custom script)
python list_azure_devops_users.py

# Create PR
python create_pr_with_pat.py

# Check PR status
python pr_review_status.py
```