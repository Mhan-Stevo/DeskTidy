from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QComboBox

class SchedulerPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout()

        layout.addWidget(QLabel("Automatic Cleaning Schedule"))

        self.combo = QComboBox()
        self.combo.addItems(["None", "Daily", "Weekly"])
        layout.addWidget(self.combo)

        self.setLayout(layout)
