#!/usr/bin/env python3
"""
Workflow Diagrams Database Module
Handles workflow diagram storage (orchestration, interaction, RACI matrix)
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class WorkflowDiagramsDatabase:
    """Manages workflow diagrams in SQLite database"""
    
    def __init__(self, db_path: str = None):
        """Initialize the workflow diagrams database
        
        Args:
            db_path: Path to SQLite database file. If None, uses default location.
        """
        if db_path is None:
            # Use project root for database
            project_root = Path(__file__).parent.parent.parent
            db_path = project_root / "workflow_diagrams.db"
        
        self.db_path = str(db_path)
        self._init_database()
        self._initialize_default_diagrams()
    
    def _init_database(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Workflow diagrams table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workflow_diagrams (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id TEXT NOT NULL,
                    diagram_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    format TEXT NOT NULL,
                    metadata TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(workflow_id, diagram_type)
                )
            """)
            
            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_workflow_diagrams_workflow 
                ON workflow_diagrams(workflow_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_workflow_diagrams_type 
                ON workflow_diagrams(diagram_type)
            """)
            
            conn.commit()
            logger.info(f"Workflow diagrams database initialized at {self.db_path}")
    
    def _initialize_default_diagrams(self):
        """Initialize default diagrams from files if they exist"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Check if we already have the feature development diagrams
            cursor.execute("""
                SELECT COUNT(*) FROM workflow_diagrams 
                WHERE workflow_id = 'wf0'
            """)
            count = cursor.fetchone()[0]
            
            if count == 0:
                # Load initialization data from files
                project_root = Path(__file__).parent.parent.parent
                
                # Load orchestration diagram
                orchestration_path = project_root / "src/workflows/diagrams/feature-dev-sequence_orchestration.mermaid"
                if orchestration_path.exists():
                    with open(orchestration_path, 'r') as f:
                        orchestration_content = f.read()
                    
                    self.save_diagram(
                        workflow_id='wf0',
                        diagram_type='orchestration',
                        content=orchestration_content,
                        format='mermaid',
                        metadata={
                            'title': 'Feature Development Orchestration',
                            'description': 'Shows workflow-to-workflow interactions'
                        }
                    )
                    logger.info("Loaded orchestration diagram for wf0-feature-development")
                
                # Load interaction diagram
                interaction_path = project_root / "src/workflows/diagrams/feature-dev-sequence_interaction.mermaid"
                if interaction_path.exists():
                    with open(interaction_path, 'r') as f:
                        interaction_content = f.read()
                    
                    self.save_diagram(
                        workflow_id='wf0',
                        diagram_type='interaction',
                        content=interaction_content,
                        format='mermaid',
                        metadata={
                            'title': 'Feature Development Persona Interactions',
                            'description': 'Shows persona and system interactions'
                        }
                    )
                    logger.info("Loaded interaction diagram for wf0-feature-development")
                
                # Load RACI matrix
                raci_path = project_root / "src/workflows/raci/feature-dev-raci-matrix.html"
                if raci_path.exists():
                    with open(raci_path, 'r') as f:
                        raci_content = f.read()
                    
                    self.save_diagram(
                        workflow_id='wf0',
                        diagram_type='raci',
                        content=raci_content,
                        format='html',
                        metadata={
                            'title': 'Feature Development RACI Matrix',
                            'description': 'Responsibility assignment matrix'
                        }
                    )
                    logger.info("Loaded RACI matrix for wf0-feature-development")
                
                # Load Bug Fix Workflow diagrams (wf1)
                # Check if we already have the bug fix diagrams
                cursor.execute("""
                    SELECT COUNT(*) FROM workflow_diagrams 
                    WHERE workflow_id = 'wf1'
                """)
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # Load orchestration diagram for bug fix
                    bugfix_orchestration_path = project_root / "src/workflows/diagrams/bugfix-orchestration-view.mermaid"
                    if bugfix_orchestration_path.exists():
                        with open(bugfix_orchestration_path, 'r') as f:
                            orchestration_content = f.read()
                        
                        self.save_diagram(
                            workflow_id='wf1',
                            diagram_type='orchestration',
                            content=orchestration_content,
                            format='mermaid',
                            metadata={
                                'title': 'Bug Fix Workflow Orchestration',
                                'description': 'Shows workflow-to-workflow interactions for bug fixes'
                            }
                        )
                        logger.info("Loaded orchestration diagram for wf1-bug-fix")
                    
                    # Load interaction diagram for bug fix
                    bugfix_interaction_path = project_root / "src/workflows/diagrams/bugfix-interaction-view.mermaid"
                    if bugfix_interaction_path.exists():
                        with open(bugfix_interaction_path, 'r') as f:
                            interaction_content = f.read()
                        
                        self.save_diagram(
                            workflow_id='wf1',
                            diagram_type='interaction',
                            content=interaction_content,
                            format='mermaid',
                            metadata={
                                'title': 'Bug Fix Persona Interactions',
                                'description': 'Shows persona and system interactions for bug fixes'
                            }
                        )
                        logger.info("Loaded interaction diagram for wf1-bug-fix")
                    
                    # Load RACI matrix for bug fix
                    bugfix_raci_path = project_root / "src/workflows/raci/bugfix-raci-matrix.html"
                    if bugfix_raci_path.exists():
                        with open(bugfix_raci_path, 'r') as f:
                            raci_content = f.read()
                        
                        self.save_diagram(
                            workflow_id='wf1',
                            diagram_type='raci',
                            content=raci_content,
                            format='html',
                            metadata={
                                'title': 'Bug Fix RACI Matrix',
                                'description': 'Responsibility assignment matrix for bug fixes'
                            }
                        )
                        logger.info("Loaded RACI matrix for wf1-bug-fix")
                
                # Load Hotfix Workflow diagrams (wf2)
                # Check if we already have the hotfix diagrams
                cursor.execute("""
                    SELECT COUNT(*) FROM workflow_diagrams 
                    WHERE workflow_id = 'wf2'
                """)
                count = cursor.fetchone()[0]
                
                if count == 0:
                    # Load orchestration diagram for hotfix
                    hotfix_orchestration_path = project_root / "src/workflows/diagrams/hotfix-orchestration-view.mermaid"
                    if hotfix_orchestration_path.exists():
                        with open(hotfix_orchestration_path, 'r') as f:
                            orchestration_content = f.read()
                        
                        self.save_diagram(
                            workflow_id='wf2',
                            diagram_type='orchestration',
                            content=orchestration_content,
                            format='mermaid',
                            metadata={
                                'title': 'Hotfix Workflow Orchestration',
                                'description': 'Shows workflow-to-workflow interactions for hotfixes'
                            }
                        )
                        logger.info("Loaded orchestration diagram for wf2-hotfix")
                    
                    # Load interaction diagram for hotfix
                    hotfix_interaction_path = project_root / "src/workflows/diagrams/hotfix-interaction-view.mermaid"
                    if hotfix_interaction_path.exists():
                        with open(hotfix_interaction_path, 'r') as f:
                            interaction_content = f.read()
                        
                        self.save_diagram(
                            workflow_id='wf2',
                            diagram_type='interaction',
                            content=interaction_content,
                            format='mermaid',
                            metadata={
                                'title': 'Hotfix Persona Interactions',
                                'description': 'Shows persona and system interactions for hotfixes'
                            }
                        )
                        logger.info("Loaded interaction diagram for wf2-hotfix")
                    
                    # Load RACI matrix for hotfix
                    hotfix_raci_path = project_root / "src/workflows/raci/hotfix-raci-matrix.html"
                    if hotfix_raci_path.exists():
                        with open(hotfix_raci_path, 'r') as f:
                            raci_content = f.read()
                        
                        self.save_diagram(
                            workflow_id='wf2',
                            diagram_type='raci',
                            content=raci_content,
                            format='html',
                            metadata={
                                'title': 'Hotfix RACI Matrix',
                                'description': 'Responsibility assignment matrix for hotfixes'
                            }
                        )
                        logger.info("Loaded RACI matrix for wf2-hotfix")
    
    def save_diagram(self, workflow_id: str, diagram_type: str, content: str,
                    format: str, metadata: Dict[str, Any] = None) -> int:
        """Save or update a workflow diagram"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            metadata_json = json.dumps(metadata) if metadata else '{}'
            
            # Use INSERT OR REPLACE to handle updates
            cursor.execute("""
                INSERT OR REPLACE INTO workflow_diagrams 
                (workflow_id, diagram_type, content, format, metadata, updated_at)
                VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (workflow_id, diagram_type, content, format, metadata_json))
            
            diagram_id = cursor.lastrowid
            conn.commit()
            
            return diagram_id
    
    def get_diagram(self, workflow_id: str, diagram_type: str) -> Optional[Dict[str, Any]]:
        """Get a specific workflow diagram"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, workflow_id, diagram_type, content, format, metadata,
                       created_at, updated_at
                FROM workflow_diagrams
                WHERE workflow_id = ? AND diagram_type = ?
            """, (workflow_id, diagram_type))
            
            row = cursor.fetchone()
            if row:
                result = dict(row)
                result['metadata'] = json.loads(result['metadata'])
                return result
            return None
    
    def get_workflow_diagrams(self, workflow_id: str) -> List[Dict[str, Any]]:
        """Get all diagrams for a workflow"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, workflow_id, diagram_type, content, format, metadata,
                       created_at, updated_at
                FROM workflow_diagrams
                WHERE workflow_id = ?
                ORDER BY diagram_type
            """, (workflow_id,))
            
            diagrams = []
            for row in cursor.fetchall():
                diagram = dict(row)
                diagram['metadata'] = json.loads(diagram['metadata'])
                diagrams.append(diagram)
            
            return diagrams
    
    def list_diagram_types(self, workflow_id: str) -> List[str]:
        """List available diagram types for a workflow"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT DISTINCT diagram_type
                FROM workflow_diagrams
                WHERE workflow_id = ?
                ORDER BY diagram_type
            """, (workflow_id,))
            
            return [row[0] for row in cursor.fetchall()]
    
    def delete_diagram(self, workflow_id: str, diagram_type: str) -> bool:
        """Delete a specific diagram"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM workflow_diagrams
                WHERE workflow_id = ? AND diagram_type = ?
            """, (workflow_id, diagram_type))
            
            conn.commit()
            return cursor.rowcount > 0
    
    def get_all_workflows_with_diagrams(self) -> List[Dict[str, Any]]:
        """Get a list of all workflows that have diagrams"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT workflow_id, 
                       COUNT(*) as diagram_count,
                       GROUP_CONCAT(diagram_type) as diagram_types
                FROM workflow_diagrams
                GROUP BY workflow_id
                ORDER BY workflow_id
            """)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'workflow_id': row['workflow_id'],
                    'diagram_count': row['diagram_count'],
                    'diagram_types': row['diagram_types'].split(',') if row['diagram_types'] else []
                })
            
            return results


# Singleton instance
_workflow_diagrams_db = None

def get_workflow_diagrams_database() -> WorkflowDiagramsDatabase:
    """Get the singleton workflow diagrams database instance"""
    global _workflow_diagrams_db
    if _workflow_diagrams_db is None:
        _workflow_diagrams_db = WorkflowDiagramsDatabase()
    return _workflow_diagrams_db