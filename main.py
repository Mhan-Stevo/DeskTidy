import sys  # access to interpreter-related utilities and argv
import os  # filesystem and OS interaction utilities
from PyQt5.QtWidgets import QApplication, QMessageBox  # main Qt application class and message dialog
from PyQt5.QtCore import QTimer  # Qt timer useful for scheduled callbacks (kept for potential use)
from ui.main_window import MainWindow  # import main window class from UI package
from core.settings_manager import SettingsManager  # import settings manager for load/save
from core.logger import Logger  # import simple logger wrapper


def handle_exception(exc_type, exc_value, exc_traceback):
    """Global exception handler.

    This function will be assigned to `sys.excepthook` so that any
    uncaught exception in the main thread is routed here. It formats
    the traceback for logging and displays an error dialog to the user.
    """
    import traceback  # import here to avoid top-level overhead

    # Format the full traceback into a readable string
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    # Print to stdout so developers running from a console can see the trace
    print(f"Unhandled exception: {error_msg}")

    # Show a blocking error dialog so users are aware the app is unstable
    QMessageBox.critical(
        None,
        "Unexpected Error",
        f"An unexpected error occurred:\n\n{str(exc_value)}\n\n"
        "The application may become unstable."
    )


def check_requirements():
    """Ensure required filesystem directories exist.

    The application expects several directories such as `logs` and
    UI subfolders. If they are missing, create them so subsequent
    operations (like writing logs) don't fail.
    """
    required_dirs = ['logs', 'ui', 'core', 'ui/components', 'ui/tabs']

    # Create each required directory if it does not already exist
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            try:
                os.makedirs(dir_name, exist_ok=True)  # create nested dirs as needed
                print(f"Created directory: {dir_name}")
            except Exception as e:
                # Print error but don't raise — startup may continue depending on the failure
                print(f"Failed to create directory {dir_name}: {e}")


def main():
    # Set up exception handling
    sys.excepthook = handle_exception

    # Check and create required directories
    check_requirements()

    # Create the Qt application instance with command-line args
    app = QApplication(sys.argv)
    # Set metadata for the application (used by settings/storage on some OSes)
    app.setApplicationName("DeskTidy")
    app.setOrganizationName("DeskTidy")
    app.setApplicationVersion("1.0.1")

    # Set a consistent UI style
    app.setStyle('Fusion')

    # Print startup message for console users
    print("Starting DeskTidy...")

    # Initialize the app's core components and UI, handling any startup errors
    try:
        settings = SettingsManager()  # create settings manager instance
        settings.load()  # load persisted settings from disk (if present)

        logger = Logger()  # initialize application logger

        # Create the main window, passing in settings and logger for use by UI
        window = MainWindow(settings, logger)
        window.show()  # make the window visible

        # Center the window on the primary screen by moving its rect
        window.move(
            app.desktop().screen().rect().center() - window.rect().center()
        )

        # Display a helpful status message in the UI
        window.status_bar.showMessage("Ready - Select a folder to begin")

        # Persist settings when the app is about to quit
        app.aboutToQuit.connect(lambda: settings.save())

        print("Application started successfully")

    except Exception as e:
        # If anything goes wrong during initialization, show a blocking dialog
        QMessageBox.critical(
            None,
            "Startup Error",
            f"Failed to start application:\n\n{str(e)}"
        )
        return 1

    # Start the Qt event loop (this call blocks until the application exits)
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())