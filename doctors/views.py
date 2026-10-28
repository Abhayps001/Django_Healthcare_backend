from rest_framework import generics, permissions

from doctors.models import Doctor
from doctors.serializers import DoctorSerializer


class DoctorListCreateView(generics.ListCreateAPIView):
    queryset = Doctor.objects.all().order_by("id")
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Doctor.objects.all()
    serializer_class = DoctorSerializer
    permission_classes = [permissions.IsAuthenticated]
