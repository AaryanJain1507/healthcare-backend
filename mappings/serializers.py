from rest_framework import serializers
from patients.models import Patient
from patients.serializers import PatientSerializer
from doctors.models import Doctor
from doctors.serializers import DoctorSerializer
from .models import PatientDoctorMapping


class PatientDoctorMappingSerializer(serializers.ModelSerializer):
    patient = serializers.PrimaryKeyRelatedField(queryset=Patient.objects.all())
    doctor = serializers.PrimaryKeyRelatedField(queryset=Doctor.objects.all())

    class Meta:
        model = PatientDoctorMapping
        fields = ('id', 'patient', 'doctor', 'assigned_at')
        read_only_fields = ('id', 'assigned_at')

    def to_internal_value(self, data):
        # Support both 'patient' / 'patient_id' and 'doctor' / 'doctor_id' in request body
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        if 'patient_id' in mutable_data and 'patient' not in mutable_data:
            mutable_data['patient'] = mutable_data['patient_id']
        if 'doctor_id' in mutable_data and 'doctor' not in mutable_data:
            mutable_data['doctor'] = mutable_data['doctor_id']
        return super().to_internal_value(mutable_data)

    def validate(self, attrs):
        request = self.context.get('request')
        patient = attrs.get('patient')
        doctor = attrs.get('doctor')

        # The patient must belong to the request user
        if patient and request and patient.created_by != request.user:
            raise serializers.ValidationError({
                "patient": "You can only assign doctors to patients created by you."
            })

        # Reject duplicates with a clear error
        if patient and doctor and PatientDoctorMapping.objects.filter(patient=patient, doctor=doctor).exists():
            raise serializers.ValidationError({
                "detail": "A mapping for this patient and doctor already exists."
            })

        return attrs

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['patient_details'] = PatientSerializer(instance.patient).data
        rep['doctor_details'] = DoctorSerializer(instance.doctor).data
        return rep
