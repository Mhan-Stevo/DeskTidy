import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from PyQt5.QtCore import QObject, pyqtSignal


class BatchProcessor(QObject):
    """Process files in batches using a thread pool.

    Emits Qt signals to report progress, individual file results and
    a final batch summary so the UI can remain responsive.
    """

    # Signal emitted with (percentage:int, status:str)
    progress = pyqtSignal(int, str)
    # Signal emitted for each processed file with a result dict
    file_processed = pyqtSignal(dict)
    # Signal emitted when the entire batch completes with a summary dict
    batch_complete = pyqtSignal(dict)

    def __init__(self, max_workers=4):
        super().__init__()
        self.max_workers = max_workers
        self.stop_requested = False
        self.current_batch = []

    def process_batch(self, files, operation='delete'):
        """Process a list of `files` concurrently.

        `operation` controls what action to perform per file (delete/move/compress).
        Returns a summary dict with counts and errors.
        """
        self.stop_requested = False
        self.current_batch = files

        total_files = len(files)
        processed = 0
        results = {
            'success': 0,
            'failed': 0,
            'skipped': 0,
            'total_size': 0,
            'errors': []
        }

        # Use a ThreadPoolExecutor to parallelize file operations
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Map futures to file entries so we know which file completed
            future_to_file = {
                executor.submit(self.process_file, file, operation): file
                for file in files
            }

            # Iterate as futures complete to update progress incrementally
            for future in as_completed(future_to_file):
                if self.stop_requested:
                    break

                file = future_to_file[future]
                try:
                    # Wait for result with a timeout to avoid hangs
                    result = future.result(timeout=30)

                    if result['success']:
                        results['success'] += 1
                        results['total_size'] += result.get('size', 0)
                    else:
                        results['failed'] += 1
                        results['errors'].append(result.get('error'))

                    processed += 1
                    progress = int((processed / total_files) * 100) if total_files else 100

                    # Emit progress and per-file signals for UI
                    self.progress.emit(progress, f"Processing {file['name']}")
                    self.file_processed.emit(result)

                except Exception as e:
                    # Record unexpected failures
                    results['failed'] += 1
                    results['errors'].append(str(e))
                    processed += 1

        # Emit final summary and return it
        self.batch_complete.emit(results)
        return results

    def process_file(self, file_info, operation):
        """Handle a single file operation and return a result dict.

        The method is intentionally simple here; the actual move/compress
        implementations would be added where `pass` currently exists.
        """
        result = {
            'file': file_info['name'],
            'path': file_info['path'],
            'size': file_info['size'],
            'operation': operation,
            'success': False,
            'error': None
        }

        try:
            if operation == 'delete':
                # Remove the file from disk
                import os
                os.remove(file_info['path'])
                result['success'] = True

            elif operation == 'move':
                # Placeholder for move logic (e.g., shutil.move)
                pass

            elif operation == 'compress':
                # Placeholder for compress logic (gzip/tar)
                pass

        except Exception as e:
            # Capture the exception text for reporting
            result['error'] = str(e)

        return result

    def stop_processing(self):
        """Signal that processing should stop as soon as possible."""
        self.stop_requested = True