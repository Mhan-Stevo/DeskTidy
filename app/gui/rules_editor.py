from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QLineEdit, QPushButton, QListWidget

class RulesEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Edit Rules")
        self.resize(400, 300)

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Create a rule (e.g. *.pdf → Documents/PDFs)"))

        self.ext_input = QLineEdit()
        self.ext_input.setPlaceholderText("File extension (e.g. .pdf)")
        layout.addWidget(self.ext_input)

        self.target_input = QLineEdit()
        self.target_input.setPlaceholderText("Target folder")
        layout.addWidget(self.target_input)

        add_btn = QPushButton("Add Rule")
        layout.addWidget(add_btn)

        self.rules_list = QListWidget()
        layout.addWidget(self.rules_list)

        self.setLayout(layout)