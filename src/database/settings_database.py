#!/usr/bin/env python3
"""
Settings Database - Persistent storage for application settings including Azure DevOps PAT
Stores encrypted sensitive data like Personal Access Tokens
"""

import sqlite3
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.encryption_utils import get_encryption_manager, is_encryption_available, EncryptionError

logger = logging.getLogger(__name__)


class SettingsDatabase:
    """Manages application settings including encrypted PATs in SQLite"""
    
    def __init__(self, db_path: str = "database/settings.db"):
        """Initialize the settings database
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
        self._migrate_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Application settings table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS app_settings (
                    setting_key TEXT PRIMARY KEY,
                    setting_value TEXT,
                    setting_type TEXT DEFAULT 'string',  -- string, number, boolean, json
                    is_encrypted BOOLEAN DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Encrypted credentials table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS credentials (
                    credential_id TEXT PRIMARY KEY,
                    credential_name TEXT NOT NULL,
                    encrypted_value TEXT,
                    value_hint TEXT,  -- For display purposes (e.g., last 4 chars)
                    key_version INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Settings history for audit trail
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    setting_key TEXT NOT NULL,
                    old_value TEXT,
                    new_value TEXT,
                    changed_by TEXT DEFAULT 'system',
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_settings_key ON app_settings(setting_key)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_credentials_id ON credentials(credential_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_history_timestamp ON settings_history(changed_at DESC)')
            
            conn.commit()
    
    def _migrate_database(self):
        """Migrate database schema if needed"""
        # Currently no migrations needed for initial version
        pass
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value
        
        Args:
            key: Setting key
            default: Default value if not found
            
        Returns:
            Setting value or default
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT setting_value, setting_type 
                    FROM app_settings 
                    WHERE setting_key = ?
                ''', (key,))
                
                row = cursor.fetchone()
                if not row:
                    return default
                
                value, setting_type = row
                
                # Convert value based on type
                if setting_type == 'number':
                    return float(value) if '.' in value else int(value)
                elif setting_type == 'boolean':
                    return value.lower() == 'true'
                elif setting_type == 'json':
                    return json.loads(value)
                else:
                    return value
                    
        except Exception as e:
            logger.error(f"Error getting setting {key}: {str(e)}")
            return default
    
    def set_setting(self, key: str, value: Any, is_encrypted: bool = False) -> bool:
        """Set a setting value
        
        Args:
            key: Setting key
            value: Setting value
            is_encrypted: Whether this setting contains encrypted data
            
        Returns:
            True if successful
        """
        try:
            # Determine type
            if isinstance(value, bool):
                setting_type = 'boolean'
                value_str = 'true' if value else 'false'
            elif isinstance(value, (int, float)):
                setting_type = 'number'
                value_str = str(value)
            elif isinstance(value, (dict, list)):
                setting_type = 'json'
                value_str = json.dumps(value)
            else:
                setting_type = 'string'
                value_str = str(value)
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Get old value for history
                cursor.execute('SELECT setting_value FROM app_settings WHERE setting_key = ?', (key,))
                old_row = cursor.fetchone()
                old_value = old_row[0] if old_row else None
                
                # Insert or update setting
                cursor.execute('''
                    INSERT OR REPLACE INTO app_settings 
                    (setting_key, setting_value, setting_type, is_encrypted, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (key, value_str, setting_type, is_encrypted))
                
                # Log change
                if old_value != value_str:
                    cursor.execute('''
                        INSERT INTO settings_history 
                        (setting_key, old_value, new_value)
                        VALUES (?, ?, ?)
                    ''', (key, old_value, value_str))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error setting {key}: {str(e)}")
            return False
    
    def get_credential(self, credential_id: str) -> Optional[Dict[str, Any]]:
        """Get credential information (without decrypted value)
        
        Args:
            credential_id: Credential identifier
            
        Returns:
            Dictionary with credential info or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT credential_name, value_hint, created_at, updated_at
                    FROM credentials
                    WHERE credential_id = ?
                ''', (credential_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'id': credential_id,
                        'name': row['credential_name'],
                        'hint': row['value_hint'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error getting credential {credential_id}: {str(e)}")
            return None
    
    def set_credential(self, credential_id: str, credential_value: str, 
                      credential_name: Optional[str] = None) -> bool:
        """Set an encrypted credential
        
        Args:
            credential_id: Unique identifier for the credential
            credential_value: The credential value to encrypt
            credential_name: Human-readable name for the credential
            
        Returns:
            True if successful
        """
        try:
            if not is_encryption_available():
                logger.error("Cannot store credential - encryption not available")
                return False
            
            # Encrypt the credential
            encryption_manager = get_encryption_manager()
            encrypted_value, value_hint = encryption_manager.encrypt_api_key(
                credential_value, credential_id
            )
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO credentials
                    (credential_id, credential_name, encrypted_value, value_hint, 
                     key_version, updated_at)
                    VALUES (?, ?, ?, ?, 1, CURRENT_TIMESTAMP)
                ''', (
                    credential_id,
                    credential_name or credential_id,
                    encrypted_value,
                    value_hint
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error setting credential {credential_id}: {str(e)}")
            return False
    
    def get_decrypted_credential(self, credential_id: str) -> Optional[str]:
        """Get the decrypted credential value
        
        Args:
            credential_id: Credential identifier
            
        Returns:
            Decrypted credential or None
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT encrypted_value
                    FROM credentials
                    WHERE credential_id = ?
                ''', (credential_id,))
                
                row = cursor.fetchone()
                if not row or not row[0]:
                    return None
                
                if not is_encryption_available():
                    logger.error("Cannot decrypt credential - encryption not available")
                    return None
                
                # Decrypt the credential
                encryption_manager = get_encryption_manager()
                return encryption_manager.decrypt_api_key(row[0], credential_id)
                
        except Exception as e:
            logger.error(f"Error decrypting credential {credential_id}: {str(e)}")
            return None
    
    def delete_credential(self, credential_id: str) -> bool:
        """Delete a credential
        
        Args:
            credential_id: Credential identifier
            
        Returns:
            True if successful
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('DELETE FROM credentials WHERE credential_id = ?', (credential_id,))
                conn.commit()
                return cursor.rowcount > 0
                
        except Exception as e:
            logger.error(f"Error deleting credential {credential_id}: {str(e)}")
            return False
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all non-encrypted settings
        
        Returns:
            Dictionary of settings
        """
        try:
            settings = {}
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT setting_key, setting_value, setting_type
                    FROM app_settings
                    WHERE is_encrypted = 0
                ''')
                
                for key, value, setting_type in cursor.fetchall():
                    if setting_type == 'number':
                        settings[key] = float(value) if '.' in value else int(value)
                    elif setting_type == 'boolean':
                        settings[key] = value.lower() == 'true'
                    elif setting_type == 'json':
                        settings[key] = json.loads(value)
                    else:
                        settings[key] = value
            
            return settings
            
        except Exception as e:
            logger.error(f"Error getting all settings: {str(e)}")
            return {}


# Singleton instance
_settings_db_instance = None


def get_settings_database() -> SettingsDatabase:
    """Get the singleton settings database instance
    
    Returns:
        SettingsDatabase instance
    """
    global _settings_db_instance
    if _settings_db_instance is None:
        _settings_db_instance = SettingsDatabase()
    return _settings_db_instance