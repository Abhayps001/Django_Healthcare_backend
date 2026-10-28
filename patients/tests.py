from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from patients.models import Patient


class PatientApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email="owner@example.com", name="Owner", password="Strong-Passphrase-984!"
        )
        self.other_user = user_model.objects.create_user(
            email="other@example.com", name="Other", password="Strong-Passphrase-984!"
        )
        self.patient = Patient.objects.create(
            owner=self.user,
            name="Jamie Sample",
            age=30,
            gender="other",
            address="10 Example Street",
            phone_number="+1 555 0100",
        )
        self.client.force_authenticate(self.user)
        self.payload = {
            "name": "Casey Example",
            "age": 42,
            "gender": "female",
            "address": "11 Example Street",
            "phone_number": "+1 555 0101",
        }

    def test_create_and_list_only_owned_patients(self):
        Patient.objects.create(
            owner=self.other_user,
            name="Private Record",
            age=28,
            gender="male",
            address="Other address",
            phone_number="5550102",
        )
        created = self.client.post(
            "/api/patients/",
            {**self.payload, "owner": self.other_user.id},
            format="json",
        )
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        self.assertEqual(created.data["owner"], self.user.id)
        listed = self.client.get("/api/patients/")
        self.assertEqual(listed.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listed.data), 2)

    def test_retrieve_update_delete_owned_patient(self):
        detail = f"/api/patients/{self.patient.id}/"
        self.assertEqual(self.client.get(detail).status_code, status.HTTP_200_OK)
        updated = self.client.put(detail, self.payload, format="json")
        self.assertEqual(updated.status_code, status.HTTP_200_OK)
        self.assertEqual(updated.data["name"], "Casey Example")
        deleted = self.client.delete(detail)
        self.assertEqual(deleted.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Patient.objects.filter(pk=self.patient.pk).exists())

    def test_other_users_patient_is_not_accessible(self):
        self.client.force_authenticate(self.other_user)
        detail = f"/api/patients/{self.patient.id}/"
        for response in (
            self.client.get(detail),
            self.client.put(detail, self.payload, format="json"),
            self.client.delete(detail),
        ):
            self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_invalid_patient_payload_and_missing_id(self):
        invalid = self.client.post(
            "/api/patients/", {**self.payload, "age": -1}, format="json"
        )
        self.assertEqual(invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get("/api/patients/999999/").status_code, status.HTTP_404_NOT_FOUND)
