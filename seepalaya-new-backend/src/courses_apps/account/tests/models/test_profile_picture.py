from django.test import TestCase
from courses_apps.account.models import ProfilePicture, UserRoles

class ProfilePictureTestCase(TestCase):
    def setUp(self):
        self.profile_picture = ProfilePicture.objects.create(name='Profile Picture', link='http://example.com/picture.jpg')

    def test_profile_picture_creation(self):
        self.assertEqual(self.profile_picture.name, 'Profile Picture')
        self.assertEqual(self.profile_picture.link, 'http://example.com/picture.jpg')
