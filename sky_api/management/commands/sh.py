from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import BaseCommand

from config.settings import TIME_ZONE
from sky_api.services import start_async_code


class Command(BaseCommand):

    def handle(self, *args, **options):
        scheduler = BackgroundScheduler(timezone=TIME_ZONE)
        scheduler.add_job(start_async_code, 'interval', seconds=15)
        scheduler.start()