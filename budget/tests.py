from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import os, json

# ============================================================
# Epic 1 — User Accounts & Profile Management (Kanyinsola)
# ============================================================
class UserAccountTest(TestCase):
    def test_user_can_register_and_login(self):
        # Create a test user
        user = User.objects.create_user(username="family_user", password="test1234")

        # Verify the user was created
        self.assertEqual(user.username, "family_user")
        self.assertTrue(user.check_password("test1234"))

        # Try logging in through Django's test client
        login_successful = self.client.login(username="family_user", password="test1234")
        self.assertTrue(login_successful)


# ============================================================
# Epic 2 — Income Management (Aryan)
# Per-user JSON data storage test
# ============================================================
class UserDataStorageTest(TestCase):
    def setUp(self):
        self.client = Client()

    def tearDown(self):
        # Clean up JSON files created by tests
        for file in os.listdir('.'):
            if file.endswith('_data.json'):
                os.remove(file)

    def _login(self, username):
        # Simulate login
        resp = self.client.post(reverse("login"), {"username": username})
        self.assertEqual(resp.status_code, 302)

    def _read_json(self, filename):
        with open(filename, "r") as f:
            return json.load(f)

    def test_data_is_separate_per_user(self):
        # First user
        self._login("Aryan")
        self.client.post(reverse("add_income"), {"source": "Job", "amount": "100"})
        aryan_data = self._read_json("Aryan_data.json")
        self.assertEqual(aryan_data["total_income"], 100)

        # Second user
        self._login("Jamie")
        self.client.post(reverse("add_income"), {"source": "Gift", "amount": "200"})
        jamie_data = self._read_json("Jamie_data.json")
        self.assertEqual(jamie_data["total_income"], 200)

        # Aryan's income should remain unchanged
        aryan_data = self._read_json("Aryan_data.json")
        self.assertEqual(aryan_data["total_income"], 100)
