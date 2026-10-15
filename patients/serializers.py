from rest_framework import serializers
from .models import Patient


class PatientSerializer(serializers.ModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.id')

    class Meta:
        model = Patient
        fields = (
            'id',
            'created_by',
            'name',
            'age',
            'gender',
            'phone',
            'address',
            'medical_history',
            'created_at',
            'updated_at',
        )
        read_only_fields = ('id', 'created_by', 'created_at', 'updated_at')

    def validate_age(self, value):
        if value <= 0:
            raise serializers.ValidationError("Age must be a positive integer greater than 0.")
        return value
