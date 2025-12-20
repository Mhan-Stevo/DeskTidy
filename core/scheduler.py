import schedule
import time
import threading
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal


class Scheduler(QObject):
    """Background scheduler for automated cleanups.

    Uses the `schedule` library to define jobs and runs them in a
    background thread. When a scheduled cleanup should execute the
    `cleanup_triggered` signal is emitted with details.
    """

    # Signal emitted with a dict describing the triggered cleanup
    cleanup_triggered = pyqtSignal(dict)

    def __init__(self, settings, logger):
        super().__init__()
        self.settings = settings  # Settings manager instance
        self.logger = logger  # Logger instance for recording events
        self.scheduled_jobs = []  # Keep track of job descriptors
        self.running = False

    def schedule_daily_cleanup(self, time_str, folder_path, rules):
        """Schedule a job to run every day at `time_str` (HH:MM format)."""

        def job():
            # Record that a scheduled job ran and notify listeners
            self.logger.log_action("Scheduled", f"Daily cleanup for {folder_path}")
            self.cleanup_triggered.emit({
                'type': 'daily',
                'folder': folder_path,
                'rules': rules,
                'time': datetime.now()
            })

        job_id = schedule.every().day.at(time_str).do(job)
        self.scheduled_jobs.append({
            'id': job_id,
            'type': 'daily',
            'time': time_str,
            'folder': folder_path
        })

    def schedule_weekly_cleanup(self, day, time_str, folder_path, rules):
        """Schedule a weekly cleanup on a specific day at `time_str`.

        `day` should be a weekday name (e.g. 'monday').
        """

        def job():
            self.logger.log_action("Scheduled", f"Weekly cleanup for {folder_path}")
            self.cleanup_triggered.emit({
                'type': 'weekly',
                'folder': folder_path,
                'rules': rules,
                'time': datetime.now()
            })

        # Mapping of lowercase weekday names to schedule library methods
        day_methods = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday
        }

        if day.lower() in day_methods:
            job_id = day_methods[day.lower()].at(time_str).do(job)
            self.scheduled_jobs.append({
                'id': job_id,
                'type': 'weekly',
                'day': day,
                'time': time_str,
                'folder': folder_path
            })

    def start(self):
        """Start the scheduler loop in a daemon thread."""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.scheduler_thread.start()
            self.logger.log_action("Scheduler", "Started scheduler service")

    def stop(self):
        """Stop the scheduler and clear scheduled jobs."""
        self.running = False
        schedule.clear()
        self.scheduled_jobs.clear()
        self.logger.log_action("Scheduler", "Stopped scheduler service")

    def run_scheduler(self):
        """Loop that runs pending scheduled jobs at short intervals."""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def get_scheduled_jobs(self):
        """Return a copy of scheduled job descriptors."""
        return self.scheduled_jobs.copy()

    def cancel_job(self, job_id):
        """Cancel and remove a scheduled job by `job_id`."""
        schedule.cancel_job(job_id)
        self.scheduled_jobs = [job for job in self.scheduled_jobs if job['id'] != job_id]