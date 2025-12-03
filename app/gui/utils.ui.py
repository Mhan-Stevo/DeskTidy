from PyQt5.QtWidgets import QMessageBox

def alert(message):
    popup = QMessageBox()
    popup.setText(message)
    popup.exec_()
