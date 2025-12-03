from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QFileDialog,
    QListWidget, QHBoxLayout, QComboBox
)
from PyQt5.QtCore import Qt
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("DeskTidy")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)

        self.selected_folder = ""

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Title
        title = QLabel("DeskTidy — Desktop Cleaner")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)

        # Folder selection
        folder_btn = QPushButton("Select Folder")
        folder_btn.clicked.connect(self.choose_folder)
        layout.addWidget(folder_btn)

        # Show selected folder
        self.folder_label = QLabel("No folder selected.")
        layout.addWidget(self.folder_label)

        # File preview list
        self.preview_list = QListWidget()
        layout.addWidget(self.preview_list)

        # Theme selector
        theme_row = QHBoxLayout()
        theme_label = QLabel("Theme:")
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        self.theme_combo.currentIndexChanged.connect(self.change_theme)
        theme_row.addWidget(theme_label)
        theme_row.addWidget(self.theme_combo)
        layout.addLayout(theme_row)

        # Clean button
        clean_btn = QPushButton("Run Cleaning")
        layout.addWidget(clean_btn)

        # Main widget
        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.selected_folder = folder
            self.folder_label.setText(f"Selected: {folder}")

    def change_theme(self):
        choice = self.theme_combo.currentText()
        if choice == "Light":
            self.setStyleSheet("background-color: white; color: black;")
        else:
            self.setStyleSheet("background-color: #121212; color: white;")
