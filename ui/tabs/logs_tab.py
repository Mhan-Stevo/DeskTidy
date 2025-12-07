from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                             QTableWidgetItem, QPushButton, QFileDialog,
                             QComboBox, QDateEdit, QLabel, QHeaderView,
                             QMessageBox)
from PyQt5.QtCore import QDate, pyqtSlot
from PyQt5.QtGui import QColor
from datetime import datetime
import json
import os
import csv


class LogsTab(QWidget):
    def __init__(self, settings, logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self.logs = []
        self.init_ui()
        self.load_logs()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Filter controls
        filter_layout = QHBoxLayout()

        filter_layout.addWidget(QLabel("Filter by:"))

        self.filter_type = QComboBox()
        self.filter_type.addItems(["All", "Deletion", "Preview", "Error", "System"])
        self.filter_type.currentTextChanged.connect(self.apply_filters)
        filter_layout.addWidget(self.filter_type)

        filter_layout.addWidget(QLabel("Date range:"))

        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_from.dateChanged.connect(self.apply_filters)
        self.date_from.setCalendarPopup(True)
        filter_layout.addWidget(self.date_from)

        filter_layout.addWidget(QLabel("to"))

        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.dateChanged.connect(self.apply_filters)
        self.date_to.setCalendarPopup(True)
        filter_layout.addWidget(self.date_to)

        self.clear_filter_btn = QPushButton("Clear Filters")
        self.clear_filter_btn.clicked.connect(self.clear_filters)
        self.clear_filter_btn.setStyleSheet("""
            QPushButton {
                padding: 5px 15px;
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        filter_layout.addWidget(self.clear_filter_btn)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        # Stats label
        self.stats_label = QLabel("Total logs: 0")
        self.stats_label.setStyleSheet("font-weight: bold; color: #666;")
        layout.addWidget(self.stats_label)

        # Logs table
        self.logs_table = QTableWidget()
        self.logs_table.setColumnCount(5)
        self.logs_table.setHorizontalHeaderLabels([
            "Timestamp", "Action", "Details", "Files", "Status"
        ])
        header = self.logs_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        self.logs_table.setAlternatingRowColors(True)
        self.logs_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.logs_table.setSortingEnabled(True)
        layout.addWidget(self.logs_table)

        # Action buttons
        button_layout = QHBoxLayout()

        self.refresh_btn = QPushButton("🔄 Refresh")
        self.refresh_btn.clicked.connect(self.load_logs)
        self.refresh_btn.setMinimumHeight(35)
        button_layout.addWidget(self.refresh_btn)

        self.export_btn = QPushButton("📤 Export Logs")
        self.export_btn.clicked.connect(self.export_logs)
        self.export_btn.setMinimumHeight(35)
        button_layout.addWidget(self.export_btn)

        self.clear_btn = QPushButton("🗑️ Clear Logs")
        self.clear_btn.clicked.connect(self.clear_logs)
        self.clear_btn.setMinimumHeight(35)
        button_layout.addWidget(self.clear_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def load_logs(self):
        """Load logs from logger"""
        self.logs = self.logger.get_logs()
        self.apply_filters()
        self.stats_label.setText(f"Total logs: {len(self.logs)} | Filtered: {self.logs_table.rowCount()}")

    def display_logs(self, logs):
        self.logs_table.setRowCount(len(logs))

        for row, log in enumerate(logs):
            # Timestamp
            timestamp_item = QTableWidgetItem(log["timestamp"].strftime("%Y-%m-%d %H:%M:%S"))
            timestamp_item.setData(0, log["timestamp"])  # Store actual datetime for sorting
            self.logs_table.setItem(row, 0, timestamp_item)

            # Action with color coding
            action_item = QTableWidgetItem(log["action"])
            if log["action"] == "Deletion":
                action_item.setForeground(QColor("#e74c3c"))  # Red
                action_item.setText("🗑️ " + log["action"])
            elif log["action"] == "Preview":
                action_item.setForeground(QColor("#3498db"))  # Blue
                action_item.setText("🔍 " + log["action"])
            elif log["action"] == "Error":
                action_item.setForeground(QColor("#f39c12"))  # Orange
                action_item.setText("⚠️ " + log["action"])
            elif log["action"] == "System":
                action_item.setForeground(QColor("#95a5a6"))  # Gray
                action_item.setText("⚙️ " + log["action"])
            self.logs_table.setItem(row, 1, action_item)

            # Details
            details_item = QTableWidgetItem(log["details"])
            self.logs_table.setItem(row, 2, details_item)

            # Files
            files_item = QTableWidgetItem(str(log["files"]))
            files_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.logs_table.setItem(row, 3, files_item)

            # Status
            status_item = QTableWidgetItem(log["status"])
            if log["status"] == "Success":
                status_item.setForeground(QColor("#2ecc71"))  # Green
                status_item.setText("✅ " + log["status"])
            elif "Failed" in log["status"] or "Error" in log["status"]:
                status_item.setForeground(QColor("#e74c3c"))  # Red
                status_item.setText("❌ " + log["status"])
            else:
                status_item.setText("📝 " + log["status"])
            self.logs_table.setItem(row, 4, status_item)

    @pyqtSlot(dict)
    def on_new_log(self, log_entry):
        """Slot called when a new log is added"""
        # Add to logs list
        self.logs.insert(0, log_entry)  # Add at beginning (newest first)

        # Apply current filters
        self.apply_filters()

        # Update stats
        self.stats_label.setText(f"Total logs: {len(self.logs)} | Filtered: {self.logs_table.rowCount()}")

    def apply_filters(self):
        filter_type = self.filter_type.currentText()
        date_from = self.date_from.date().toPyDate()
        date_to = self.date_to.date().toPyDate()

        filtered_logs = []
        for log in self.logs:
            # Filter by type
            if filter_type != "All" and log["action"] != filter_type:
                continue

            # Filter by date
            log_date = log["timestamp"].date()
            if not (date_from <= log_date <= date_to):
                continue

            filtered_logs.append(log)

        self.display_logs(filtered_logs)

    def clear_filters(self):
        self.filter_type.setCurrentText("All")
        self.date_from.setDate(QDate.currentDate().addDays(-7))
        self.date_to.setDate(QDate.currentDate())
        self.apply_filters()

    def export_logs(self):
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Export Logs", "filecleaner_logs",
            "CSV Files (*.csv);;JSON Files (*.json);;Text Files (*.txt)"
        )

        if not file_path:
            return

        try:
            # Get currently filtered logs
            filtered_logs = []
            for i in range(self.logs_table.rowCount()):
                log = {
                    'timestamp': self.logs_table.item(i, 0).text(),
                    'action': self.logs_table.item(i, 1).text().replace("🗑️ ", "").replace("🔍 ", "").replace("⚠️ ",
                                                                                                             "").replace(
                        "⚙️ ", ""),
                    'details': self.logs_table.item(i, 2).text(),
                    'files': int(self.logs_table.item(i, 3).text()),
                    'status': self.logs_table.item(i, 4).text().replace("✅ ", "").replace("❌ ", "").replace("📝 ", "")
                }
                filtered_logs.append(log)

            if selected_filter == "JSON Files (*.json)":
                if not file_path.endswith('.json'):
                    file_path += '.json'

                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(filtered_logs, f, indent=2, ensure_ascii=False)

            elif selected_filter == "CSV Files (*.csv)":
                if not file_path.endswith('.csv'):
                    file_path += '.csv'

                with open(file_path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Timestamp', 'Action', 'Details', 'Files', 'Status'])
                    for log in filtered_logs:
                        writer.writerow([
                            log['timestamp'],
                            log['action'],
                            log['details'],
                            log['files'],
                            log['status']
                        ])
            else:  # Text file
                if not file_path.endswith('.txt'):
                    file_path += '.txt'

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("FileCleaner Pro - Activity Log\n")
                    f.write("=" * 50 + "\n\n")

                    for log in filtered_logs:
                        f.write(f"Timestamp: {log['timestamp']}\n")
                        f.write(f"Action:    {log['action']}\n")
                        f.write(f"Details:   {log['details']}\n")
                        f.write(f"Files:     {log['files']}\n")
                        f.write(f"Status:    {log['status']}\n")
                        f.write("-" * 50 + "\n")

            QMessageBox.information(self, "Export Successful",
                                    f"✅ Logs exported successfully!\n\n"
                                    f"File: {file_path}\n"
                                    f"Entries: {len(filtered_logs)}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error",
                                 f"❌ Failed to export logs:\n\n{str(e)}")

    def clear_logs(self):
        reply = QMessageBox.question(
            self, "Clear Logs",
            "Are you sure you want to clear all logs?\n"
            "This action cannot be undone and will delete all log history.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            self.logger.clear_logs()
            self.load_logs()
            QMessageBox.information(self, "Logs Cleared",
                                    "✅ All logs have been cleared successfully.")