# Test written by Kanyinsola (Epic 1: User Accounts & Profile Management)

from django.test import TestCase
from django.contrib.auth.models import User

class UserAccountTest(TestCase):
    def test_user_can_register_and_login(self):
        # ✅ Create a test user
        user = User.objects.create_user(username="family_user", password="test1234")

        # ✅ Verify the user was created
        self.assertEqual(user.username, "family_user")
        self.assertTrue(user.check_password("test1234"))

        # ✅ Try logging in through Django’s test client
        login_successful = self.client.login(username="family_user", password="test1234")
        self.assertTrue(login_successful)
