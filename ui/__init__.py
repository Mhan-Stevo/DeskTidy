"""
UI module for FileCleaner Pro application.
Contains all user interface components.
"""

from .main_window import MainWindow
from .tabs.file_cleaner_tab import FileCleanerTab
from .tabs.settings_tab import SettingsTab
from .tabs.logs_tab import LogsTab
from .components.folder_chooser import FolderChooser
from .components.preview_panel import PreviewPanel

__all__ = [
    'MainWindow',
    'FileCleanerTab',
    'SettingsTab',
    'LogsTab',
    'FolderChooser',
    'PreviewPanel'
]