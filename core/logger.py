import json  # for serializing logs
import os  # filesystem utilities
from datetime import datetime  # for timestamps
from PyQt5.QtCore import QObject, pyqtSignal  # Qt object base and signals


class Logger(QObject):
    """Logger class for tracking application events.

    This class stores log entries in memory and persists them to a JSON
    file. It also emits a Qt signal when a new log is added so UI
    components can react.
    """

    # Signal emitted with the new log entry dict when a log is added
    log_added = pyqtSignal(dict)

    def __init__(self, log_file="logs/cleaner_logs.json"):
        super().__init__()
        # Path to the log file on disk
        self.log_file = log_file
        # In-memory list of log dictionaries
        self.logs = []
        # Ensure directory exists and load any existing logs
        self.ensure_log_directory()
        self.load_logs()

    def ensure_log_directory(self):
        """Create parent directory for log file if it doesn't exist."""
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

    def load_logs(self):
        """Load existing logs from JSON file and convert timestamps.

        If the file is missing or corrupted we fall back to an empty list.
        """
        if os.path.exists(self.log_file):
            try:
                with open(self.log_file, 'r', encoding='utf-8') as f:
                    self.logs = json.load(f)
                    # Convert ISO-format timestamp strings back to datetime
                    for log in self.logs:
                        log['timestamp'] = datetime.fromisoformat(log['timestamp'])
            except Exception as e:
                # If anything goes wrong, report it and reset logs to empty
                print(f"Error loading logs: {e}")
                self.logs = []
        else:
            # No file yet — start with an empty log list
            self.logs = []

    def save_logs(self):
        """Persist logs to disk, converting datetimes to ISO strings."""
        try:
            # Convert each log entry's timestamp to a serializable ISO string
            logs_to_save = []
            for log in self.logs:
                log_copy = log.copy()
                log_copy['timestamp'] = log['timestamp'].isoformat()
                logs_to_save.append(log_copy)

            with open(self.log_file, 'w', encoding='utf-8') as f:
                json.dump(logs_to_save, f, indent=2, ensure_ascii=False)
        except Exception as e:
            # Printing here is acceptable; don't raise to avoid crashing callers
            print(f"Error saving logs: {e}")

    def log_action(self, action_type, details, files_affected=0, status="Success"):
        """Create and store a single log entry.

        Parameters:
        - action_type: string describing the kind of action (e.g. 'Deletion')
        - details: human-readable details about the action
        - files_affected: integer count of files touched
        - status: string status (e.g. 'Success' or 'Failed')
        """
        # Build the log dict with a current timestamp
        log_entry = {
            'timestamp': datetime.now(),
            'action': action_type,
            'details': details,
            'files': files_affected,
            'status': status
        }

        # Append to in-memory logs
        self.logs.append(log_entry)

        # Keep log list bounded to prevent excessive disk usage
        if len(self.logs) > 1000:
            self.logs = self.logs[-1000:]

        # Persist to disk and notify any UI listeners
        self.save_logs()
        self.log_added.emit(log_entry)

        # Return the entry for convenience
        return log_entry

    def log_cleanup(self, folder, files_deleted, space_freed, errors=0):
        """Convenience method to log a cleanup/deletion operation."""
        status = "Success" if errors == 0 else f"Partial Success ({errors} errors)"
        details = f"Cleaned: {folder}"

        return self.log_action(
            action_type="Deletion",
            details=details,
            files_affected=files_deleted,
            status=status
        )

    def log_preview(self, folder, files_found, files_to_delete):
        """Convenience method to log preview operations (no deletion yet)."""
        return self.log_action(
            action_type="Preview",
            details=f"Previewed: {folder}",
            files_affected=files_found,
            status=f"{files_to_delete} to delete"
        )

    def log_error(self, error_message, action_type="Error"):
        """Log an error with failure status."""
        return self.log_action(
            action_type=action_type,
            details=error_message,
            files_affected=0,
            status="Failed"
        )

    def get_logs(self, limit=None, filter_type=None, date_range=None):
        """Return logs optionally filtered by type and date range.

        - `limit` caps the number of returned entries
        - `filter_type` filters by the action string
        - `date_range` is a tuple (start_date, end_date) of `date` objects
        """
        logs = self.logs.copy()

        # Filter by action type unless 'All' is requested
        if filter_type and filter_type != "All":
            logs = [log for log in logs if log['action'] == filter_type]

        # Filter by date range (inclusive)
        if date_range:
            start_date, end_date = date_range
            logs = [log for log in logs if start_date <= log['timestamp'].date() <= end_date]

        # Sort newest first
        logs.sort(key=lambda x: x['timestamp'], reverse=True)

        # Apply a limit if provided
        if limit:
            logs = logs[:limit]

        return logs

    def clear_logs(self):
        """Erase all logs from memory and delete the log file if it exists."""
        self.logs = []
        if os.path.exists(self.log_file):
            os.remove(self.log_file)