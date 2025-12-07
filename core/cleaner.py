import os
import shutil
from datetime import datetime, timedelta


class FileCleaner:
    def __init__(self, folder_path):
        self.folder_path = folder_path
        self.total_size = 0

    def scan_files(self):
        """Scan folder and return list of files with metadata"""
        files = []
        self.total_size = 0

        for root, dirs, filenames in os.walk(self.folder_path):
            for filename in filenames:
                filepath = os.path.join(root, filename)
                try:
                    stat = os.stat(filepath)
                    file_info = {
                        'path': filepath,
                        'name': filename,
                        'size': stat.st_size,
                        'modified': datetime.fromtimestamp(stat.st_mtime),
                        'extension': os.path.splitext(filename)[1].lower()
                    }
                    files.append(file_info)
                    self.total_size += stat.st_size
                except:
                    continue  # Skip files we can't access

        return files

    def filter_files(self, files, rules):
        """Filter files based on rules"""
        filtered = []

        for file in files:
            should_delete = False

            # Check file extensions
            if rules.get('delete_tmp', True) and file['extension'] in ['.tmp', '.temp']:
                should_delete = True
            elif rules.get('delete_log', False) and file['extension'] == '.log':
                should_delete = True
            elif rules.get('delete_cache', False) and 'cache' in file['name'].lower():
                should_delete = True

            # Check custom extensions
            custom_extensions = rules.get('custom_extensions', [])
            if file['extension'] in custom_extensions:
                should_delete = True

            # Check file age
            file_age_days = rules.get('file_age_days', 30)
            if (datetime.now() - file['modified']).days > file_age_days:
                should_delete = True

            # Check minimum size
            min_size_mb = rules.get('min_size_mb', 1)
            if file['size'] > (min_size_mb * 1024 * 1024):
                should_delete = True

            if should_delete:
                filtered.append(file)

        return filtered

    def clean_files(self, rules, progress_callback=None):
        """Delete filtered files"""
        files = self.scan_files()
        to_delete = self.filter_files(files, rules)

        deleted = 0
        space_freed = 0
        errors = 0

        total_files = len(to_delete)

        for i, file in enumerate(to_delete):
            try:
                os.remove(file['path'])
                deleted += 1
                space_freed += file['size']
            except Exception as e:
                print(f"Error deleting {file['path']}: {e}")
                errors += 1

            # Update progress
            if progress_callback:
                progress = int((i + 1) / total_files * 100) if total_files > 0 else 100
                progress_callback.emit(progress)

        return {
            'deleted': deleted,
            'space_freed': space_freed,
            'errors': errors,
            'total_scanned': len(files)
        }