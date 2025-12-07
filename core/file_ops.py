import os
import shutil
import time
from pathlib import Path
from datetime import datetime
import magic  # For MIME type detection


class FileOperations:
    """Handle all file operations with safety checks"""

    def __init__(self):
        self.safe_extensions = {
            '.exe', '.dll', '.sys', '.bat', '.cmd', '.ps1',
            '.sh', '.py', '.js', '.php', '.html', '.xml'
        }

    def safe_delete(self, filepath, send_to_trash=True):
        """Delete file with safety checks"""
        try:
            filepath = Path(filepath)

            # Safety checks
            if not filepath.exists():
                return False, "File does not exist"

            if filepath.is_symlink():
                return False, "Cannot delete symbolic links"

            if filepath.resolve() == Path.home():
                return False, "Cannot delete home directory"

            if filepath.suffix.lower() in self.safe_extensions:
                return False, f"Unsafe extension: {filepath.suffix}"

            # Check file size warning (over 100MB)
            file_size = filepath.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB
                return False, f"Large file detected ({file_size / 1024 / 1024:.1f}MB)"

            # Delete operation
            if send_to_trash:
                # Send to recycle bin/trash
                try:
                    import send2trash
                    send2trash.send2trash(str(filepath))
                    return True, "Sent to trash"
                except:
                    # Fallback to permanent delete
                    os.remove(filepath)
                    return True, "Permanently deleted"
            else:
                os.remove(filepath)
                return True, "Permanently deleted"

        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            return False, f"Error: {str(e)}"

    def get_file_info(self, filepath):
        """Get detailed file information"""
        try:
            path = Path(filepath)
            stat = path.stat()

            info = {
                'path': str(path),
                'name': path.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime),
                'modified': datetime.fromtimestamp(stat.st_mtime),
                'accessed': datetime.fromtimestamp(stat.st_atime),
                'extension': path.suffix.lower(),
                'is_dir': path.is_dir(),
                'is_file': path.is_file(),
                'is_symlink': path.is_symlink(),
                'parent': str(path.parent),
                'absolute_path': str(path.absolute())
            }

            # Try to get MIME type
            try:
                mime = magic.Magic(mime=True)
                info['mime_type'] = mime.from_file(str(path))
            except:
                info['mime_type'] = 'unknown'

            return info
        except Exception as e:
            return None

    def find_duplicates(self, folder_path):
        """Find duplicate files in a folder"""
        duplicates = {}
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                filepath = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(filepath)
                    file_hash = self.get_file_hash(filepath)

                    key = (file, file_size, file_hash)
                    if key in duplicates:
                        duplicates[key].append(filepath)
                    else:
                        duplicates[key] = [filepath]
                except:
                    continue

        # Return only actual duplicates (more than one file)
        return {k: v for k, v in duplicates.items() if len(v) > 1}

    def get_file_hash(self, filepath, chunk_size=8192):
        """Calculate file hash for duplicate detection"""
        import hashlib
        hasher = hashlib.md5()

        try:
            with open(filepath, 'rb') as f:
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except:
            return ""

    def compress_file(self, filepath, compression_level=6):
        """Compress a file (gzip)"""
        import gzip
        compressed_path = filepath + '.gz'

        try:
            with open(filepath, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            original_size = os.path.getsize(filepath)
            compressed_size = os.path.getsize(compressed_path)
            ratio = (original_size - compressed_size) / original_size * 100

            return True, compressed_path, ratio
        except Exception as e:
            return False, None, 0