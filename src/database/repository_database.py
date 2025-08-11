#!/usr/bin/env python3
"""
Repository Database Module
Handles repository structure and branching configuration with version control
"""

import sqlite3
import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class RepositoryDatabase:
    """Manages repository structure and branching configuration in SQLite database"""
    
    def __init__(self, db_path: str = None):
        """Initialize the repository database
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use project root for database
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "repository.db"
        
        self.db_path = str(db_path)
        self._init_database()
        self._initialize_defaults()
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Repository structure table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repository_structure (
                    id INTEGER PRIMARY KEY,
                    structure TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Repository structure history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repository_structure_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    structure TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    change_notes TEXT
                )
            """)
            
            # Branching strategy table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS branching_strategy (
                    id INTEGER PRIMARY KEY,
                    strategy TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    version INTEGER DEFAULT 1,
                    is_active BOOLEAN DEFAULT TRUE
                )
            """)
            
            # Branching strategy history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS branching_strategy_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    strategy TEXT NOT NULL,
                    version INTEGER NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_by TEXT,
                    change_notes TEXT
                )
            """)
            
            # Create indexes for better performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_structure_history_version 
                ON repository_structure_history(version)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_branching_history_version 
                ON branching_strategy_history(version)
            """)
            
            conn.commit()
            logger.info(f"Repository database initialized at {self.db_path}")
    
    def _initialize_defaults(self):
        """Initialize default repository structure and branching strategy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if repository structure exists
            cursor.execute("SELECT COUNT(*) FROM repository_structure")
            structure_count = cursor.fetchone()[0]
            
            if structure_count == 0:
                # Default repository structure
                default_structure = """
/project-root/
├── src/
│   ├── api/               # API endpoints and services
│   ├── components/        # Reusable components
│   ├── features/          # Feature modules
│   ├── services/          # Business logic services
│   ├── database/          # Database modules
│   ├── utils/             # Utility functions
│   └── config/            # Configuration files
├── tests/
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   ├── e2e/               # End-to-end tests
│   └── fixtures/          # Test fixtures
├── docs/
│   ├── api/               # API documentation
│   ├── architecture/      # Architecture docs
│   ├── guides/            # User guides
│   └── decisions/         # ADRs
├── infrastructure/
│   ├── terraform/         # Infrastructure as Code
│   ├── kubernetes/        # K8s manifests
│   ├── docker/            # Docker configurations
│   └── scripts/           # Deployment scripts
├── .github/
│   ├── workflows/         # GitHub Actions
│   └── ISSUE_TEMPLATE/    # Issue templates
├── outputs/               # Generated artifacts
│   └── personas/          # Persona outputs
├── config/                # Application config
├── logs/                  # Application logs
└── README.md              # Project documentation
"""
                
                cursor.execute("""
                    INSERT INTO repository_structure (structure, version)
                    VALUES (?, 1)
                """, (default_structure.strip(),))
                
                # Add to history
                cursor.execute("""
                    INSERT INTO repository_structure_history 
                    (structure, version, created_by, change_notes)
                    VALUES (?, 1, 'system', 'Initial default structure')
                """, (default_structure.strip(),))
            
            # Check if branching strategy exists
            cursor.execute("SELECT COUNT(*) FROM branching_strategy")
            branching_count = cursor.fetchone()[0]
            
            if branching_count == 0:
                # Default branching strategy
                default_branching = """
## Branch Naming Convention

- main                     # Production-ready code
- develop                  # Integration branch
- feature/*               # New features
- bugfix/*                # Bug fixes
- hotfix/*                # Emergency fixes
- release/*               # Release preparation
- persona/*               # Persona-specific work

## Branch Patterns

### Feature Branches
- feature/TASK-ID-description
- Example: feature/WI-123-add-authentication

### Bugfix Branches
- bugfix/BUG-ID-description
- Example: bugfix/BUG-456-fix-login-error

### Hotfix Branches
- hotfix/INCIDENT-ID-description
- Example: hotfix/INC-789-critical-security-patch

### Persona Work Branches
- persona/PERSONA-NAME/TASK-ID-description
- Example: persona/steve/WI-123-security-review

## Branch Policies

1. All changes must go through pull requests
2. Require code reviews before merging
3. Run automated tests on all branches
4. Protect main and develop branches
5. Delete branches after merging
6. Rebase feature branches regularly
7. Tag releases with semantic versioning
"""
                
                cursor.execute("""
                    INSERT INTO branching_strategy (strategy, version)
                    VALUES (?, 1)
                """, (default_branching.strip(),))
                
                # Add to history
                cursor.execute("""
                    INSERT INTO branching_strategy_history 
                    (strategy, version, created_by, change_notes)
                    VALUES (?, 1, 'system', 'Initial default branching strategy')
                """, (default_branching.strip(),))
            
            conn.commit()
    
    # Repository Structure Methods
    
    def get_repository_structure(self) -> Dict[str, Any]:
        """Get the current active repository structure"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, structure, version, created_at, updated_at
                FROM repository_structure
                WHERE is_active = TRUE
                ORDER BY id DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'structure': row[1],
                    'version': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                }
            return None
    
    def update_repository_structure(self, structure: str, created_by: str = None, 
                                  change_notes: str = None) -> Dict[str, Any]:
        """Update the repository structure and increment version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current version
            current = self.get_repository_structure()
            new_version = (current['version'] if current else 0) + 1
            
            if current:
                # Update existing record
                cursor.execute("""
                    UPDATE repository_structure
                    SET structure = ?, version = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE is_active = TRUE
                """, (structure, new_version))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO repository_structure (structure, version)
                    VALUES (?, ?)
                """, (structure, new_version))
            
            # Add to history
            cursor.execute("""
                INSERT INTO repository_structure_history 
                (structure, version, created_by, change_notes)
                VALUES (?, ?, ?, ?)
            """, (structure, new_version, created_by, change_notes))
            
            conn.commit()
            
            return {
                'structure': structure,
                'version': new_version,
                'updated_at': datetime.now().isoformat()
            }
    
    def get_repository_structure_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get repository structure change history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, structure, version, created_at, created_by, change_notes
                FROM repository_structure_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row[0],
                    'structure': row[1],
                    'version': row[2],
                    'created_at': row[3],
                    'created_by': row[4] or 'unknown',
                    'change_notes': row[5] or ''
                })
            
            return history
    
    def get_repository_structure_by_version(self, version: int) -> Optional[Dict[str, Any]]:
        """Get a specific version of repository structure from history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, structure, version, created_at, created_by, change_notes
                FROM repository_structure_history
                WHERE version = ?
            """, (version,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'structure': row[1],
                    'version': row[2],
                    'created_at': row[3],
                    'created_by': row[4] or 'unknown',
                    'change_notes': row[5] or ''
                }
            return None
    
    # Branching Strategy Methods
    
    def get_branching_strategy(self) -> Dict[str, Any]:
        """Get the current active branching strategy"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, strategy, version, created_at, updated_at
                FROM branching_strategy
                WHERE is_active = TRUE
                ORDER BY id DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'strategy': row[1],
                    'version': row[2],
                    'created_at': row[3],
                    'updated_at': row[4]
                }
            return None
    
    def update_branching_strategy(self, strategy: str, created_by: str = None, 
                                change_notes: str = None) -> Dict[str, Any]:
        """Update the branching strategy and increment version"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get current version
            current = self.get_branching_strategy()
            new_version = (current['version'] if current else 0) + 1
            
            if current:
                # Update existing record
                cursor.execute("""
                    UPDATE branching_strategy
                    SET strategy = ?, version = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE is_active = TRUE
                """, (strategy, new_version))
            else:
                # Insert new record
                cursor.execute("""
                    INSERT INTO branching_strategy (strategy, version)
                    VALUES (?, ?)
                """, (strategy, new_version))
            
            # Add to history
            cursor.execute("""
                INSERT INTO branching_strategy_history 
                (strategy, version, created_by, change_notes)
                VALUES (?, ?, ?, ?)
            """, (strategy, new_version, created_by, change_notes))
            
            conn.commit()
            
            return {
                'strategy': strategy,
                'version': new_version,
                'updated_at': datetime.now().isoformat()
            }
    
    def get_branching_strategy_history(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get branching strategy change history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, strategy, version, created_at, created_by, change_notes
                FROM branching_strategy_history
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'id': row[0],
                    'strategy': row[1],
                    'version': row[2],
                    'created_at': row[3],
                    'created_by': row[4] or 'unknown',
                    'change_notes': row[5] or ''
                })
            
            return history
    
    def get_branching_strategy_by_version(self, version: int) -> Optional[Dict[str, Any]]:
        """Get a specific version of branching strategy from history"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, strategy, version, created_at, created_by, change_notes
                FROM branching_strategy_history
                WHERE version = ?
            """, (version,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'strategy': row[1],
                    'version': row[2],
                    'created_at': row[3],
                    'created_by': row[4] or 'unknown',
                    'change_notes': row[5] or ''
                }
            return None