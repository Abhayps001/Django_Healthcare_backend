from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor


class DoctorApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="doctor-user@example.com", name="User", password="Strong-Passphrase-984!"
        )
        self.client.force_authenticate(self.user)
        self.doctor = Doctor.objects.create(
            name="Taylor Doctor",
            specialization="Cardiology",
            email="taylor@example.com",
            phone_number="5550103",
        )
        self.payload = {
            "name": "Jordan Doctor",
            "specialization": "Pediatrics",
            "email": "jordan@example.com",
            "phone_number": "5550104",
        }

    def test_create_list_retrieve_update_delete(self):
        created = self.client.post("/api/doctors/", self.payload, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.client.get("/api/doctors/").status_code, status.HTTP_200_OK)
        detail = f"/api/doctors/{self.doctor.id}/"
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_200_OK)
        updated = self.client.put(detail, self.payload, format="json")
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["name"], "Jordan Doctor")
        self.assertEqual(self.client.delete(detail).status_code, status.HTTP_204_NO_CONTENT)

    def test_invalid_input_and_unknown_id(self):
        invalid = self.client.post(
            "/api/doctors/", {**self.payload, "email": "bad"}, format="json"
        )
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get("/api/doctors/999999/").status_code, status.HTTP_404_NOT_FOUND)

    def test_all_doctor_endpoints_require_authentication(self):
        self.client.force_authenticate(user=None)
        for method, url in (
            (self.client.get, "/api/doctors/"),
            (self.client.post, "/api/doctors/"),
            (self.client.get, f"/api/doctors/{self.doctor.id}/"),
        ):
            self.assertEqual(method(url).status_code, status.HTTP_401_UNAUTHORIZED)
