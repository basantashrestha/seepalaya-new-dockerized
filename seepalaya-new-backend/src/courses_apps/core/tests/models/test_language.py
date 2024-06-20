from django.test import TestCase
from courses_apps.core.models import Language

class LanguageModelTests(TestCase):

    def test_language_creation(self):
        language = Language.objects.create(
            language="English",
            abbreviation="ENG"
        )

        self.assertEqual(language.language, "English")
        self.assertEqual(language.abbreviation, "ENG")

    def test_string_representation(self):
        language = Language.objects.create(
            language="English",
            abbreviation="ENG"
        )
        self.assertEqual(str(language), "English")

    def test_verbose_name(self):
        self.assertEqual(Language._meta.verbose_name, "Language")
        self.assertEqual(Language._meta.verbose_name_plural, "Language")

