from rest_framework import serializers
from learning.models import Certificate


class CertificateSerializer(serializers.ModelSerializer):
    """
    Serializer de Certificate para lectura (estudiante y admin).
    """
    student_email  = serializers.EmailField(source='student.email',    read_only=True)
    issued_by_email = serializers.EmailField(source='issued_by.email', read_only=True, default=None)
    level_display  = serializers.CharField(source='get_level_display',  read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    certificate_file = serializers.SerializerMethodField()

    def get_certificate_file(self, obj):
        if obj.certificate_file and obj.certificate_file.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.certificate_file.file.url)
            return obj.certificate_file.file.url
        return None

    class Meta:
        model  = Certificate
        fields = [
            'id',
            'student',
            'student_email',
            'issued_by',
            'issued_by_email',
            'level',
            'level_display',
            'title',
            'description',
            'certificate_code',
            'certificate_file',
            'status',
            'status_display',
            'issued_at',
            'created_at',
        ]
        read_only_fields = ['certificate_code', 'created_at']


class CertificateCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para que un profesor o admin emita un certificado.
    POST /api/certificates/
    """
    class Meta:
        model  = Certificate
        fields = [
            'student',
            'level',
            'title',
            'description',
            'status',
            'issued_at',
        ]

    def validate(self, attrs):
        # Verificar que no exista ya un certificado del mismo nivel para el estudiante
        student = attrs.get('student')
        level   = attrs.get('level')

        if Certificate.objects.filter(student=student, level=level).exists():
            raise serializers.ValidationError(
                f'El estudiante ya tiene un certificado de nivel {level}.'
            )
        return attrs

    def create(self, validated_data):
        from learning.services.email_service import send_certificate_email
        validated_data['issued_by'] = self.context['request'].user
        instance = super().create(validated_data)
        
        # Enviar correo si el estado es 'issued'
        if instance.status == 'issued':
            try:
                send_certificate_email(instance.student, instance)
            except Exception:
                pass
        return instance


class CertificateIssueSerializer(serializers.Serializer):
    """
    Serializer para aprobar (emitir) un certificado pendiente.
    PATCH /api/certificates/{id}/issue/
    """
    issued_at = serializers.DateTimeField(required=False, allow_null=True)

    def save(self, instance, **kwargs):
        from django.utils import timezone
        from learning.services.email_service import send_certificate_email
        instance.status    = 'issued'
        instance.issued_at = self.validated_data.get('issued_at') or timezone.now()
        instance.issued_by = self.context['request'].user
        instance.save(update_fields=['status', 'issued_at', 'issued_by'])
        
        # Enviar correo al emitir
        try:
            send_certificate_email(instance.student, instance)
        except Exception:
            pass
            
        return instance
