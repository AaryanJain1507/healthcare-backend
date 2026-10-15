from rest_framework import generics, permissions
from .models import Doctor
from .serializers import DoctorSerializer


class IsCreatorOrReadOnly(permissions.BasePermission):
    """
    Object-level permission allowing read access to any authenticated user,
    but write/delete access only to the user who created the doctor.
    """
    message = "Only the creator of this doctor profile can modify or delete it."

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.created_by == request.user


class DoctorListCreateView(generics.ListCreateAPIView):
    """
    POST /api/doctors/ : create a doctor, setting created_by to request.user.
    GET /api/doctors/ : list all doctors in the system.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all().order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class DoctorDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET /api/doctors/<id>/ : get doctor details (any authenticated user).
    PUT /api/doctors/<id>/ : update doctor (creator only).
    DELETE /api/doctors/<id>/ : delete doctor (creator only).
    """
    permission_classes = [permissions.IsAuthenticated, IsCreatorOrReadOnly]
    serializer_class = DoctorSerializer
    queryset = Doctor.objects.all()
