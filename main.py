import sys
from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from core.settings_manager import SettingsManager


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("FileCleaner Pro")
    app.setStyle('Fusion')  # Better looking style

    # Load settings
    settings = SettingsManager()
    settings.load()

    # Create and show main window
    window = MainWindow(settings)
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()