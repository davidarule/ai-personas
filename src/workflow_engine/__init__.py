"""
AI Personas Workflow Engine

A flexible workflow execution engine for AI personas to discover, load, validate,
and execute structured workflows defined in YAML/JSON format.
"""

from .loader import WorkflowLoader
from .parser import WorkflowParser
from .registry import WorkflowRegistry
from .context import WorkflowContext
from .executor import WorkflowExecutor

__all__ = [
    'WorkflowLoader',
    'WorkflowParser',
    'WorkflowRegistry',
    'WorkflowContext',
    'WorkflowExecutor'
]

__version__ = '1.0.0'