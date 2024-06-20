import csv
from django.core.management.base import BaseCommand
from courses_apps.core.models import Language, Subject, Grade
from courses_apps.epaath.models import EpaathModules

class Command(BaseCommand):
    """
    This command imports epaath chapters from a CSV file. The CSV file must have the following columns:
    title, chapter_id, language, language_code, grade, grade_in_symbol, subject, thumbnail, link
    running the command:
        - python manage.py import_epaath path/to/csv/file.csv
    """
    help = 'Import chapters from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The CSV file to import')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        
        with open(csv_file, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Get or create the Language object
                language, created = Language.objects.get_or_create(
                    language=row['language'],
                    defaults={'abbreviation': row['language_code']}
                )
                if not created:
                    # Update the abbreviation if it doesn't match
                    if language.abbreviation != row['language_code']:
                        language.abbreviation = row['language_code']
                        language.save()

                # Get or create the Grade object
                grade, created = Grade.objects.get_or_create(
                    grade=row['grade'],
                    defaults={'in_symbol': row['grade_in_symbol']}
                )
                if not created:
                    # Update the in_symbol if it doesn't match
                    if grade.in_symbol != row['grade_in_symbol']:
                        grade.in_symbol = row['grade_in_symbol']
                        grade.save()

                # Get or create the Subject object
                subject, created = Subject.objects.get_or_create(
                    subject=row['subject']
                )

                chapter = EpaathModules.objects.create(
                    title=row['title'],
                    chapter_id=row['chapter_id'],
                    abstract=None,
                    thumbnail=row['thumbnail'],
                    link=row['link'],
                    language=language,
                    grade=grade,
                    subject=subject,
                    published='yes'
                )
                self.stdout.write(self.style.SUCCESS(f'Successfully created chapter: {chapter.title}'))