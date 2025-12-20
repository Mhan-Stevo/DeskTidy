import os
import shutil
import time
from pathlib import Path
from datetime import datetime
import magic  # optional dependency used for MIME type detection


class FileOperations:
    """Utility class for common file operations with safety checks.

    Includes deletion with safety guards, metadata extraction,
    duplicate detection and simple compression.
    """

    def __init__(self):
        # Set of extensions considered unsafe to delete automatically
        self.safe_extensions = {
            '.exe', '.dll', '.sys', '.bat', '.cmd', '.ps1',
            '.sh', '.py', '.js', '.php', '.html', '.xml'
        }

    def safe_delete(self, filepath, send_to_trash=True):
        """Attempt to delete `filepath` with multiple safety checks.

        Returns a tuple `(success: bool, message: str)` describing the result.
        If `send_to_trash` is True the function will try to use `send2trash`
        to move the file to the OS recycle bin; otherwise the file is
        permanently removed.
        """
        try:
            filepath = Path(filepath)

            # Ensure the path exists before attempting deletion
            if not filepath.exists():
                return False, "File does not exist"

            # Avoid following/deleting symlinks here
            if filepath.is_symlink():
                return False, "Cannot delete symbolic links"

            # Never allow deleting the user's home directory
            if filepath.resolve() == Path.home():
                return False, "Cannot delete home directory"

            # Block deletion of files with critical extensions
            if filepath.suffix.lower() in self.safe_extensions:
                return False, f"Unsafe extension: {filepath.suffix}"

            # Warn/deny deletion of very large files (here 100MB threshold)
            file_size = filepath.stat().st_size
            if file_size > 100 * 1024 * 1024:  # 100MB
                return False, f"Large file detected ({file_size / 1024 / 1024:.1f}MB)"

            # Perform deletion: prefer sending to trash, but fall back to remove
            if send_to_trash:
                try:
                    import send2trash
                    send2trash.send2trash(str(filepath))
                    return True, "Sent to trash"
                except Exception:
                    # If send2trash is not available, perform permanent delete
                    os.remove(filepath)
                    return True, "Permanently deleted"
            else:
                os.remove(filepath)
                return True, "Permanently deleted"

        except PermissionError:
            return False, "Permission denied"
        except Exception as e:
            # Catch-all to avoid crashing callers; return failure message
            return False, f"Error: {str(e)}"

    def get_file_info(self, filepath):
        """Return a dictionary with metadata about `filepath`.

        Fields include size, timestamps, extension, path info and MIME type
        (if the optional `python-magic` package is installed).
        """
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

            # Attempt to detect MIME type; if magic is unavailable mark unknown
            try:
                mime = magic.Magic(mime=True)
                info['mime_type'] = mime.from_file(str(path))
            except Exception:
                info['mime_type'] = 'unknown'

            return info
        except Exception:
            # On failure (e.g., path inaccessible) return None
            return None

    def find_duplicates(self, folder_path):
        """Scan `folder_path` to find duplicate files.

        Returns a dict mapping (name, size, hash) -> [filepaths] where the
        value list contains at least two entries for duplicates.
        """
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
                except Exception:
                    # Skip problematic files (permission issues, etc.)
                    continue

        # Filter out keys that do not represent duplicates
        return {k: v for k, v in duplicates.items() if len(v) > 1}

    def get_file_hash(self, filepath, chunk_size=8192):
        """Calculate an MD5 hash of the file by reading it in chunks.

        Returns the hex digest or an empty string on error.
        """
        import hashlib
        hasher = hashlib.md5()

        try:
            with open(filepath, 'rb') as f:
                # Read the file in chunks to avoid high memory usage
                while chunk := f.read(chunk_size):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return ""

    def compress_file(self, filepath, compression_level=6):
        """Compress `filepath` to a gzip file and return stats.

        Returns `(success: bool, compressed_path or None, percent_reduction)`.
        """
        import gzip
        compressed_path = filepath + '.gz'

        try:
            with open(filepath, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb', compresslevel=compression_level) as f_out:
                    shutil.copyfileobj(f_in, f_out)

            original_size = os.path.getsize(filepath)
            compressed_size = os.path.getsize(compressed_path)
            # Compute percent space saved
            ratio = (original_size - compressed_size) / original_size * 100

            return True, compressed_path, ratio
        except Exception:
            return False, None, 0