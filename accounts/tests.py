from rest_framework import status
from rest_framework.test import APITestCase


class AuthenticationApiTests(APITestCase):
    register_url = "/api/auth/register/"
    login_url = "/api/auth/login/"

    def setUp(self):
        self.payload = {
            "name": "Alex Patient",
            "email": "alex@example.com",
            "password": "Strong-Passphrase-984!",
        }

    def test_registration_returns_safe_user(self):
        response = self.client.post(self.register_url, self.payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "alex@example.com")
        self.assertNotIn("password", response.data)
        self.assertEqual(response.data["name"], "Alex Patient")

    def test_duplicate_email_is_case_insensitive(self):
        self.client.post(self.register_url, self.payload, format="json")
        duplicate = {**self.payload, "email": "ALEX@EXAMPLE.COM"}
        response = self.client.post(self.register_url, duplicate, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_registration_is_rejected(self):
        for invalid in (
            {**self.payload, "email": "invalid"},
            {**self.payload, "password": "123"},
            {"name": "", "email": "alex@example.com", "password": self.payload["password"]},
        ):
            response = self.client.post(self.register_url, invalid, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_returns_jwt_and_rejects_bad_credentials(self):
        self.client.post(self.register_url, self.payload, format="json")
        response = self.client.post(
            self.login_url,
            {"email": self.payload["email"].upper(), "password": self.payload["password"]},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

        invalid = self.client.post(
            self.login_url,
            {"email": self.payload["email"], "password": "incorrect"},
            format="json",
        )
        self.assertEqual(invalid.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn("incorrect", str(invalid.data))

    def test_access_token_authenticates_protected_api(self):
        self.client.post(self.register_url, self.payload, format="json")
        token = self.client.post(
            self.login_url,
            {"email": self.payload["email"], "password": self.payload["password"]},
            format="json",
        ).data["access"]
        response = self.client.get(
            "/api/patients/",
            HTTP_AUTHORIZATION=f"Bearer {token}",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_protected_api_requires_authentication(self):
        response = self.client.get("/api/patients/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
