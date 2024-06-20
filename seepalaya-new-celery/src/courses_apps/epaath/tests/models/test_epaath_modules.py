from django.test import TestCase
from django.core.exceptions import ValidationError
from courses_apps.epaath.models import EpaathModules
from courses_apps.core.models import Language, Grade, Subject
from django.utils.translation import gettext_lazy as _

class EpaathModulesModelTests(TestCase):

    def setUp(self):
        self.language = Language.objects.create(language="English")
        self.grade = Grade.objects.create(grade="Grade 1")
        self.subject = Subject.objects.create(subject="Mathematics")

    def test_epaathmodule_creation(self):
        module = EpaathModules.objects.create(
            title="Basic Math",
            chapter_id="MATH101",
            abstract="Introduction to basic math concepts",
            thumbnail="http://example.com/thumb.jpg",
            link="http://example.com/module",
            language=self.language,
            grade=self.grade,
            subject=self.subject,
            published="yes"
        )

        self.assertEqual(module.title, "Basic Math")
        self.assertEqual(module.chapter_id, "MATH101")
        self.assertEqual(module.abstract, "Introduction to basic math concepts")
        self.assertEqual(module.thumbnail, "http://example.com/thumb.jpg")
        self.assertEqual(module.link, "http://example.com/module")
        self.assertEqual(module.language, self.language)
        self.assertEqual(module.grade, self.grade)
        self.assertEqual(module.subject, self.subject)
        self.assertEqual(module.published, "yes")

    def test_string_representation(self):
        module = EpaathModules.objects.create(
            title="Advanced Math",
            chapter_id="MATH201",
            abstract="Advanced math concepts",
            thumbnail="http://example.com/thumb.jpg",
            link="http://example.com/module",
            language=self.language,
            grade=self.grade,
            subject=self.subject,
            published="yes"
        )
        self.assertEqual(str(module), "Advanced Math")

    def test_verbose_name(self):
        self.assertEqual(EpaathModules._meta.verbose_name, _("E-Paath Module"))
        self.assertEqual(EpaathModules._meta.verbose_name_plural, _("E-Paath Modules"))

    def test_published_choices(self):
        module = EpaathModules.objects.create(
            title="Science Basics",
            chapter_id="SCI101",
            abstract="Introduction to basic science concepts",
            thumbnail="http://example.com/thumb.jpg",
            link="http://example.com/module",
            language=self.language,
            grade=self.grade,
            subject=self.subject,
            published="no"
        )
        self.assertEqual(module.published, "no")
