from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, QPushButton,
                             QFileDialog)
from PyQt5.QtCore import pyqtSignal


class FolderChooser(QWidget):
    folder_selected = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select a folder...")
        self.path_input.setReadOnly(True)
        layout.addWidget(self.path_input)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_folder)
        layout.addWidget(self.browse_btn)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(
            self, "Select Folder to Clean", ""
        )
        if folder:
            self.path_input.setText(folder)
            self.folder_selected.emit(folder)