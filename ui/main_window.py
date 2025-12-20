"""
Main application window
-----------------------
Creates the primary `QMainWindow`, sets up the tabbed UI, status bar,
and application menu. The MainWindow wires together the `settings` and
`logger` objects with the tab widgets so the UI can interact with the
core logic (settings persistence, logging, and running cleaners).
"""

from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout,
                             QWidget, QStatusBar, QAction, QMenuBar,
                             QMessageBox)
from PyQt5.QtCore import Qt
from ui.tabs.file_cleaner_tab import FileCleanerTab
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.logs_tab import LogsTab


class MainWindow(QMainWindow):
    def __init__(self, settings, logger):
        # `settings` should implement get/set/save methods
        # `logger` should expose signal `log_added` and methods like get_logs
        super().__init__()
        self.settings = settings
        self.logger = logger

        # Build UI and menus
        self.init_ui()
        self.setup_menu()

    def init_ui(self):
        # Window basic properties
        self.setWindowTitle("FileCleaner Pro")
        self.setGeometry(100, 100, 1200, 800)

        # Central widget holds the tab widget layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Tab widget contains the primary application screens
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(False)  # Keep tabs in fixed order

        # Instantiate tabs and inject dependencies where required
        self.file_cleaner_tab = FileCleanerTab(self.settings, self.logger)
        self.settings_tab = SettingsTab(self.settings)
        self.logs_tab = LogsTab(self.settings, self.logger)

        # Wire logger's signal to the logs tab so the UI updates live
        self.logger.log_added.connect(self.logs_tab.on_new_log)

        # Add tabs to the QTabWidget (text icons used for simplicity)
        self.tab_widget.addTab(self.file_cleaner_tab, "📁 File Cleaner")
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        self.tab_widget.addTab(self.logs_tab, "📈 Logs")

        # Helpful tooltips for each tab
        self.tab_widget.setTabToolTip(0, "Clean files and folders")
        self.tab_widget.setTabToolTip(1, "Configure application settings")
        self.tab_widget.setTabToolTip(2, "View cleaning history")

        layout.addWidget(self.tab_widget)

        # Simple status bar to show short messages
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Apply the persisted theme (if any)
        self.apply_theme()

    def apply_theme(self):
        # Apply a stylesheet based on persisted theme name. Styles are
        # embedded here for simplicity; a larger app might load .qss files.
        theme = self.settings.get("theme", "light")
        if theme == "dark":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
                QTabWidget::pane {
                    border: 1px solid #444;
                    background-color: #2b2b2b;
                    border-radius: 4px;
                }
                QTabBar::tab {
                    background-color: #3c3c3c;
                    color: #ffffff;
                    padding: 10px 20px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    font-size: 12px;
                }
                QTabBar::tab:selected {
                    background-color: #007acc;
                    font-weight: bold;
                }
                QTabBar::tab:hover {
                    background-color: #505050;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 2px solid #444;
                    border-radius: 5px;
                    margin-top: 10px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
            """)
        elif theme == "blue":
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f0f8ff;
                }
                QTabBar::tab {
                    background-color: #e6f2ff;
                    padding: 10px 20px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected {
                    background-color: #007acc;
                    color: white;
                    font-weight: bold;
                }
            """)
        else:  # light theme
            self.setStyleSheet("""
                QTabBar::tab {
                    padding: 10px 20px;
                    margin-right: 2px;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    background-color: #f0f0f0;
                }
                QTabBar::tab:selected {
                    background-color: #ffffff;
                    border-bottom: 2px solid #007acc;
                    font-weight: bold;
                }
                QTabBar::tab:hover {
                    background-color: #e0e0e0;
                }
                QGroupBox {
                    font-weight: bold;
                    border: 1px solid #ccc;
                    border-radius: 4px;
                    margin-top: 10px;
                }
            """)

    def setup_menu(self):
        menubar = self.menuBar()

        # File menu with an export logs action and exit
        file_menu = menubar.addMenu("File")

        export_action = QAction("Export Logs...", self)
        export_action.triggered.connect(self.logs_tab.export_logs)
        export_action.setShortcut("Ctrl+E")
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        file_menu.addAction(exit_action)

        # Edit menu contains quick navigation to settings
        edit_menu = menubar.addMenu("Edit")

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        settings_action.setShortcut("Ctrl+,")
        edit_menu.addAction(settings_action)

        # View menu contains UI-level commands (refresh + open logs)
        view_menu = menubar.addMenu("View")

        refresh_action = QAction("Refresh Preview", self)
        refresh_action.triggered.connect(self.file_cleaner_tab.refresh_preview)
        refresh_action.setShortcut("F5")
        view_menu.addAction(refresh_action)

        view_logs_action = QAction("View Logs", self)
        view_logs_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(2))
        view_logs_action.setShortcut("Ctrl+L")
        view_menu.addAction(view_logs_action)

        view_menu.addSeparator()

        # Theme submenu to change styling at runtime
        theme_menu = view_menu.addMenu("Theme")

        light_theme = QAction("Light", self)
        light_theme.triggered.connect(lambda: self.change_theme("light"))
        theme_menu.addAction(light_theme)

        dark_theme = QAction("Dark", self)
        dark_theme.triggered.connect(lambda: self.change_theme("dark"))
        theme_menu.addAction(dark_theme)

        blue_theme = QAction("Blue", self)
        blue_theme.triggered.connect(lambda: self.change_theme("blue"))
        theme_menu.addAction(blue_theme)

        # Help menu with documentation and about dialog
        help_menu = menubar.addMenu("Help")

        docs_action = QAction("Documentation", self)
        docs_action.setShortcut("F1")
        help_menu.addAction(docs_action)

        help_menu.addSeparator()

        about_action = QAction("About FileCleaner Pro", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def change_theme(self, theme_name):
        # Persist chosen theme and re-apply styles immediately. The
        # message suggests a restart but here we simply reapply the
        # stylesheet so changes take effect in the running instance.
        self.settings.set("theme", theme_name)
        self.settings.save()
        self.apply_theme()
        QMessageBox.information(self, "Theme Changed",
                                f"Theme changed to {theme_name.capitalize()}.\n"
                                "Application will restart with new theme.")

    def show_about(self):
        # Display an about dialog with basic product info. This is a
        # simple, hard-coded HTML string; internationalization would move
        # these strings to a resource or translation files.
        QMessageBox.about(self, "About FileCleaner Pro",
                          "<h2>FileCleaner Pro</h2>"
                          "<p>Version 1.0.0</p>"
                          "<p>A professional file cleaning utility for desktop.</p>"
                          "<p>© 2024 FileCleaner Pro. All rights reserved.</p>"
                          "<hr>"
                          "<p>Features:</p>"
                          "<ul>"
                          "<li>Smart file cleaning with preview</li>"
                          "<li>Configurable cleanup rules</li>"
                          "<li>Detailed activity logs</li>"
                          "<li>Multiple theme support</li>"
                          "</ul>")

    def closeEvent(self, event):
        """Handle application close event.

        Saves settings, logs shutdown, and asks the user to confirm if a
        cleanup operation is currently running.
        """
        # Persist settings immediately
        self.settings.save()

        # Emit a final log entry
        self.logger.log_action("System", "Application shutdown", status="Info")

        # If a cleanup thread is running, ask the user whether to abort
        if hasattr(self.file_cleaner_tab, 'cleaner_thread') and self.file_cleaner_tab.cleaner_thread.isRunning():
            reply = QMessageBox.question(
                self, "Cleanup in Progress",
                "A file cleanup operation is still in progress.\n"
                "Do you want to stop it and exit?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                # User chose not to exit while cleanup is running
                event.ignore()
                return

        # Allow the window to close
        event.accept()