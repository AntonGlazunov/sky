from apscheduler.schedulers.background import BackgroundScheduler
from django.core.management import BaseCommand

from sky_api.services import add_forecast_in_db


class Command(BaseCommand):

    def handle(self, *args, **options):
        sh = BackgroundScheduler()
        sh.add_job(add_forecast_in_db, 'interval', seconds=30)
        sh.start()
        print('Планировщик запущен')