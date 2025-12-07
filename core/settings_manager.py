import json
import os


class SettingsManager:
    def __init__(self):
        self.settings_file = "settings.json"
        self.settings = self.get_default_settings()

    def get_default_settings(self):
        """Return default settings"""
        return {
            "theme": "light",
            "rules": {
                "delete_tmp": True,
                "delete_log": False,
                "delete_cache": False,
                "file_age_days": 30,
                "min_size_mb": 1,
                "custom_extensions": [".bak", ".old"]
            },
            "auto_preview": False,
            "confirm_deletions": True,
            "max_file_size": 100
        }

    def load(self):
        """Load settings from file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
            except:
                print("Error loading settings, using defaults")

    def save(self):
        """Save settings to file"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(self.settings_file) or '.', exist_ok=True)

        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
        except Exception as e:
            print(f"Error saving settings: {e}")

    def get(self, key, default=None):
        """Get setting value"""
        return self.settings.get(key, default)

    def set(self, key, value):
        """Set setting value"""
        self.settings[key] = value