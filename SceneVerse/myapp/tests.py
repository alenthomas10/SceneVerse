from django.test import TestCase, Client
from django.urls import reverse
from myapp.models import Register

class BasicAppTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Register.objects.create(
            first_name="Test",
            last_name="User",
            email="testuser@example.com",
            role="artist",
            password="securepassword123"
        )

    def test_user_creation(self):
        self.assertEqual(self.user.first_name, "Test")
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertEqual(str(self.user), "Test User")

    def test_login_page_status(self):
        response = self.client.get('/login/')
        self.assertEqual(response.status_code, 200)


