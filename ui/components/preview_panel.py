from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QHeaderView)
from PyQt5.QtCore import Qt


class PreviewPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        self.title_label = QLabel("File Preview")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Filename", "Size", "Modified", "Type"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        self.summary_label = QLabel("No files to display")
        layout.addWidget(self.summary_label)

    def display_files(self, files):
        self.table.setRowCount(len(files))

        for row, file in enumerate(files):
            # Filename
            self.table.setItem(row, 0, QTableWidgetItem(file['name']))

            # Size
            size_text = self.format_size(file['size'])
            self.table.setItem(row, 1, QTableWidgetItem(size_text))

            # Modified date
            mod_date = file['modified'].strftime("%Y-%m-%d %H:%M")
            self.table.setItem(row, 2, QTableWidgetItem(mod_date))

            # Type/Extension
            self.table.setItem(row, 3, QTableWidgetItem(file['extension'] or "None"))

        self.summary_label.setText(f"Showing {len(files)} files")

    def format_size(self, size_bytes):
        """Convert bytes to human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"