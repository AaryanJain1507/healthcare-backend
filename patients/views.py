from rest_framework import generics, permissions
from .models import Patient
from .serializers import PatientSerializer


class IsOwner(permissions.BasePermission):
    """
    Object-level permission: only the user who created the patient can access or modify it.
    """
    message = "You do not have permission to access or modify this patient record."

    def has_object_permission(self, request, view, obj):
        return obj.created_by == request.user


class PatientListCreateView(generics.ListCreateAPIView):
    """
    POST /api/patients/ : create, set created_by to the request user.
    GET /api/patients/ : list only patients created by the authenticated user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PatientSerializer

    def get_queryset(self):
        return Patient.objects.filter(created_by=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/patients/<id>/
    PUT /api/patients/<id>/
    DELETE /api/patients/<id>/
    Only for the owner; returns 404 if not found or 403 if belonging to another user.
    """
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    serializer_class = PatientSerializer
    queryset = Patient.objects.all()
