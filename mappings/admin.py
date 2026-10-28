from django.contrib import admin

from mappings.models import PatientDoctorMapping


@admin.register(PatientDoctorMapping)
class PatientDoctorMappingAdmin(admin.ModelAdmin):
    list_display = ("id", "patient", "doctor", "created_at")
    list_select_related = ("patient", "doctor")
