"""
Log Database for AI Personas
Stores system and persona logs in SQLite for persistence
"""

import sqlite3
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class LogDatabase:
    """Manages log storage in SQLite database"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'database', 'logs.db')
        
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database tables"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # System logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Persona logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persona_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    persona_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    message TEXT NOT NULL,
                    work_item_id INTEGER,
                    project_name TEXT,
                    metadata TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp 
                ON system_logs(timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_persona_logs_persona 
                ON persona_logs(persona_name, timestamp DESC)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_persona_logs_timestamp 
                ON persona_logs(timestamp DESC)
            """)
            
            conn.commit()
            logger.info("Log database initialized")
    
    def _get_aest_timestamp(self) -> str:
        """Get current timestamp in Australian Eastern Time"""
        # Australian Eastern Time is UTC+10 (or UTC+11 during DST)
        # For simplicity, using UTC+10 as specified
        aest = timezone(timedelta(hours=10))
        now = datetime.now(aest)
        return now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] + ' +10:00'
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with proper error handling"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()
    
    def add_system_log(self, level: str, message: str, timestamp: str = None) -> int:
        """Add a system log entry"""
        if timestamp is None:
            timestamp = self._get_aest_timestamp()
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_logs (timestamp, level, message)
                VALUES (?, ?, ?)
            """, (timestamp, level.upper(), message))
            conn.commit()
            return cursor.lastrowid
    
    def add_persona_log(self, persona_name: str, level: str, message: str, 
                       timestamp: str = None, work_item_id: int = None,
                       project_name: str = None, metadata: Dict[str, Any] = None) -> int:
        """Add a persona log entry"""
        if timestamp is None:
            timestamp = self._get_aest_timestamp()
        
        metadata_json = json.dumps(metadata) if metadata else None
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO persona_logs 
                (persona_name, timestamp, level, message, work_item_id, project_name, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (persona_name, timestamp, level.upper(), message, work_item_id, project_name, metadata_json))
            conn.commit()
            return cursor.lastrowid
    
    def get_system_logs(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """Get system logs with pagination"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM system_logs
                ORDER BY timestamp DESC
                LIMIT ? OFFSET ?
            """, (limit, offset))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_persona_logs(self, persona_name: str = None, limit: int = 1000, 
                        offset: int = 0) -> List[Dict[str, Any]]:
        """Get persona logs, optionally filtered by persona name"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            if persona_name:
                cursor.execute("""
                    SELECT * FROM persona_logs
                    WHERE persona_name = ?
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """, (persona_name, limit, offset))
            else:
                cursor.execute("""
                    SELECT * FROM persona_logs
                    ORDER BY timestamp DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            
            logs = []
            for row in cursor.fetchall():
                log = dict(row)
                if log.get('metadata'):
                    log['metadata'] = json.loads(log['metadata'])
                logs.append(log)
            
            return logs
    
    def delete_old_logs(self, days: int):
        """Delete logs older than specified days - for backward compatibility"""
        return self.delete_old_logs_separate(days, days)
    
    def delete_old_logs_separate(self, system_days: int, persona_days: int):
        """Delete logs older than specified days with separate retention for system and persona logs"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete old system logs
            system_cutoff_date = datetime.now() - timedelta(days=system_days)
            system_cutoff_str = system_cutoff_date.isoformat()
            cursor.execute("""
                DELETE FROM system_logs
                WHERE timestamp < ?
            """, (system_cutoff_str,))
            system_deleted = cursor.rowcount
            
            # Delete old persona logs
            persona_cutoff_date = datetime.now() - timedelta(days=persona_days)
            persona_cutoff_str = persona_cutoff_date.isoformat()
            cursor.execute("""
                DELETE FROM persona_logs
                WHERE timestamp < ?
            """, (persona_cutoff_str,))
            persona_deleted = cursor.rowcount
            
            conn.commit()
            
            logger.info(f"Deleted {system_deleted} system logs older than {system_days} days and {persona_deleted} persona logs older than {persona_days} days")
            return system_deleted, persona_deleted
    
    def get_log_counts(self) -> Dict[str, int]:
        """Get counts of logs in database"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM system_logs")
            system_count = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM persona_logs")
            persona_count = cursor.fetchone()[0]
            
            # Get per-persona counts
            cursor.execute("""
                SELECT persona_name, COUNT(*) as count
                FROM persona_logs
                GROUP BY persona_name
            """)
            persona_counts = {row['persona_name']: row['count'] for row in cursor.fetchall()}
            
            return {
                "system_logs": system_count,
                "persona_logs": persona_count,
                "personas": persona_counts
            }
    
    def search_logs(self, query: str, log_type: str = "all", 
                   persona_name: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Search logs by message content"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            results = []
            
            if log_type in ["all", "system"]:
                cursor.execute("""
                    SELECT 'system' as log_type, * FROM system_logs
                    WHERE message LIKE ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """, (f"%{query}%", limit))
                results.extend([dict(row) for row in cursor.fetchall()])
            
            if log_type in ["all", "persona"]:
                if persona_name:
                    cursor.execute("""
                        SELECT 'persona' as log_type, * FROM persona_logs
                        WHERE message LIKE ? AND persona_name = ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """, (f"%{query}%", persona_name, limit))
                else:
                    cursor.execute("""
                        SELECT 'persona' as log_type, * FROM persona_logs
                        WHERE message LIKE ?
                        ORDER BY timestamp DESC
                        LIMIT ?
                    """, (f"%{query}%", limit))
                
                for row in cursor.fetchall():
                    log = dict(row)
                    if log.get('metadata'):
                        log['metadata'] = json.loads(log['metadata'])
                    results.append(log)
            
            return results
    
    def format_log_entry(self, log: Dict[str, Any]) -> str:
        """Format a log entry for display with fixed-width columns"""
        timestamp = log['timestamp']
        level = log['level'].ljust(8)  # Left-justify, pad to 8 chars
        
        # Determine source (SYSTEM or persona name)
        if log.get('log_type') == 'persona' or log.get('persona_name'):
            source = log.get('persona_name', 'Unknown')
        else:
            source = 'SYSTEM'
        
        # Truncate and pad source to 14 chars
        source = source[:14].ljust(14)
        
        message = log['message']
        
        return f"{timestamp}   {level}   {source}   {message}"
    
    def get_latest_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get the latest logs from both tables combined"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM (
                    SELECT 'system' as log_type, id, timestamp, level, message, 
                           NULL as persona_name, NULL as work_item_id, NULL as project_name
                    FROM system_logs
                    UNION ALL
                    SELECT 'persona' as log_type, id, timestamp, level, message,
                           persona_name, work_item_id, project_name
                    FROM persona_logs
                )
                ORDER BY timestamp DESC
                LIMIT ?
            """, (count,))
            
            return [dict(row) for row in cursor.fetchall()]


# Singleton instance
_log_db = None


def get_log_database() -> LogDatabase:
    """Get or create the log database instance"""
    global _log_db
    if _log_db is None:
        _log_db = LogDatabase()
    return _log_db