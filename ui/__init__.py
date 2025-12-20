"""UI package exports.

This module re-exports the main UI classes so consumers can import
from `ui` directly (e.g. `from ui import MainWindow`).
"""

from .main_window import MainWindow
from .tabs.file_cleaner_tab import FileCleanerTab
from .tabs.settings_tab import SettingsTab
from .tabs.logs_tab import LogsTab
from .components.folder_chooser import FolderChooser
from .components.preview_panel import PreviewPanel

# Public API for the ui package
__all__ = [
    'MainWindow',
    'FileCleanerTab',
    'SettingsTab',
    'LogsTab',
    'FolderChooser',
    'PreviewPanel'
]