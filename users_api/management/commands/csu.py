from django.core.management import BaseCommand

from users_api.models import User


class Command(BaseCommand):

    def handle(self, *args, **options):
        user = User.objects.create(
            username='admin',
            is_superuser=True,
            is_staff=True
        )
        user.set_password('200818')
        user.save()