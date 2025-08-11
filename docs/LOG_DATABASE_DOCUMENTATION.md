# Log Database Documentation

## Overview

The AI Personas project now includes a comprehensive log database system that stores both system and persona logs persistently in SQLite. This enables full log history, search capabilities, and automatic cleanup.

## Features Implemented

### 1. Database Storage
- **SQLite Database**: Located at `.memory/logs.db`
- **Two Tables**:
  - `system_logs`: General system events
  - `persona_logs`: Persona-specific activities with work item tracking

### 2. Log Types

#### System Logs
- General factory operations
- Azure DevOps connections
- Configuration changes
- Errors and warnings

#### Persona Logs
- Work item processing activities
- Success/failure status
- Associated work item IDs
- Project information

### 3. API Endpoints

#### Get Logs
```
GET /api/logs?type={all|system|persona}&limit=100&persona={name}
```
- `type`: Filter by log type (default: all)
- `limit`: Number of logs to return (default: 100)
- `persona`: Filter by persona name (for persona logs)

#### Get Persona-Specific Logs
```
GET /api/personas/{persona_name}/logs?limit=100
```
- Returns logs for a specific persona

#### Delete Old Logs
```
POST /api/logs/cleanup
Body: { "days": 7 }
```
- Manually trigger deletion of logs older than specified days

### 4. Automatic Log Cleanup

- **Background Task**: Runs every 24 hours
- **Configurable Retention**: Set `logRetentionDays` in settings.json
- **Default**: 7 days
- **Automatic Deletion**: Removes logs older than retention period

### 5. Settings Configuration

Add to settings.json:
```json
{
  "orgUrl": "https://dev.azure.com/yourorg",
  "patToken": "your-pat-token",
  "logRetentionDays": 7,
  "savedAt": "2025-08-05T..."
}
```

## Database Schema

### system_logs Table
```sql
CREATE TABLE system_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### persona_logs Table
```sql
CREATE TABLE persona_logs (
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
```

## Usage Examples

### Python API Usage
```python
from database import get_log_database

log_db = get_log_database()

# Add system log
log_db.add_system_log("info", "Factory started")

# Add persona log
log_db.add_persona_log(
    persona_name="Steve Bot",
    level="success",
    message="Completed security review",
    work_item_id=101,
    project_name="AI-Personas-Test-Sandbox"
)

# Get logs
system_logs = log_db.get_system_logs(limit=50)
persona_logs = log_db.get_persona_logs(persona_name="Steve Bot")
latest_logs = log_db.get_latest_logs(count=100)

# Search logs
results = log_db.search_logs("security", log_type="all")

# Get counts
counts = log_db.get_log_counts()

# Delete old logs
system_deleted, persona_deleted = log_db.delete_old_logs(days=30)
```

## Benefits

1. **Persistent Storage**: Logs survive API restarts
2. **Search Capability**: Find logs by content
3. **Performance**: Indexed for fast queries
4. **Automatic Cleanup**: Prevents database growth
5. **Persona Tracking**: See what each persona has done
6. **Work Item Association**: Track logs by work item

## Migration Notes

- The API still maintains in-memory logs for backwards compatibility
- Both in-memory and database logs are populated simultaneously
- The database is created automatically on first use