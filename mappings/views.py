from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from mappings.models import PatientDoctorMapping
from mappings.serializers import (
    MappingWithDoctorSerializer,
    PatientDoctorMappingSerializer,
)
from patients.models import Patient


class MappingListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientDoctorMappingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(
            patient__owner=self.request.user
        ).select_related("patient", "doctor").order_by("id")

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                serializer.save()
        except IntegrityError as exc:
            raise ValidationError(
                {"doctor": "This doctor is already assigned to this patient."}
            ) from exc


class PatientMappingsView(generics.GenericAPIView):
    serializer_class = MappingWithDoctorSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, patient_id):
        patient = get_object_or_404(Patient, pk=patient_id, owner=request.user)
        mappings = PatientDoctorMapping.objects.filter(
            patient=patient
        ).select_related("doctor").order_by("id")
        return Response(self.get_serializer(mappings, many=True).data)

    def delete(self, request, patient_id):
        mapping = get_object_or_404(
            PatientDoctorMapping.objects.select_related("patient"),
            pk=patient_id,
            patient__owner=request.user,
        )
        mapping.delete()
        return Response(status=204)
