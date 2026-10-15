from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from patients.models import Patient
from doctors.serializers import DoctorSerializer
from .models import PatientDoctorMapping
from .serializers import PatientDoctorMappingSerializer


class MappingListCreateView(generics.ListCreateAPIView):
    """
    POST /api/mappings/ : body has patient and doctor ids. The patient must belong to the request user.
    GET /api/mappings/ : all mappings for the user's patients.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PatientDoctorMappingSerializer

    def get_queryset(self):
        return PatientDoctorMapping.objects.filter(
            patient__created_by=self.request.user
        ).select_related('patient', 'doctor').order_by('-assigned_at')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class MappingPatientOrDetailView(APIView):
    """
    Handles:
    - GET /api/mappings/<patient_id>/ : all doctors assigned to that patient
    - DELETE /api/mappings/<id>/ : remove the mapping (only if the patient belongs to the user)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, pk):
        """Get all doctors assigned to the specified patient_id."""
        patient = Patient.objects.filter(pk=pk).first()
        if not patient:
            return Response(
                {"detail": "Patient not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if patient.created_by != request.user:
            return Response(
                {"detail": "You do not have permission to view mappings for this patient."},
                status=status.HTTP_403_FORBIDDEN
            )

        mappings = PatientDoctorMapping.objects.filter(patient=patient).select_related('doctor')
        doctors = [m.doctor for m in mappings]
        serializer = DoctorSerializer(doctors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        """Remove the mapping by mapping id (only if the patient belongs to the user)."""
        mapping = PatientDoctorMapping.objects.filter(pk=pk).select_related('patient').first()
        if not mapping:
            return Response(
                {"detail": "Mapping not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        if mapping.patient.created_by != request.user:
            return Response(
                {"detail": "You do not have permission to delete this mapping."},
                status=status.HTTP_403_FORBIDDEN
            )

        mapping.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
