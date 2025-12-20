"""
DashboardTab
--------------
Lightweight dashboard tab that shows quick system stats, recent activity,
and quick actions. This module provides a small, read-only view used by
the main window to give the user an overview of the application's
status and quick operations.

This file contains UI construction code (PyQt5) and small helper methods
to update widgets periodically. It deliberately avoids heavy logic and
delegates real work (scan, cleanup, duplicate finding) back to core
modules via the `logger` and later integrations.
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QGroupBox, QProgressBar, QPushButton,
                             QFrame, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap
import psutil
import os


class DashboardTab(QWidget):
    def __init__(self, settings, logger):
        # Initialize QWidget and store dependencies
        # `settings` is a SettingsManager-like object and `logger` is the
        # application's Logger instance (used to read recent activity).
        super().__init__()
        self.settings = settings
        self.logger = logger

        # Build the UI controls and start periodic updates
        self.init_ui()
        self.start_monitoring()

    def init_ui(self):
        # Top-level vertical layout for the tab
        layout = QVBoxLayout(self)

        # Welcome banner (left: title, right: quick stats)
        welcome_frame = QFrame()
        welcome_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        welcome_layout = QHBoxLayout(welcome_frame)

        # Title label uses a larger font
        welcome_label = QLabel("Welcome to DeskTidy")
        welcome_label.setFont(QFont("Arial", 16, QFont.Bold))
        welcome_layout.addWidget(welcome_label)

        # Spacer pushes the quick stats to the right
        welcome_layout.addStretch()

        # Small label showing a compact overview (updated periodically)
        self.quick_stats = QLabel("")
        self.quick_stats.setFont(QFont("Arial", 10))
        welcome_layout.addWidget(self.quick_stats)

        layout.addWidget(welcome_frame)

        # Grid contains multiple groups: disk usage, recent activity, actions, stats
        grid = QGridLayout()

        # Disk usage group: progress bar + descriptive label
        disk_group = QGroupBox("Disk Usage")
        disk_layout = QVBoxLayout()

        self.disk_progress = QProgressBar()
        self.disk_progress.setTextVisible(True)
        disk_layout.addWidget(self.disk_progress)

        self.disk_label = QLabel("")
        disk_layout.addWidget(self.disk_label)

        disk_group.setLayout(disk_layout)
        grid.addWidget(disk_group, 0, 0)

        # Recent activity group: shows last few log events
        recent_group = QGroupBox("Recent Activity")
        recent_layout = QVBoxLayout()

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(150)
        recent_layout.addWidget(self.recent_list)

        recent_group.setLayout(recent_layout)
        grid.addWidget(recent_group, 0, 1)

        # Quick actions: buttons wired to small helper that logs intent
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QGridLayout()

        # Row 1
        self.scan_temp_btn = QPushButton("🔍 Scan Temp Files")
        # lambda used to pass a simple action identifier
        self.scan_temp_btn.clicked.connect(lambda: self.quick_action("scan_temp"))
        actions_layout.addWidget(self.scan_temp_btn, 0, 0)

        self.clean_cache_btn = QPushButton("🧹 Clean Cache")
        self.clean_cache_btn.clicked.connect(lambda: self.quick_action("clean_cache"))
        actions_layout.addWidget(self.clean_cache_btn, 0, 1)

        # Row 2
        self.find_duplicates_btn = QPushButton("📊 Find Duplicates")
        self.find_duplicates_btn.clicked.connect(lambda: self.quick_action("find_duplicates"))
        actions_layout.addWidget(self.find_duplicates_btn, 1, 0)

        self.empty_trash_btn = QPushButton("🗑️ Empty Trash")
        self.empty_trash_btn.clicked.connect(lambda: self.quick_action("empty_trash"))
        actions_layout.addWidget(self.empty_trash_btn, 1, 1)

        actions_group.setLayout(actions_layout)
        grid.addWidget(actions_group, 1, 0)

        # Statistics group: summary text about cleanups (placeholder values)
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()

        self.stats_label = QLabel("")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        stats_group.setLayout(stats_layout)
        grid.addWidget(stats_group, 1, 1)

        layout.addLayout(grid)

        # Scheduled cleanups area (simple placeholder UI)
        schedule_group = QGroupBox("Scheduled Cleanups")
        schedule_layout = QVBoxLayout()

        schedule_info = QLabel("No scheduled cleanups")
        schedule_layout.addWidget(schedule_info)

        schedule_btn = QPushButton("⚙️ Schedule New Cleanup")
        schedule_layout.addWidget(schedule_btn)

        schedule_group.setLayout(schedule_layout)
        layout.addWidget(schedule_group)

        # Push everything to the top and leave flexible space at the bottom
        layout.addStretch()

    def start_monitoring(self):
        # Create a QTimer that fires periodically to refresh the UI elements
        # (disk usage, quick stats, recent activity). Interval is 5000ms.
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(5000)

        # Do an immediate update so the UI shows values on open
        self.update_system_info()
        self.update_recent_activity()

    def update_system_info(self):
        # Update the disk and memory stats using psutil. This is wrapped in a
        # try/except because psutil may raise on some platforms or in rare
        # error conditions and we do not want the UI timer to crash.
        try:
            # Use root path for overall disk stats; on Windows this returns
            # stats for the current drive. For a multi-drive app you would
            # compute per-drive usage instead.
            disk = psutil.disk_usage('/')
            used_percent = disk.percent
            used_gb = disk.used / (1024 ** 3)
            total_gb = disk.total / (1024 ** 3)

            # Progress bar shows percent used, label gives human-friendly sizes
            self.disk_progress.setValue(int(used_percent))
            self.disk_label.setText(
                f"Used: {used_gb:.1f} GB / {total_gb:.1f} GB\n"
                f"Free: {disk.free / (1024 ** 3):.1f} GB"
            )

            # Quick stats shows a compact line for disk and memory use
            self.quick_stats.setText(
                f"Disk: {used_percent}% | Memory: {psutil.virtual_memory().percent}%"
            )

            # Placeholder statistics text; the real values would be computed
            # from the application's logs or disk analyzer results.
            stats_text = (
                f"📁 Files cleaned today: 0\n"
                f"💾 Space recovered: 0 MB\n"
                f"⏱️ Last cleanup: Never\n"
                f"✅ Status: Ready"
            )
            self.stats_label.setText(stats_text)

        except Exception as e:
            # Log the error to console; in a production app send this to the
            # application's Logger so it is visible in the logs tab.
            print(f"Error updating system info: {e}")

    def update_recent_activity(self):
        self.recent_list.clear()
        # Query the logger for the most recent events. The logger returns
        # structured dicts with keys like 'timestamp', 'action', 'details'.
        recent_logs = self.logger.get_logs(limit=5)

        for log in recent_logs:
            # Format time and a short preview of the details
            time_str = log['timestamp'].strftime("%H:%M")
            text = f"{time_str} - {log['action']}: {log['details'][:30]}..."

            item = QListWidgetItem(text)

            # Color-code items by action or status for easier scanning
            if log.get('action') == 'Deletion':
                item.setForeground(QColor('#e74c3c'))
            elif log.get('action') == 'Preview':
                item.setForeground(QColor('#3498db'))
            elif log.get('status') == 'Failed':
                item.setForeground(QColor('#f39c12'))

            self.recent_list.addItem(item)

    def quick_action(self, action):
        # These quick actions are UI shortcuts that currently only log an
        # intent. The actual implementations should call into core services
        # (e.g. FileOperations.find_duplicates, Cleaner.clean_cache, ...).
        if action == "scan_temp":
            self.logger.log_action("Quick Action", "Scanned temporary files")
            # TODO: call a temp-file scanner and show results in a preview

        elif action == "clean_cache":
            self.logger.log_action("Quick Action", "Cleaned cache")
            # TODO: perform cache cleaning (browser caches, app caches)

        elif action == "find_duplicates":
            self.logger.log_action("Quick Action", "Started duplicate finder")
            # TODO: trigger the duplicate finder (potentially long-running)

        elif action == "empty_trash":
            self.logger.log_action("Quick Action", "Emptied trash")
            # TODO: securely empty recycle bin / trash across platforms

        # Refresh the recent activity widget to show the new log entry
        self.update_recent_activity()