from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QTableWidget,
                             QTableWidgetItem, QLabel, QHeaderView)
from PyQt5.QtCore import Qt


class PreviewPanel(QWidget):
    """A panel to display a list of files and basic metadata in a table."""

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Vertical layout: title, table, summary label
        layout = QVBoxLayout(self)

        # Title label for the panel
        self.title_label = QLabel("File Preview")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(self.title_label)

        # Table used to show filename, size, modified date, and type
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels([
            "Filename", "Size", "Modified", "Type"
        ])
        # Make columns expand to fill available space
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        layout.addWidget(self.table)

        # Summary label shown below the table
        self.summary_label = QLabel("No files to display")
        layout.addWidget(self.summary_label)

    def display_files(self, files):
        """Populate the table with `files`, a list of metadata dicts."""
        self.table.setRowCount(len(files))

        for row, file in enumerate(files):
            # Filename cell
            self.table.setItem(row, 0, QTableWidgetItem(file['name']))

            # Size cell (human-readable)
            size_text = self.format_size(file['size'])
            self.table.setItem(row, 1, QTableWidgetItem(size_text))

            # Modified date cell formatted as a short timestamp
            mod_date = file['modified'].strftime("%Y-%m-%d %H:%M")
            self.table.setItem(row, 2, QTableWidgetItem(mod_date))

            # Type/Extension cell; fall back to 'None' if missing
            self.table.setItem(row, 3, QTableWidgetItem(file['extension'] or "None"))

        # Update the summary label with the number of displayed files
        self.summary_label.setText(f"Showing {len(files)} files")

    def format_size(self, size_bytes):
        """Convert bytes to a human readable string like '1.2 MB'."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"