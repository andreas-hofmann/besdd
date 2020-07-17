from django.core.management.base import BaseCommand, CommandError
from slogger.models import SleepPhase, Child

def total_sleep(child_id):
    duration = 0
    for s in SleepPhase.objects.filter(child_id=child_id):
        duration += s.duration_sec()
    print(f"Total sleep duration: {duration/3600} hours.")

class Command(BaseCommand):
    help = 'Calculates the total sleep time for a child.'

    def add_arguments(self, parser):
        parser.add_argument('child_id', type=int)

    def handle(self, *args, **options):
        total_sleep(options['child_id'])