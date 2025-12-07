from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                             QLabel, QGroupBox, QProgressBar, QPushButton,
                             QFrame, QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor, QPixmap
import psutil
import os


class DashboardTab(QWidget):
    def __init__(self, settings, logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self.init_ui()
        self.start_monitoring()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Welcome section
        welcome_frame = QFrame()
        welcome_frame.setFrameStyle(QFrame.Panel | QFrame.Raised)
        welcome_layout = QHBoxLayout(welcome_frame)

        welcome_label = QLabel("Welcome to FileCleaner Pro")
        welcome_label.setFont(QFont("Arial", 16, QFont.Bold))
        welcome_layout.addWidget(welcome_label)

        welcome_layout.addStretch()

        self.quick_stats = QLabel("")
        self.quick_stats.setFont(QFont("Arial", 10))
        welcome_layout.addWidget(self.quick_stats)

        layout.addWidget(welcome_frame)

        # System info grid
        grid = QGridLayout()

        # Disk usage widget
        disk_group = QGroupBox("Disk Usage")
        disk_layout = QVBoxLayout()

        self.disk_progress = QProgressBar()
        self.disk_progress.setTextVisible(True)
        disk_layout.addWidget(self.disk_progress)

        self.disk_label = QLabel("")
        disk_layout.addWidget(self.disk_label)

        disk_group.setLayout(disk_layout)
        grid.addWidget(disk_group, 0, 0)

        # Recent activity
        recent_group = QGroupBox("Recent Activity")
        recent_layout = QVBoxLayout()

        self.recent_list = QListWidget()
        self.recent_list.setMaximumHeight(150)
        recent_layout.addWidget(self.recent_list)

        recent_group.setLayout(recent_layout)
        grid.addWidget(recent_group, 0, 1)

        # Quick actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QGridLayout()

        # Row 1
        self.scan_temp_btn = QPushButton("🔍 Scan Temp Files")
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

        # Statistics
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()

        self.stats_label = QLabel("")
        self.stats_label.setWordWrap(True)
        stats_layout.addWidget(self.stats_label)

        stats_group.setLayout(stats_layout)
        grid.addWidget(stats_group, 1, 1)

        layout.addLayout(grid)

        # Scheduled tasks
        schedule_group = QGroupBox("Scheduled Cleanups")
        schedule_layout = QVBoxLayout()

        schedule_info = QLabel("No scheduled cleanups")
        schedule_layout.addWidget(schedule_info)

        schedule_btn = QPushButton("⚙️ Schedule New Cleanup")
        schedule_layout.addWidget(schedule_btn)

        schedule_group.setLayout(schedule_layout)
        layout.addWidget(schedule_group)

        layout.addStretch()

    def start_monitoring(self):
        # Update system info every 5 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_system_info)
        self.timer.start(5000)

        # Initial update
        self.update_system_info()
        self.update_recent_activity()

    def update_system_info(self):
        # Disk usage
        try:
            disk = psutil.disk_usage('/')
            used_percent = disk.percent
            used_gb = disk.used / (1024 ** 3)
            total_gb = disk.total / (1024 ** 3)

            self.disk_progress.setValue(int(used_percent))
            self.disk_label.setText(
                f"Used: {used_gb:.1f} GB / {total_gb:.1f} GB\n"
                f"Free: {disk.free / (1024 ** 3):.1f} GB"
            )

            # Update quick stats
            self.quick_stats.setText(
                f"Disk: {used_percent}% | Memory: {psutil.virtual_memory().percent}%"
            )

            # Update statistics
            stats_text = (
                f"📁 Files cleaned today: 0\n"
                f"💾 Space recovered: 0 MB\n"
                f"⏱️ Last cleanup: Never\n"
                f"✅ Status: Ready"
            )
            self.stats_label.setText(stats_text)

        except Exception as e:
            print(f"Error updating system info: {e}")

    def update_recent_activity(self):
        self.recent_list.clear()

        # Get recent logs
        recent_logs = self.logger.get_logs(limit=5)

        for log in recent_logs:
            time_str = log['timestamp'].strftime("%H:%M")
            text = f"{time_str} - {log['action']}: {log['details'][:30]}..."

            item = QListWidgetItem(text)

            if log['action'] == 'Deletion':
                item.setForeground(QColor('#e74c3c'))
            elif log['action'] == 'Preview':
                item.setForeground(QColor('#3498db'))
            elif log['status'] == 'Failed':
                item.setForeground(QColor('#f39c12'))

            self.recent_list.addItem(item)

    def quick_action(self, action):
        if action == "scan_temp":
            self.logger.log_action("Quick Action", "Scanned temporary files")
            # Implement temp file scanning

        elif action == "clean_cache":
            self.logger.log_action("Quick Action", "Cleaned cache")
            # Implement cache cleaning

        elif action == "find_duplicates":
            self.logger.log_action("Quick Action", "Started duplicate finder")
            # Implement duplicate finder

        elif action == "empty_trash":
            self.logger.log_action("Quick Action", "Emptied trash")
            # Implement trash emptying

        self.update_recent_activity()