from django.core.management.base import BaseCommand, CommandError

from football365.models import Call

class Command(BaseCommand):
    help = "Fetch feeds from Football365 and pass to handlers."

    def handle(self, *args, **options):
        pass
