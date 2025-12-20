from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QPushButton,
                             QFileDialog)
from PyQt5.QtCore import pyqtSignal


class FolderChooser(QWidget):
    """Small reusable widget that allows the user to pick a folder.

    Emits `folder_selected` with the selected path when a selection is made.
    """

    # Signal carrying the selected folder path as a string
    folder_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        # Build the user interface
        self.init_ui()

    def init_ui(self):
        # Horizontal layout: read-only line edit + browse button
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Read-only text field showing the currently selected folder
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select a folder...")
        self.path_input.setReadOnly(True)
        layout.addWidget(self.path_input)

        # Button to open a native folder picker dialog
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_btn)

    def browse_folder(self):
        # Open a platform-native directory chooser dialog
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Clean", ""
        )
        if folder:
            # Update visible path and emit the selection signal
            self.path_input.setText(folder)
            self.folder_selected.emit(folder)