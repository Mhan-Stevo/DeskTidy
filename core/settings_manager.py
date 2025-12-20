import json  # for serializing/deserializing settings to JSON
import os  # for filesystem operations (checking existence, creating dirs)


class SettingsManager:
    """Manage application settings stored in a JSON file.

    Responsibilities:
    - Provide default settings
    - Load settings from disk (merge with defaults)
    - Save settings back to disk
    - Provide simple get/set accessors
    """

    def __init__(self):
        # Filename where settings are persisted (relative to cwd)
        self.settings_file = "settings.json"
        # Start with default settings; they will be merged with any loaded values
        self.settings = self.get_default_settings()

    def get_default_settings(self):
        """Return a dictionary of default settings used when no file exists.

        These defaults define sensible behavior for the application and
        ensure keys exist even before the user customizes anything.
        """
        return {
            "theme": "light",  # UI theme preference
            "rules": {
                "delete_tmp": True,  # whether to delete temporary files
                "delete_log": False,  # whether to delete log files by default
                "delete_cache": False,  # whether to delete cache files
                "file_age_days": 30,  # age threshold in days for deletions
                "min_size_mb": 1,  # minimum file size (MB) to consider
                "custom_extensions": [".bak", ".old"]  # user-defined extensions to target
            },
            "auto_preview": False,  # automatically preview files when selected
            "confirm_deletions": True,  # prompt before deleting files
            "max_file_size": 100  # maximum file size (MB) to operate on
        }

    def load(self):
        """Load settings from disk and merge into the in-memory settings dict.

        If the settings file does not exist we simply keep defaults. If
        the file exists we load it and update the defaults so missing
        keys remain present.
        """
        # Only attempt to read if the file exists
        if os.path.exists(self.settings_file):
            try:
                # Read JSON and merge into existing defaults
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Update will overwrite default keys with loaded values
                    self.settings.update(loaded)
            except Exception:
                # On any error, print a helpful message and continue with defaults
                print("Error loading settings, using defaults")

    def save(self):
        """Persist current settings to disk as JSON.

        Ensures the parent directory exists before writing. Exceptions
        during save are caught and reported to stdout.
        """
        # Ensure parent directory exists; if settings_file has no dirname use '.'
        os.makedirs(os.path.dirname(self.settings_file) or '.', exist_ok=True)

        try:
            # Write the settings dict as pretty JSON
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            # Print an error but avoid crashing the application
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        """Return the value for `key` from settings, or `default` if missing."""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Assign `value` to `key` in the settings dictionary."""
        self.settings[key] = value