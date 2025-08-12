#!/usr/bin/env python3
"""
Agent Settings Database - Persistent storage for AI provider configurations
Stores provider settings, API keys (encrypted), model selections, and custom providers
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class AgentsDatabase:
    """Manages agent provider configurations and settings in SQLite"""
    
    def __init__(self, db_path: str = "database/agents.db"):
        """Initialize the agents database
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Provider configurations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS provider_configs (
                    provider_id TEXT PRIMARY KEY,
                    provider_name TEXT NOT NULL,
                    enabled BOOLEAN DEFAULT 0,
                    has_api_key BOOLEAN DEFAULT 0,
                    api_key_hint TEXT,  -- Store last 4 chars for UI display
                    selected_models TEXT,  -- JSON array of model IDs
                    is_custom BOOLEAN DEFAULT 0,
                    description TEXT,
                    models_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Custom provider models table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_models (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    description TEXT,
                    capabilities TEXT,  -- JSON array of capabilities
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (provider_id) REFERENCES provider_configs(provider_id) ON DELETE CASCADE,
                    UNIQUE(provider_id, model_id)
                )
            ''')
            
            # Agent settings history for audit trail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    change_type TEXT NOT NULL,  -- 'provider_update', 'model_selection', etc.
                    provider_id TEXT,
                    old_value TEXT,  -- JSON
                    new_value TEXT,  -- JSON
                    changed_by TEXT DEFAULT 'system',
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_provider_enabled ON provider_configs(enabled)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_custom_models_provider ON custom_models(provider_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_timestamp ON settings_history(changed_at DESC)')
            
            conn.commit()
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all agent settings including providers and custom configurations
        
        Returns:
            Dictionary with providers and customProviders keys
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get all provider configurations
                cursor.execute('''
                    SELECT provider_id, provider_name, enabled, has_api_key, 
                           api_key_hint, selected_models, is_custom, description, models_url
                    FROM provider_configs
                    ORDER BY is_custom, provider_id
                ''')
                
                providers = {}
                custom_providers = []
                
                for row in cursor.fetchall():
                    provider_data = {
                        'enabled': bool(row['enabled']),
                        'hasApiKey': bool(row['has_api_key']),
                        'apiKeyHint': row['api_key_hint'],
                        'models': json.loads(row['selected_models'] or '[]')
                        # Note: Never return actual API keys in GET requests
                    }
                    
                    if row['is_custom']:
                        # Add custom provider info
                        custom_provider = {
                            'id': row['provider_id'],
                            'name': row['provider_name'],
                            'description': row['description'],
                            'modelsUrl': row['models_url'],
                            'models': []
                        }
                        
                        # Get custom models for this provider
                        cursor.execute('''
                            SELECT model_id, model_name, description, capabilities
                            FROM custom_models
                            WHERE provider_id = ?
                            ORDER BY model_name
                        ''', (row['provider_id'],))
                        
                        for model_row in cursor.fetchall():
                            custom_provider['models'].append({
                                'id': model_row['model_id'],
                                'name': model_row['model_name'],
                                'description': model_row['description'],
                                'capabilities': json.loads(model_row['capabilities'] or '[]')
                            })
                        
                        custom_providers.append(custom_provider)
                    
                    providers[row['provider_id']] = provider_data
                
                return {
                    'providers': providers,
                    'customProviders': custom_providers
                }
                
        except Exception as e:
            logger.error(f"Error getting agent settings: {str(e)}")
            return {'providers': {}, 'customProviders': []}
    
    def update_settings(self, settings: Dict[str, Any]) -> bool:
        """Update agent settings
        
        Args:
            settings: Dictionary containing providers and customProviders
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Start transaction
                cursor.execute('BEGIN TRANSACTION')
                
                # Update providers
                if 'providers' in settings:
                    for provider_id, config in settings['providers'].items():
                        # Check if provider exists
                        cursor.execute('SELECT provider_id FROM provider_configs WHERE provider_id = ?', (provider_id,))
                        exists = cursor.fetchone() is not None
                        
                        if exists:
                            # Update existing provider
                            cursor.execute('''
                                UPDATE provider_configs
                                SET enabled = ?, has_api_key = ?, api_key_hint = ?, 
                                    selected_models = ?, updated_at = CURRENT_TIMESTAMP
                                WHERE provider_id = ?
                            ''', (
                                config.get('enabled', False),
                                config.get('hasApiKey', False),
                                config.get('apiKeyHint', '') if config.get('apiKeyHint') else '',
                                json.dumps(config.get('models', [])),
                                provider_id
                            ))
                        else:
                            # Insert new provider (built-in)
                            cursor.execute('''
                                INSERT INTO provider_configs 
                                (provider_id, provider_name, enabled, has_api_key, api_key_hint, selected_models, is_custom)
                                VALUES (?, ?, ?, ?, ?, ?, 0)
                            ''', (
                                provider_id,
                                provider_id.title(),  # Use title case for built-in providers
                                config.get('enabled', False),
                                config.get('hasApiKey', False),
                                config.get('apiKeyHint', '') if config.get('apiKeyHint') else '',
                                json.dumps(config.get('models', []))
                            ))
                        
                        # Log the change
                        self._log_change(cursor, 'provider_update', provider_id, None, config)
                
                # Update custom providers
                if 'customProviders' in settings:
                    # Get existing custom provider IDs
                    cursor.execute('SELECT provider_id FROM provider_configs WHERE is_custom = 1')
                    existing_custom_ids = {row[0] for row in cursor.fetchall()}
                    
                    new_custom_ids = {p['id'] for p in settings['customProviders']}
                    
                    # Delete removed custom providers
                    for provider_id in existing_custom_ids - new_custom_ids:
                        cursor.execute('DELETE FROM provider_configs WHERE provider_id = ?', (provider_id,))
                        cursor.execute('DELETE FROM custom_models WHERE provider_id = ?', (provider_id,))
                        self._log_change(cursor, 'provider_delete', provider_id, None, None)
                    
                    # Update or insert custom providers
                    for provider in settings['customProviders']:
                        provider_id = provider['id']
                        
                        # Update or insert provider config
                        cursor.execute('''
                            INSERT OR REPLACE INTO provider_configs
                            (provider_id, provider_name, enabled, has_api_key, api_key_hint, 
                             selected_models, is_custom, description, models_url, updated_at)
                            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?, CURRENT_TIMESTAMP)
                        ''', (
                            provider_id,
                            provider['name'],
                            settings['providers'].get(provider_id, {}).get('enabled', False),
                            settings['providers'].get(provider_id, {}).get('hasApiKey', False),
                            settings['providers'].get(provider_id, {}).get('apiKeyHint', ''),
                            json.dumps(settings['providers'].get(provider_id, {}).get('models', [])),
                            provider.get('description', ''),
                            provider.get('modelsUrl', '')
                        ))
                        
                        # Update custom models
                        # First, delete existing models
                        cursor.execute('DELETE FROM custom_models WHERE provider_id = ?', (provider_id,))
                        
                        # Then insert new models
                        for model in provider.get('models', []):
                            cursor.execute('''
                                INSERT INTO custom_models
                                (provider_id, model_id, model_name, description, capabilities)
                                VALUES (?, ?, ?, ?, ?)
                            ''', (
                                provider_id,
                                model['id'],
                                model['name'],
                                model.get('description', ''),
                                json.dumps(model.get('capabilities', []))
                            ))
                
                # Commit transaction
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error updating agent settings: {str(e)}")
            return False
    
    def _log_change(self, cursor, change_type: str, provider_id: Optional[str], 
                    old_value: Any, new_value: Any):
        """Log a change to the settings history
        
        Args:
            cursor: Database cursor
            change_type: Type of change
            provider_id: Provider ID if applicable
            old_value: Previous value
            new_value: New value
        """
        try:
            cursor.execute('''
                INSERT INTO settings_history (change_type, provider_id, old_value, new_value)
                VALUES (?, ?, ?, ?)
            ''', (
                change_type,
                provider_id,
                json.dumps(old_value) if old_value is not None else None,
                json.dumps(new_value) if new_value is not None else None
            ))
        except Exception as e:
            logger.error(f"Error logging change: {str(e)}")
    
    def get_settings_history(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent settings changes
        
        Args:
            limit: Maximum number of history entries to return
            
        Returns:
            List of history entries
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM settings_history
                    ORDER BY changed_at DESC
                    LIMIT ?
                ''', (limit,))
                
                history = []
                for row in cursor.fetchall():
                    history.append({
                        'id': row['id'],
                        'changeType': row['change_type'],
                        'providerId': row['provider_id'],
                        'oldValue': json.loads(row['old_value']) if row['old_value'] else None,
                        'newValue': json.loads(row['new_value']) if row['new_value'] else None,
                        'changedBy': row['changed_by'],
                        'changedAt': row['changed_at']
                    })
                
                return history
                
        except Exception as e:
            logger.error(f"Error getting settings history: {str(e)}")
            return []


# Singleton instance
_agents_db_instance = None


def get_agents_database() -> AgentsDatabase:
    """Get the singleton agents database instance
    
    Returns:
        AgentsDatabase instance
    """
    global _agents_db_instance
    if _agents_db_instance is None:
        _agents_db_instance = AgentsDatabase()
    return _agents_db_instance