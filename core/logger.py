import json
import os
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal


class Logger(QObject):
    """Logger class for tracking application events"""

    # Signal to update UI when new log is added
    log_added = pyqtSignal(dict)

    def __init__(self, log_file="logs/cleaner_logs.json"):
        super().__init__()
        self.log_file = log_file
        self.logs = []
        self.ensure_log_directory()
        self.load_logs()

    def ensure_log_directory(self):
        """Create logs directory if it doesn't exist"""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    def load_logs(self):
        """Load existing logs from file"""
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.logs = json.load(f)
                    # Convert string timestamps back to datetime
                    for log in self.logs:
                        log['timestamp'] = datetime.fromisoformat(log['timestamp'])
            except Exception as e:
                print(f"Error loading logs: {e}")
                self.logs = []
        else:
            self.logs = []

    def save_logs(self):
        """Save logs to file"""
        try:
            # Convert datetime to string for JSON serialization
            logs_to_save = []
            for log in self.logs:
                log_copy = log.copy()
                log_copy['timestamp'] = log['timestamp'].isoformat()
                logs_to_save.append(log_copy)

            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving logs: {e}")

    def log_action(self, action_type, details, files_affected=0, status="Success"):
        """Log an action"""
        log_entry = {
            'timestamp': datetime.now(),
            'action': action_type,
            'details': details,
            'files': files_affected,
            'status': status
        }

        self.logs.append(log_entry)

        # Keep only last 1000 logs to prevent file from getting too large
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]

        # Save to file
        self.save_logs()

        # Emit signal for UI updates
        self.log_added.emit(log_entry)

        return log_entry

    def log_cleanup(self, folder, files_deleted, space_freed, errors=0):
        """Log a cleanup operation"""
        status = "Success" if errors == 0 else f"Partial Success ({errors} errors)"
        details = f"Cleaned: {folder}"

        return self.log_action(
            action_type="Deletion",
            details=details,
            files_affected=files_deleted,
            status=status
        )

    def log_preview(self, folder, files_found, files_to_delete):
        """Log a preview operation"""
        return self.log_action(
            action_type="Preview",
            details=f"Previewed: {folder}",
            files_affected=files_found,
            status=f"{files_to_delete} to delete"
        )

    def log_error(self, error_message, action_type="Error"):
        """Log an error"""
        return self.log_action(
            action_type=action_type,
            details=error_message,
            files_affected=0,
            status="Failed"
        )

    def get_logs(self, limit=None, filter_type=None, date_range=None):
        """Get logs with optional filtering"""
        logs = self.logs.copy()

        # Filter by type
        if filter_type and filter_type != "All":
            logs = [log for log in logs if log['action'] == filter_type]

        # Filter by date range
        if date_range:
            start_date, end_date = date_range
            logs = [log for log in logs if start_date <= log['timestamp'].date() <= end_date]

        # Sort by timestamp (newest first)
        logs.sort(key=lambda x: x['timestamp'], reverse=True)

        # Apply limit
        if limit:
            logs = logs[:limit]

        return logs

    def clear_logs(self):
        """Clear all logs"""
        self.logs = []
        if os.path.exists(self.log_file):
            os.remove(self.log_file)