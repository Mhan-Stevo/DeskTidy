from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                             QLabel, QGroupBox, QProgressBar, QTreeWidget,
                             QTreeWidgetItem, QSplitter, QTableWidget,
                             QTableWidgetItem, QHeaderView)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtGui import QFont, QColor
from core.disk_analyzer import DiskAnalyzer


class AnalysisThread(QThread):
    progress = pyqtSignal(int, str)
    analysis_complete = pyqtSignal(dict)

    def __init__(self, folder_path):
        super().__init__()
        self.folder_path = folder_path
        self.analyzer = DiskAnalyzer()

    def run(self):
        self.progress.emit(0, "Starting analysis...")

        # Load from cache if available
        cached = self.analyzer.load_analysis(self.folder_path)
        if cached:
            self.progress.emit(50, "Loading cached analysis...")
            self.analysis_complete.emit(cached['stats'])
            return

        # Perform fresh analysis
        self.progress.emit(10, "Scanning folder structure...")
        stats = self.analyzer.analyze_folder(self.folder_path)

        self.progress.emit(80, "Generating recommendations...")
        stats['recommendations'] = self.analyzer.get_recommendations(stats)

        self.progress.emit(90, "Saving analysis...")
        self.analyzer.save_analysis(self.folder_path, stats)

        self.progress.emit(100, "Analysis complete!")
        self.analysis_complete.emit(stats)


class AnalysisTab(QWidget):
    def __init__(self, settings, logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self.current_analysis = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)

        # Folder selection
        folder_group = QGroupBox("Select Folder to Analyze")
        folder_layout = QHBoxLayout()

        self.folder_label = QLabel("No folder selected")
        self.folder_label.setWordWrap(True)
        folder_layout.addWidget(self.folder_label)

        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_folder)
        folder_layout.addWidget(self.browse_btn)

        self.analyze_btn = QPushButton("🔍 Analyze")
        self.analyze_btn.clicked.connect(self.start_analysis)
        self.analyze_btn.setEnabled(False)
        folder_layout.addWidget(self.analyze_btn)

        folder_group.setLayout(folder_layout)
        layout.addWidget(folder_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)

        self.progress_label = QLabel("")
        self.progress_label.hide()
        layout.addWidget(self.progress_label)

        # Splitter for results
        splitter = QSplitter(Qt.Vertical)

        # Statistics panel
        stats_group = QGroupBox("Statistics")
        stats_layout = QVBoxLayout()

        self.stats_tree = QTreeWidget()
        self.stats_tree.setHeaderLabels(["Metric", "Value"])
        self.stats_tree.setColumnWidth(0, 200)
        stats_layout.addWidget(self.stats_tree)

        stats_group.setLayout(stats_layout)
        splitter.addWidget(stats_group)

        # Recommendations panel
        rec_group = QGroupBox("Recommendations")
        rec_layout = QVBoxLayout()

        self.rec_table = QTableWidget()
        self.rec_table.setColumnCount(4)
        self.rec_table.setHorizontalHeaderLabels(["Type", "Description", "Potential Savings", "Priority"])
        self.rec_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        rec_layout.addWidget(self.rec_table)

        rec_group.setLayout(rec_layout)
        splitter.addWidget(rec_group)

        splitter.setSizes([300, 200])
        layout.addWidget(splitter)

        # Action buttons
        button_layout = QHBoxLayout()

        self.clean_btn = QPushButton("🧹 Apply Recommendations")
        self.clean_btn.clicked.connect(self.apply_recommendations)
        self.clean_btn.setEnabled(False)
        button_layout.addWidget(self.clean_btn)

        self.export_btn = QPushButton("📊 Export Report")
        self.export_btn.clicked.connect(self.export_report)
        self.export_btn.setEnabled(False)
        button_layout.addWidget(self.export_btn)

        button_layout.addStretch()
        layout.addLayout(button_layout)

    def browse_folder(self):
        from PyQt5.QtWidgets import QFileDialog
        folder = QFileDialog.getExistingDirectory(self, "Select Folder to Analyze")
        if folder:
            self.folder_path = folder
            self.folder_label.setText(folder)
            self.analyze_btn.setEnabled(True)

    def start_analysis(self):
        self.progress_bar.show()
        self.progress_label.show()
        self.progress_bar.setValue(0)

        self.analysis_thread = AnalysisThread(self.folder_path)
        self.analysis_thread.progress.connect(self.update_progress)
        self.analysis_thread.analysis_complete.connect(self.display_analysis)
        self.analysis_thread.start()

    @pyqtSlot(int, str)
    def update_progress(self, value, message):
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)

    @pyqtSlot(dict)
    def display_analysis(self, stats):
        self.current_analysis = stats
        self.progress_bar.hide()
        self.progress_label.hide()

        # Display statistics
        self.stats_tree.clear()

        # Basic stats
        basic_item = QTreeWidgetItem(["Basic Information"])
        basic_item.addChild(QTreeWidgetItem(["Total Size", self.format_size(stats['total_size'])]))
        basic_item.addChild(QTreeWidgetItem(["File Count", str(stats['file_count'])]))
        basic_item.addChild(QTreeWidgetItem(["Folder Count", str(stats['folder_count'])]))
        self.stats_tree.addTopLevelItem(basic_item)

        # File size distribution
        size_item = QTreeWidgetItem(["File Size Distribution"])
        for category, count in stats['by_size'].items():
            size_item.addChild(QTreeWidgetItem([category, str(count)]))
        self.stats_tree.addTopLevelItem(size_item)

        # File age distribution
        age_item = QTreeWidgetItem(["File Age Distribution"])
        for age_range, size in stats['by_age'].items():
            age_item.addChild(QTreeWidgetItem([age_range, self.format_size(size)]))
        self.stats_tree.addTopLevelItem(age_item)

        # File extensions
        ext_item = QTreeWidgetItem(["Largest File Types"])
        sorted_exts = sorted(stats['by_extension'].items(), key=lambda x: x[1], reverse=True)[:10]
        for ext, size in sorted_exts:
            ext_item.addChild(QTreeWidgetItem([ext or "No extension", self.format_size(size)]))
        self.stats_tree.addTopLevelItem(ext_item)

        self.stats_tree.expandAll()

        # Display recommendations
        self.display_recommendations(stats.get('recommendations', []))

        self.clean_btn.setEnabled(True)
        self.export_btn.setEnabled(True)

    def display_recommendations(self, recommendations):
        self.rec_table.setRowCount(len(recommendations))

        for row, rec in enumerate(recommendations):
            # Type
            type_item = QTableWidgetItem(rec['type'].replace('_', ' ').title())
            self.rec_table.setItem(row, 0, type_item)

            # Description
            desc_item = QTableWidgetItem(rec['description'])
            self.rec_table.setItem(row, 1, desc_item)

            # Potential Savings
            savings_item = QTableWidgetItem(f"{rec['potential_savings']:.1f} MB")
            savings_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.rec_table.setItem(row, 2, savings_item)

            # Priority
            priority_item = QTableWidgetItem(rec['priority'].upper())
            if rec['priority'] == 'high':
                priority_item.setForeground(QColor('#e74c3c'))
            elif rec['priority'] == 'medium':
                priority_item.setForeground(QColor('#f39c12'))
            else:
                priority_item.setForeground(QColor('#2ecc71'))
            priority_item.setTextAlignment(Qt.AlignCenter)
            self.rec_table.setItem(row, 3, priority_item)

    def format_size(self, size_bytes):
        """Format bytes to human readable string"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"

    def apply_recommendations(self):
        # Implement recommendation application logic
        pass

    def export_report(self):
        # Implement report export logic
        pass