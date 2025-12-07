import schedule
import time
import threading
from datetime import datetime
from PyQt5.QtCore import QObject, pyqtSignal


class Scheduler(QObject):
    """Background scheduler for automated cleanups"""

    cleanup_triggered = pyqtSignal(dict)  # Emit when scheduled cleanup runs

    def __init__(self, settings, logger):
        super().__init__()
        self.settings = settings
        self.logger = logger
        self.scheduled_jobs = []
        self.running = False

    def schedule_daily_cleanup(self, time_str, folder_path, rules):
        """Schedule a daily cleanup"""

        def job():
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
        """Schedule a weekly cleanup"""

        def job():
            self.logger.log_action("Scheduled", f"Weekly cleanup for {folder_path}")
            self.cleanup_triggered.emit({
                'type': 'weekly',
                'folder': folder_path,
                'rules': rules,
                'time': datetime.now()
            })

        # Map day string to schedule method
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
        """Start the scheduler in a background thread"""
        if not self.running:
            self.running = True
            self.scheduler_thread = threading.Thread(target=self.run_scheduler, daemon=True)
            self.scheduler_thread.start()
            self.logger.log_action("Scheduler", "Started scheduler service")

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        schedule.clear()
        self.scheduled_jobs.clear()
        self.logger.log_action("Scheduler", "Stopped scheduler service")

    def run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def get_scheduled_jobs(self):
        """Get all scheduled jobs"""
        return self.scheduled_jobs.copy()

    def cancel_job(self, job_id):
        """Cancel a specific job"""
        schedule.cancel_job(job_id)
        self.scheduled_jobs = [job for job in self.scheduled_jobs if job['id'] != job_id]