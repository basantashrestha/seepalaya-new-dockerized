from django.test import TestCase
from courses_apps.account.models import PortalUser, ProfilePicture, UserRoles

class PortalUserModelTests(TestCase):

    def setUp(self):
        self.profile_picture = ProfilePicture.objects.create(
            link="http://example.com/image.jpg"
        )

        self.role1 = UserRoles.objects.create(name="Role1")
        self.role2 = UserRoles.objects.create(name="Role2")

        self.user = PortalUser.objects.create_user(
            username="user1",
            email="user1@example.com",
            password="password",
            full_name="User One",
            address="123 Main St",
            is_verified=True,
            profile_picture=self.profile_picture
        )
        self.user.roles.add(self.role1, self.role2)

    def test_user_creation(self):
        self.assertEqual(self.user.username, "user1")
        self.assertEqual(self.user.email, "user1@example.com")
        self.assertEqual(self.user.full_name, "User One")
        self.assertEqual(self.user.address, "123 Main St")
        self.assertTrue(self.user.is_verified)
        self.assertEqual(self.user.profile_picture, self.profile_picture)
        self.assertIn(self.role1, self.user.roles.all())
        self.assertIn(self.role2, self.user.roles.all())

    def test_string_representation(self):
        self.assertEqual(str(self.user), "user1")

    def test_get_full_name(self):
        self.assertEqual(self.user.get_full_name(), "User One")

    def test_verbose_name(self):
        self.assertEqual(PortalUser._meta.verbose_name, "user")
        self.assertEqual(PortalUser._meta.verbose_name_plural, "users")

