# AI Personas Test Sandbox

This repository is used for testing AI Personas' ability to:
- Create feature branches
- Commit generated artifacts
- Create pull requests
- Assign appropriate reviewers

## Repository Structure

```
/docs/
  /architecture/     # Architecture documents (Steve)
  /security/         # Security documents (Steve, Kav)
  /api/              # API documentation (Jordan, Puck)
  /testing/          # Test plans and reports (Kav)
  /design/           # UI/UX designs (Shaun, Matt)
  /deployment/       # DevOps documentation (Lachlan)
  /requirements/     # Requirements and specs (Laureen)
  /database/         # Database schemas (Moby)
```

## Workflow

1. AI Personas receive work items from Azure DevOps
2. Each persona creates a feature branch: `feature/wi-{id}-{persona}-{timestamp}`
3. Generated artifacts are committed to appropriate directories
4. Pull request is created with suggested reviewers
5. Review process ensures quality and compliance
