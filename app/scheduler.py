from apscheduler.schedulers.background import BackgroundScheduler
from app.sync.routes import sync_to_db_internal
import atexit

def start_scheduler(app):
    scheduler = BackgroundScheduler()

    @scheduler.scheduled_job('interval', seconds=10)
    def job():
        with app.app_context():
            print("[Scheduler] Syncing Google Sheet to DB...")
            sync_to_db_internal()

    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())