from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from doctors.models import Doctor
from mappings.models import PatientDoctorMapping
from patients.models import Patient


class MappingApiTests(APITestCase):
    def setUp(self):
        user_model = get_user_model()
        self.user = user_model.objects.create_user(
            email="mapping-owner@example.com", name="Owner", password="Strong-Passphrase-984!"
        )
        self.other_user = user_model.objects.create_user(
            email="mapping-other@example.com", name="Other", password="Strong-Passphrase-984!"
        )
        self.patient = Patient.objects.create(
            owner=self.user,
            name="Riley Patient",
            age=35,
            gender="prefer_not_to_say",
            address="20 Example Street",
            phone_number="5550105",
        )
        self.other_patient = Patient.objects.create(
            owner=self.other_user,
            name="Morgan Patient",
            age=45,
            gender="other",
            address="21 Example Street",
            phone_number="5550106",
        )
        self.doctor = Doctor.objects.create(
            name="Sam Doctor",
            specialization="Neurology",
            email="sam@example.com",
            phone_number="5550107",
        )
        self.client.force_authenticate(self.user)

    def test_create_duplicate_list_and_get_patient_doctors(self):
        payload = {"patient": self.patient.id, "doctor": self.doctor.id}
        created = self.client.post("/api/mappings/", payload, format="json")
        self.assertEqual(created.status_code, status.HTTP_201_CREATED)
        duplicate = self.client.post("/api/mappings/", payload, format="json")
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        listing = self.client.get("/api/mappings/")
        self.assertEqual(listing.status_code, status.HTTP_200_OK)
        self.assertEqual(len(listing.data), 1)
        by_patient = self.client.get(f"/api/mappings/{self.patient.id}/")
        self.assertEqual(by_patient.status_code, status.HTTP_200_OK)
        self.assertEqual(by_patient.data[0]["doctor"]["id"], self.doctor.id)

    def test_invalid_or_unowned_ids_are_rejected(self):
        missing_patient = self.client.post(
            "/api/mappings/", {"patient": 999999, "doctor": self.doctor.id}, format="json"
        )
        self.assertEqual(missing_patient.status_code, status.HTTP_400_BAD_REQUEST)
        missing_doctor = self.client.post(
            "/api/mappings/", {"patient": self.patient.id, "doctor": 999999}, format="json"
        )
        self.assertEqual(missing_doctor.status_code, status.HTTP_400_BAD_REQUEST)
        foreign_patient = self.client.post(
            "/api/mappings/",
            {"patient": self.other_patient.id, "doctor": self.doctor.id},
            format="json",
        )
        self.assertEqual(foreign_patient.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            self.client.get(f"/api/mappings/{self.other_patient.id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )

    def test_mapping_list_and_delete_are_owner_scoped(self):
        mapping = PatientDoctorMapping.objects.create(
            patient=self.patient, doctor=self.doctor
        )
        other_doctor = Doctor.objects.create(
            name="Lee Doctor",
            specialization="Dermatology",
            email="lee@example.com",
            phone_number="5550108",
        )
        foreign_mapping = PatientDoctorMapping.objects.create(
            patient=self.other_patient, doctor=other_doctor
        )
        self.assertEqual(len(self.client.get("/api/mappings/").data), 1)
        self.assertEqual(
            self.client.delete(f"/api/mappings/{foreign_mapping.id}/").status_code,
            status.HTTP_404_NOT_FOUND,
        )
        removed = self.client.delete(f"/api/mappings/{mapping.id}/")
        self.assertEqual(removed.status_code, status.HTTP_204_NO_CONTENT)
        self.assertTrue(Patient.objects.filter(pk=self.patient.pk).exists())
        self.assertTrue(Doctor.objects.filter(pk=self.doctor.pk).exists())

    def test_missing_patient_and_authentication(self):
        self.assertEqual(self.client.get("/api/mappings/999999/").status_code, status.HTTP_404_NOT_FOUND)
        self.client.force_authenticate(user=None)
        self.assertEqual(self.client.get("/api/mappings/").status_code, status.HTTP_401_UNAUTHORIZED)
