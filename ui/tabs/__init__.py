"""Tab package exports for the UI.

Re-exports each tab widget so callers can import them from `ui.tabs`.
"""

from .file_cleaner_tab import FileCleanerTab
from .settings_tab import SettingsTab
from .logs_tab import LogsTab
from .analysis_tab import AnalysisTab
from .dashboard_tab import DashboardTab

__all__ = [
    'FileCleanerTab',
    'SettingsTab',
    'LogsTab',
    'AnalysisTab',
    'DashboardTab'
]