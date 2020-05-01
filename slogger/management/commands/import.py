from django.core.management.base import BaseCommand, CommandError
from slogger.imports import import_xlsx

class Command(BaseCommand):
    help = 'Imports sleep data from a spreadsheet'

    def add_arguments(self, parser):
        parser.add_argument('file', type=str)
        parser.add_argument('child_id', type=int)

    def handle(self, *args, **options):
        import_xlsx(options['file'], options['child_id'])