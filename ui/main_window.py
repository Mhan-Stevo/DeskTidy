from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QVBoxLayout,
                             QWidget, QStatusBar, QAction, QMenuBar,
                             QMessageBox)
from PyQt5.QtCore import Qt
from ui.tabs.file_cleaner_tab import FileCleanerTab
from ui.tabs.settings_tab import SettingsTab
from ui.tabs.logs_tab import LogsTab


class MainWindow(QMainWindow):
    def __init__(self, settings, logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self.init_ui()
        self.setup_menu()

    def init_ui(self):
        self.setWindowTitle("FileCleaner Pro")
        self.setGeometry(100, 100, 1200, 800)

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabPosition(QTabWidget.North)
        self.tab_widget.setMovable(False)  # Keep tabs in fixed order

        # Create tabs with dependencies
        self.file_cleaner_tab = FileCleanerTab(self.settings, self.logger)
        self.settings_tab = SettingsTab(self.settings)
        self.logs_tab = LogsTab(self.settings, self.logger)

        # Connect logger signals
        self.logger.log_added.connect(self.logs_tab.on_new_log)

        # Add tabs with icons and tooltips
        self.tab_widget.addTab(self.file_cleaner_tab, "📁 File Cleaner")
        self.tab_widget.addTab(self.settings_tab, "⚙️ Settings")
        self.tab_widget.addTab(self.logs_tab, "📈 Logs")

        # Set tab tooltips
        self.tab_widget.setTabToolTip(0, "Clean files and folders")
        self.tab_widget.setTabToolTip(1, "Configure application settings")
        self.tab_widget.setTabToolTip(2, "View cleaning history")

        layout.addWidget(self.tab_widget)

        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

        # Apply theme
        self.apply_theme()

    def apply_theme(self):
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

        # File menu
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

        # Edit menu
        edit_menu = menubar.addMenu("Edit")

        settings_action = QAction("Settings", self)
        settings_action.triggered.connect(lambda: self.tab_widget.setCurrentIndex(1))
        settings_action.setShortcut("Ctrl+,")
        edit_menu.addAction(settings_action)

        # View menu
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

        # Theme submenu
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

        # Help menu
        help_menu = menubar.addMenu("Help")

        docs_action = QAction("Documentation", self)
        docs_action.setShortcut("F1")
        help_menu.addAction(docs_action)

        help_menu.addSeparator()

        about_action = QAction("About FileCleaner Pro", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def change_theme(self, theme_name):
        self.settings.set("theme", theme_name)
        self.settings.save()
        self.apply_theme()
        QMessageBox.information(self, "Theme Changed",
                                f"Theme changed to {theme_name.capitalize()}.\n"
                                "Application will restart with new theme.")

    def show_about(self):
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
        """Handle application close event"""
        # Save settings
        self.settings.save()

        # Log shutdown
        self.logger.log_action("System", "Application shutdown", status="Info")

        # Confirm close if cleanup is in progress
        if hasattr(self.file_cleaner_tab, 'cleaner_thread') and self.file_cleaner_tab.cleaner_thread.isRunning():
            reply = QMessageBox.question(
                self, "Cleanup in Progress",
                "A file cleanup operation is still in progress.\n"
                "Do you want to stop it and exit?",
                QMessageBox.Yes | QMessageBox.No
            )

            if reply == QMessageBox.No:
                event.ignore()
                return

        event.accept()