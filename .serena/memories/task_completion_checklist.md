# Task Completion Checklist

## After Each Code Change

### 1. Code Quality Checks
```bash
# Format code
black src/

# Lint code
flake8 src/

# Type check (if applicable)
mypy src/
```

### 2. Run Tests
```bash
# Run related tests
pytest test_file.py -v

# If tests fail, fix issues before continuing
```

### 3. Update Documentation
- Update any relevant .md files in docs/
- Update docstrings if method signatures changed
- Update README.md if major changes

### 4. Git Workflow
```bash
# Stage all changes
git add -A

# Commit with descriptive message
git commit -m "type: description

- Detail 1
- Detail 2

🤖 Generated with Claude Code"

# Push to remote
git push
```

### 5. Update Todo List
- Mark current task as completed
- Add any new tasks discovered
- Update task priorities if needed

### 6. Memory Updates
- Store any new patterns discovered
- Update project state if significant progress
- Document any blockers or issues

## Special Considerations

### For Security Changes (Steve, Kav, Lachlan)
- Ensure security documentation is updated
- Run security-specific tests if available
- Document any security implications

### For API Changes (Jordan, Puck)
- Update API documentation
- Ensure backward compatibility
- Update OpenAPI specs if applicable

### For Database Changes (Moby)
- Update schema documentation
- Consider migration scripts
- Test with existing data

### Before PR Creation
- Ensure all tests pass
- Code is formatted and linted
- Documentation is updated
- Commit messages are clear
- Branch is up to date with main