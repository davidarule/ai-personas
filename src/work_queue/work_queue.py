"""
Simple work queue implementation for AI Factory
"""

import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
import uuid


class WorkQueue:
    """Simple in-memory work queue"""
    
    def __init__(self):
        self.items = []
        self._lock = None
        
    @property
    def lock(self):
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock
        
    async def add_item(self, item: Dict[str, Any]) -> str:
        """Add a work item to the queue"""
        async with self.lock:
            work_item = {
                "id": str(uuid.uuid4()),
                "created_at": datetime.now().isoformat(),
                "status": "pending",
                **item
            }
            self.items.append(work_item)
            return work_item["id"]
            
    async def get_next_item(self) -> Optional[Dict[str, Any]]:
        """Get the next pending work item"""
        async with self.lock:
            for item in self.items:
                if item["status"] == "pending":
                    item["status"] = "processing"
                    return item
            return None
            
    def size(self) -> int:
        """Get queue size (pending items only)"""
        return sum(1 for item in self.items if item["status"] == "pending")
        
    def get_all_items(self) -> List[Dict[str, Any]]:
        """Get all items in queue"""
        return self.items.copy()
        
    async def mark_complete(self, item_id: str):
        """Mark an item as complete"""
        async with self.lock:
            for item in self.items:
                if item["id"] == item_id:
                    item["status"] = "completed"
                    item["completed_at"] = datetime.now().isoformat()
                    break
                    
    async def mark_failed(self, item_id: str, error: str):
        """Mark an item as failed"""
        async with self.lock:
            for item in self.items:
                if item["id"] == item_id:
                    item["status"] = "failed"
                    item["error"] = error
                    item["failed_at"] = datetime.now().isoformat()
                    break