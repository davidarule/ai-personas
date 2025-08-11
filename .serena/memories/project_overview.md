# AI Personas Project Overview

## Purpose
The AI Personas project is a DevSecOps system that simulates different AI personas (bot personas) for software development tasks. It's designed to test Azure DevOps integration, Git workflows, and collaborative development.

## Key Features
- **13 AI Personas**: Each persona has specific skills and responsibilities
  - Dave, Brumbie, Ruley, Steve, Shaun, Matt, Jordan, Puck, Moby, Claude, Kav, Lachlan, Laureen
- **Azure DevOps Integration**: Work items, pull requests, code reviews
- **Security Focus**: DevSecOps transformation with security frameworks (NIST CSF, ISO 27001, etc.)
- **Git Workflow**: Automated branch creation, commits, PRs with reviewer assignment
- **Multi-Project Support**: Can handle multiple Azure DevOps projects

## Tech Stack
- **Language**: Python 3.12
- **Async Framework**: asyncio with aiohttp
- **Version Control**: Git with Azure DevOps
- **Testing**: pytest with pytest-asyncio
- **Code Quality**: black (formatter), flake8 (linter), mypy (type checker)
- **Dependencies**: See src/ai_personas.egg-info/requires.txt

## Current Status
- **Branch**: feature/wi-501-stevebot-20250804-054020
- **Focus**: Testing Steve persona (Security Architect)
- **DevSecOps Implementation**: Complete with 5 security frameworks