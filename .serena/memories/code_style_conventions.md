# AI Personas Code Style and Conventions

## Python Style Guidelines

### General Conventions
- **Python Version**: 3.12
- **Type Hints**: Used throughout (typing module)
- **Async/Await**: Heavy use of async patterns
- **Docstrings**: Triple quotes with description at class and method level

### File Structure
```python
"""
Module docstring explaining purpose
"""

import standard_library_modules
import third_party_modules
from typing import Dict, List, Any, Optional

from .local_modules import LocalClass

logger = logging.getLogger(__name__)


class ClassName:
    """Class docstring"""
    
    def __init__(self, param: str):
        """Initialize docstring"""
        self.param = param
```

### Naming Conventions
- **Classes**: PascalCase (e.g., `BaseProcessor`, `SteveProcessor`)
- **Functions/Methods**: snake_case (e.g., `process_work_item`, `_get_output_path`)
- **Private Methods**: Leading underscore (e.g., `_generate_threat_model`)
- **Constants**: UPPER_SNAKE_CASE
- **Files**: snake_case.py

### Async Patterns
```python
async def process_work_item(self, work_item: Any) -> Dict[str, Any]:
    """Process work item asynchronously"""
    result = await self._async_operation()
    return result
```

### Logging
- Use module-level logger: `logger = logging.getLogger(__name__)`
- Log levels: INFO for normal operations, ERROR for failures
- Include context in log messages

### Error Handling
- Try/except blocks with specific exceptions
- Log errors before re-raising
- Return meaningful error messages in result dicts