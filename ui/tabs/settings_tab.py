from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QComboBox, QGroupBox, QCheckBox, QLineEdit,
                             QPushButton, QListWidget, QListWidgetItem,
                             QFormLayout, QSpinBox, QColorDialog)
from PyQt5.QtGui import QColor


class SettingsTab(QWidget):
    def __init__(self, settings):
        super().__init__()
        self.settings = settings
        self.init_ui()
        self.load_settings()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Theme Selection
        theme_group = QGroupBox("Appearance")
        theme_layout = QFormLayout()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["light", "dark", "blue", "green"])
        self.theme_combo.currentTextChanged.connect(self.save_theme)
        theme_layout.addRow("Theme:", self.theme_combo)

        self.accent_color_btn = QPushButton("Choose Accent Color")
        self.accent_color_btn.clicked.connect(self.choose_accent_color)
        theme_layout.addRow("Accent Color:", self.accent_color_btn)

        theme_group.setLayout(theme_layout)
        layout.addWidget(theme_group)

        # Cleanup Rules
        rules_group = QGroupBox("Cleanup Rules")
        rules_layout = QVBoxLayout()

        # File types to delete
        file_types_layout = QFormLayout()

        self.delete_tmp = QCheckBox("Delete temporary files (.tmp, .temp)")
        self.delete_tmp.setChecked(True)
        file_types_layout.addRow(self.delete_tmp)

        self.delete_log = QCheckBox("Delete log files (.log)")
        file_types_layout.addRow(self.delete_log)

        self.delete_cache = QCheckBox("Delete cache files")
        file_types_layout.addRow(self.delete_cache)

        rules_layout.addLayout(file_types_layout)

        # File age
        age_layout = QHBoxLayout()
        age_layout.addWidget(QLabel("Delete files older than:"))

        self.file_age = QSpinBox()
        self.file_age.setRange(0, 365)
        self.file_age.setSuffix(" days")
        self.file_age.setValue(30)
        age_layout.addWidget(self.file_age)

        age_layout.addStretch()
        rules_layout.addLayout(age_layout)

        # Minimum size
        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Minimum file size to delete:"))

        self.min_size = QSpinBox()
        self.min_size.setRange(0, 1000)
        self.min_size.setSuffix(" MB")
        self.min_size.setValue(1)
        size_layout.addWidget(self.min_size)

        size_layout.addStretch()
        rules_layout.addLayout(size_layout)

        rules_group.setLayout(rules_layout)
        layout.addWidget(rules_group)

        # Custom File Extensions
        extensions_group = QGroupBox("Custom File Extensions to Delete")
        extensions_layout = QVBoxLayout()

        self.extensions_list = QListWidget()
        extensions_layout.addWidget(self.extensions_list)

        ext_input_layout = QHBoxLayout()
        self.new_extension_input = QLineEdit()
        self.new_extension_input.setPlaceholderText("Enter extension (e.g., .bak)")
        ext_input_layout.addWidget(self.new_extension_input)

        self.add_extension_btn = QPushButton("Add")
        self.add_extension_btn.clicked.connect(self.add_extension)
        ext_input_layout.addWidget(self.add_extension_btn)

        self.remove_extension_btn = QPushButton("Remove Selected")
        self.remove_extension_btn.clicked.connect(self.remove_extension)
        ext_input_layout.addWidget(self.remove_extension_btn)

        extensions_layout.addLayout(ext_input_layout)
        extensions_group.setLayout(extensions_layout)
        layout.addWidget(extensions_group)

        # Advanced Settings
        advanced_group = QGroupBox("Advanced Settings")
        advanced_layout = QFormLayout()

        self.auto_preview = QCheckBox("Auto-preview on folder select")
        advanced_layout.addRow(self.auto_preview)

        self.confirm_deletions = QCheckBox("Confirm before deletion")
        self.confirm_deletions.setChecked(True)
        advanced_layout.addRow(self.confirm_deletions)

        self.max_file_size = QSpinBox()
        self.max_file_size.setRange(0, 10000)
        self.max_file_size.setSuffix(" MB")
        self.max_file_size.setValue(100)
        advanced_layout.addRow("Max file size to process:", self.max_file_size)

        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)

        layout.addStretch()

        # Save button
        self.save_btn = QPushButton("💾 Save Settings")
        self.save_btn.clicked.connect(self.save_all_settings)
        self.save_btn.setMinimumHeight(40)
        layout.addWidget(self.save_btn)

    def load_settings(self):
        # Load theme
        theme = self.settings.get("theme", "light")
        self.theme_combo.setCurrentText(theme)

        # Load rules
        rules = self.settings.get("rules", {})
        self.delete_tmp.setChecked(rules.get("delete_tmp", True))
        self.delete_log.setChecked(rules.get("delete_log", False))
        self.delete_cache.setChecked(rules.get("delete_cache", False))
        self.file_age.setValue(rules.get("file_age_days", 30))
        self.min_size.setValue(rules.get("min_size_mb", 1))

        # Load extensions
        extensions = rules.get("custom_extensions", [])
        self.extensions_list.clear()
        self.extensions_list.addItems(extensions)

        # Load advanced settings
        self.auto_preview.setChecked(self.settings.get("auto_preview", False))
        self.confirm_deletions.setChecked(self.settings.get("confirm_deletions", True))
        self.max_file_size.setValue(self.settings.get("max_file_size", 100))

    def save_theme(self, theme):
        self.settings.set("theme", theme)

    def choose_accent_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.settings.set("accent_color", color.name())

    def add_extension(self):
        extension = self.new_extension_input.text().strip()
        if extension and not extension.startswith('.'):
            extension = '.' + extension

        if extension and extension not in [self.extensions_list.item(i).text()
                                           for i in range(self.extensions_list.count())]:
            self.extensions_list.addItem(extension)
            self.new_extension_input.clear()

    def remove_extension(self):
        current_row = self.extensions_list.currentRow()
        if current_row >= 0:
            self.extensions_list.takeItem(current_row)

    def save_all_settings(self):
        # Save rules
        rules = {
            "delete_tmp": self.delete_tmp.isChecked(),
            "delete_log": self.delete_log.isChecked(),
            "delete_cache": self.delete_cache.isChecked(),
            "file_age_days": self.file_age.value(),
            "min_size_mb": self.min_size.value(),
            "custom_extensions": [self.extensions_list.item(i).text()
                                  for i in range(self.extensions_list.count())]
        }
        self.settings.set("rules", rules)

        # Save advanced settings
        self.settings.set("auto_preview", self.auto_preview.isChecked())
        self.settings.set("confirm_deletions", self.confirm_deletions.isChecked())
        self.settings.set("max_file_size", self.max_file_size.value())

        # Save to disk
        self.settings.save()

        QMessageBox.information(self, "Settings", "✅ Settings saved successfully!")