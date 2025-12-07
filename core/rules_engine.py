import re
from datetime import datetime, timedelta
from pathlib import Path


class RulesEngine:
    """Advanced rules engine for file filtering"""

    def __init__(self):
        self.rules = {}

    def load_rules(self, rules_config):
        """Load rules from configuration"""
        self.rules = rules_config

    def evaluate_file(self, file_info):
        """Evaluate if a file should be deleted based on rules"""
        score = 0
        reasons = []

        # File age rule
        if 'max_age_days' in self.rules:
            max_age = self.rules['max_age_days']
            file_age = (datetime.now() - file_info['modified']).days
            if file_age > max_age:
                score += 1
                reasons.append(f"Old file ({file_age} days > {max_age} days)")

        # File size rule
        if 'min_size_mb' in self.rules:
            min_size_bytes = self.rules['min_size_mb'] * 1024 * 1024
            if file_info['size'] > min_size_bytes:
                score += 1
                reasons.append(f"Large file ({file_info['size'] / 1024 / 1024:.1f}MB)")

        # Extension rules
        if 'delete_extensions' in self.rules:
            for pattern in self.rules['delete_extensions']:
                if re.match(pattern, file_info['extension'], re.IGNORECASE):
                    score += 2
                    reasons.append(f"Extension matches: {pattern}")
                    break

        # Name pattern rules
        if 'name_patterns' in self.rules:
            for pattern in self.rules['name_patterns']:
                if re.search(pattern, file_info['name'], re.IGNORECASE):
                    score += 1
                    reasons.append(f"Name matches pattern: {pattern}")

        # Folder location rules
        if 'excluded_folders' in self.rules:
            for folder in self.rules['excluded_folders']:
                if folder in file_info['path']:
                    score -= 10  # Negative score to protect
                    reasons.append(f"Protected folder: {folder}")

        # Category-based rules
        if 'categories' in self.rules:
            file_category = self.categorize_file(file_info)
            if file_category in self.rules['categories']:
                category_rules = self.rules['categories'][file_category]
                if category_rules.get('delete', False):
                    score += 3
                    reasons.append(f"Category: {file_category}")

        return score >= 2, reasons  # File should be deleted if score >= 2

    def categorize_file(self, file_info):
        """Categorize file based on extension and MIME type"""
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
        """Validate rules configuration"""
        errors = []

        if 'max_age_days' in self.rules:
            if not isinstance(self.rules['max_age_days'], int) or self.rules['max_age_days'] < 0:
                errors.append("max_age_days must be a positive integer")

        if 'min_size_mb' in self.rules:
            if not isinstance(self.rules['min_size_mb'], (int, float)) or self.rules['min_size_mb'] < 0:
                errors.append("min_size_mb must be a positive number")

        return errors