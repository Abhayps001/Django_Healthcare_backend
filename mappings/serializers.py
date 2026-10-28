from rest_framework import serializers

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from mappings.models import PatientDoctorMapping
from patients.models import Patient


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "doctor", "created_at")
        read_only_fields = ("id", "created_at")

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            fields["patient"].queryset = Patient.objects.filter(owner=request.user)
        return fields

    def validate(self, attrs):
        patient = attrs["patient"]
        doctor = attrs["doctor"]
        if PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError(
                {"doctor": "This doctor is already assigned to this patient."}
            )
        return attrs


class MappingWithDoctorSerializer(serializers.ModelSerializer):
    doctor = DoctorSerializer(read_only=True)

    class Meta:
        model = PatientDoctorMapping
        fields = ("id", "patient", "doctor", "created_at")
