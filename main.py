import sys
import os
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from ui.main_window import MainWindow
from core.settings_manager import SettingsManager
from core.logger import Logger


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler"""
    import traceback

    # Log the error
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    print(f"Unhandled exception: {error_msg}")

    # Show error dialog
    QMessageBox.critical(
        None,
        "Unexpected Error",
        f"An unexpected error occurred:\n\n{str(exc_value)}\n\n"
        "The application may become unstable."
    )


def check_requirements():
    """Check if required directories exist"""
    required_dirs = ['logs', 'ui', 'core', 'ui/components', 'ui/tabs']

    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)
                print(f"Created directory: {dir_name}")
            except Exception as e:
                print(f"Failed to create directory {dir_name}: {e}")


def main():
    # Set up exception handling
    sys.excepthook = handle_exception

    # Check and create required directories
    check_requirements()

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("DeskTidy")
    app.setOrganizationName("DeskTidy")
    app.setApplicationVersion("1.0.1")

    # Set application style
    app.setStyle('Fusion')

    # Create a splash message
    print("Starting DeskTidy...")

    # Initialize core components
    try:
        settings = SettingsManager()
        settings.load()

        logger = Logger()

        # Create and show main window
        window = MainWindow(settings, logger)
        window.show()

        # Center window on screen
        window.move(
            app.desktop().screen().rect().center() - window.rect().center()
        )

        # Show ready message
        window.status_bar.showMessage("Ready - Select a folder to begin")

        # Ensure application quits properly
        app.aboutToQuit.connect(lambda: settings.save())

        print("Application started successfully")

    except Exception as e:
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to start application:\n\n{str(e)}"
        )
        return 1

    # Start event loop
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())