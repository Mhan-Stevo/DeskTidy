from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QFileDialog, QGroupBox, QProgressBar,
                             QMessageBox, QSplitter)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from ui.components.folder_chooser import FolderChooser
from ui.components.preview_panel import PreviewPanel
from core.cleaner import FileCleaner


class CleanerThread(QThread):
    """Run the file cleaning operation in a worker thread to keep UI responsive."""

    progress = pyqtSignal(int)  # emits integer progress percentage
    finished = pyqtSignal(dict)  # emits final result dict when done
    error = pyqtSignal(str)  # emits error messages

    def __init__(self, cleaner, rules):
        super().__init__()
        # Cleaner instance that performs the actual file operations
        self.cleaner = cleaner
        self.rules = rules

    def run(self):
        try:
            # The FileCleaner.clean_files method accepts a progress-like object
            result = self.cleaner.clean_files(self.rules, self.progress)
            self.finished.emit(result)
        except Exception as e:
            # Forward exceptions to the UI via the error signal
            self.error.emit(str(e))


class FileCleanerTab(QWidget):
    """Main tab widget that allows users to preview and clean files."""

    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.selected_folder = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection section using the FolderChooser component
        folder_group = QGroupBox("Folder Selection")
        folder_layout = QVBoxLayout()

        self.folder_chooser = FolderChooser()
        self.folder_chooser.folder_selected.connect(self.on_folder_selected)
        folder_layout.addWidget(self.folder_chooser)

        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)

        # Split view: preview on left, controls on right
        splitter = QSplitter(Qt.Horizontal)

        # Preview panel shows filtered files
        self.preview_panel = PreviewPanel()
        splitter.addWidget(self.preview_panel)

        # Control panel hosts stats, progress and action buttons
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)

        # Stats display
        self.stats_label = QLabel("No folder selected")
        self.stats_label.setWordWrap(True)
        control_layout.addWidget(self.stats_label)

        # Progress bar is hidden until an operation starts
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        control_layout.addWidget(self.progress_bar)

        # Preview button (disabled until a folder is chosen)
        self.preview_btn = QPushButton("🔍 Preview Files")
        self.preview_btn.clicked.connect(self.preview_files)
        self.preview_btn.setEnabled(False)
        self.preview_btn.setMinimumHeight(40)
        control_layout.addWidget(self.preview_btn)

        # Cleanup button
        self.clean_btn = QPushButton("🧹 Run Cleanup")
        self.clean_btn.clicked.connect(self.run_cleanup)
        self.clean_btn.setEnabled(False)
        self.clean_btn.setMinimumHeight(40)
        control_layout.addWidget(self.clean_btn)

        control_layout.addStretch()

        splitter.addWidget(control_panel)
        splitter.setSizes([800, 400])

        layout.addWidget(splitter)

    @pyqtSlot(str)
    def on_folder_selected(self, folder_path):
        # Save the selected folder and enable actions
        self.selected_folder = folder_path
        self.preview_btn.setEnabled(True)
        self.clean_btn.setEnabled(True)
        self.stats_label.setText(f"Selected folder: {folder_path}")

        # If the user enabled auto-preview in settings, run it immediately
        if self.settings.get("auto_preview", False):
            self.preview_files()

    def preview_files(self):
        # Show filtered files according to settings rules
        if not self.selected_folder:
            return

        cleaner = FileCleaner(self.selected_folder)
        files = cleaner.scan_files()

        # Apply rules from settings to determine which files match cleanup criteria
        rules = self.settings.get("rules", {})
        filtered_files = cleaner.filter_files(files, rules)

        # Display results in the preview panel and update stats
        self.preview_panel.display_files(filtered_files)
        self.stats_label.setText(
            f"Found {len(files)} files\n"
            f"{len(filtered_files)} match cleanup rules\n"
            f"Total size: {self.format_size(cleaner.total_size)}"
        )

    def format_size(self, size_bytes):
        """Convert bytes to a human readable string for display."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"

    def run_cleanup(self):
        # Kick off the cleaning process in a background thread
        if not self.selected_folder:
            return

        # Confirm destructive actions if configured
        if self.settings.get("confirm_deletions", True):
            reply = QMessageBox.question(
                self, "Confirm Cleanup",
                "Are you sure you want to delete the filtered files?\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                return

        # Show progress UI and start the worker thread
        self.progress_bar.show()
        self.progress_bar.setValue(0)

        cleaner = FileCleaner(self.selected_folder)
        rules = self.settings.get("rules", {})

        self.cleaner_thread = CleanerThread(cleaner, rules)
        self.cleaner_thread.progress.connect(self.progress_bar.setValue)
        self.cleaner_thread.finished.connect(self.on_cleanup_finished)
        self.cleaner_thread.error.connect(self.on_cleanup_error)
        self.cleaner_thread.start()

    @pyqtSlot(dict)
    def on_cleanup_finished(self, result):
        # Hide progress and show results to the user
        self.progress_bar.hide()
        QMessageBox.information(
            self, "Cleanup Complete",
            f"✅ Cleanup Complete!\n\n"
            f"Deleted files: {result['deleted']}\n"
            f"Space freed: {self.format_size(result['space_freed'])}\n"
            f"Errors: {result['errors']}"
        )

        # Refresh the preview to reflect current state
        self.preview_files()

    @pyqtSlot(str)
    def on_cleanup_error(self, error_msg):
        # Display any errors that occurred in the worker thread
        self.progress_bar.hide()
        QMessageBox.critical(self, "Cleanup Error", f"❌ Error: {error_msg}")

    def refresh_preview(self):
        # Convenience wrapper to re-run the preview
        self.preview_files()