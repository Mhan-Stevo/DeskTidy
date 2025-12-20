import re
from datetime import datetime, timedelta
from pathlib import Path


class RulesEngine:
    """Advanced rules engine for file filtering.

    The engine supports multiple rule types (age, size, extension
    patterns, name patterns, excluded folders and category based rules)
    and produces a score and reasons for why a file should be deleted.
    """

    def __init__(self):
        # Container for the loaded rules configuration
        self.rules = {}

    def load_rules(self, rules_config):
        """Load rules from an external configuration (dict)."""
        self.rules = rules_config

    def evaluate_file(self, file_info):
        """Evaluate a file against the rules and return (should_delete, reasons).

        `file_info` is expected to be a dict with at least 'modified',
        'size', 'extension' and 'name' keys. A scoring system is used —
        if the cumulative score reaches 2 or more the file is marked
        as deletable. The method returns a boolean plus a list of reasons.
        """
        score = 0
        reasons = []

        # Age-based rule
        if 'max_age_days' in self.rules:
            max_age = self.rules['max_age_days']
            file_age = (datetime.now() - file_info['modified']).days
            if file_age > max_age:
                score += 1
                reasons.append(f"Old file ({file_age} days > {max_age} days)")

        # Size-based rule
        if 'min_size_mb' in self.rules:
            min_size_bytes = self.rules['min_size_mb'] * 1024 * 1024
            if file_info['size'] > min_size_bytes:
                score += 1
                reasons.append(f"Large file ({file_info['size'] / 1024 / 1024:.1f}MB)")

        # Extension patterns (regular expressions)
        if 'delete_extensions' in self.rules:
            for pattern in self.rules['delete_extensions']:
                if re.match(pattern, file_info['extension'], re.IGNORECASE):
                    score += 2
                    reasons.append(f"Extension matches: {pattern}")
                    break

        # Filename regex patterns
        if 'name_patterns' in self.rules:
            for pattern in self.rules['name_patterns']:
                if re.search(pattern, file_info['name'], re.IGNORECASE):
                    score += 1
                    reasons.append(f"Name matches pattern: {pattern}")

        # Excluded/protected folders subtract a large score to prevent deletion
        if 'excluded_folders' in self.rules:
            for folder in self.rules['excluded_folders']:
                if folder in file_info['path']:
                    score -= 10  # strong protection
                    reasons.append(f"Protected folder: {folder}")

        # Category-based rules allow grouping of file types with specific actions
        if 'categories' in self.rules:
            file_category = self.categorize_file(file_info)
            if file_category in self.rules['categories']:
                category_rules = self.rules['categories'][file_category]
                if category_rules.get('delete', False):
                    score += 3
                    reasons.append(f"Category: {file_category}")

        # Return a decision and the collected reasons for transparency
        return score >= 2, reasons

    def categorize_file(self, file_info):
        """Classify a file into a category such as images, documents, videos.

        Uses file extension first and MIME type (if provided) as a fallback.
        """
        extension = file_info['extension'].lower()
        mime_type = file_info.get('mime_type', '')

        # Image files
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
        if extension in image_exts or 'image' in mime_type:
            return 'images'

        # Document files
        doc_exts = {'.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.txt'}
        if extension in doc_exts or 'text' in mime_type:
            return 'documents'

        # Video files
        video_exts = {'.mp4', '.avi', '.mov', '.wmv', '.flv', '.mkv'}
        if extension in video_exts or 'video' in mime_type:
            return 'videos'

        # Audio files
        audio_exts = {'.mp3', '.wav', '.aac', '.flac', '.ogg'}
        if extension in audio_exts or 'audio' in mime_type:
            return 'audio'

        # Archive files
        archive_exts = {'.zip', '.rar', '.7z', '.tar', '.gz'}
        if extension in archive_exts:
            return 'archives'

        # Temporary files
        temp_exts = {'.tmp', '.temp', '.bak', '.old'}
        if extension in temp_exts:
            return 'temporary'

        # Log files
        if extension == '.log':
            return 'logs'

        return 'other'

    def validate_rules(self):
        """Simple validation for the rules configuration.

        Returns a list of human-readable error strings.
        """
        errors = []

        if 'max_age_days' in self.rules:
            if not isinstance(self.rules['max_age_days'], int) or self.rules['max_age_days'] < 0:
                errors.append("max_age_days must be a positive integer")

        if 'min_size_mb' in self.rules:
            if not isinstance(self.rules['min_size_mb'], (int, float)) or self.rules['min_size_mb'] < 0:
                errors.append("min_size_mb must be a positive number")

        return errors