"""Core package exports.

This module re-exports the main classes from the `core` package so
consumers can import from `core` directly (e.g. `from core import Logger`).
"""

# Import core components so they are available at package level
from .cleaner import FileCleaner
from .settings_manager import SettingsManager
from .logger import Logger
from .file_ops import FileOperations
from .rules_engine import RulesEngine
from .batch_processor import BatchProcessor
from .disk_analyzer import DiskAnalyzer
from .scheduler import Scheduler

# Define the public API for `from core import *`
__all__ = [
    'FileCleaner',
    'SettingsManager',
    'Logger',
    'FileOperations',
    'RulesEngine',
    'BatchProcessor',
    'DiskAnalyzer',
    'Scheduler'
]