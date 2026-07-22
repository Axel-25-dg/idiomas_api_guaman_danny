from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from learning.models import Certificate
from learning.serializers import (
    CertificateSerializer,
    CertificateCreateSerializer,
    CertificateIssueSerializer,
)
from learning.pagination import StandardPagination
from learning.permissions import IsTeacherOrAdmin, IsAdmin, _get_role
from learning.models import ROLE_STUDENT


class CertificateViewSet(viewsets.ModelViewSet):
    """
    Gestión de certificados MCER.

    STUDENT:
      GET  /api/certificates/         — Sus propios certificados
      GET  /api/certificates/{id}/    — Detalle

    TEACHER / ADMIN:
      GET  /api/certificates/         — Todos los certificados (admin) o los emitidos por él
      POST /api/certificates/         — Crear certificado para un estudiante
      PATCH /api/certificates/{id}/issue/  — Emitir (aprobar) un certificado pendiente
      PATCH /api/certificates/{id}/revoke/ — Revocar un certificado

    PÚBLICO:
      GET  /api/certificates/verify/{code}/ — Verificar un certificado por su código único
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class   = StandardPagination
    filter_backends    = [DjangoFilterBackend, OrderingFilter]
    filterset_fields   = ['level', 'status']
    ordering_fields    = ['created_at', 'level']

    def get_serializer_class(self):
        if self.action == 'create':
            return CertificateCreateSerializer
        if self.action == 'issue':
            return CertificateIssueSerializer
        return CertificateSerializer

    def get_queryset(self):
        user = self.request.user
        role = _get_role(user)

        if role == ROLE_STUDENT:
            return Certificate.objects.filter(
                student=user
            ).select_related('issued_by')

        if user.is_superuser:
            return Certificate.objects.select_related(
                'student', 'issued_by'
            ).all()

        # Teacher ve solo los certificados que él emitió
        return Certificate.objects.filter(
            issued_by=user
        ).select_related('student')

    def get_permissions(self):
        if self.action in ('create', 'issue', 'revoke'):
            return [IsTeacherOrAdmin()]
        if self.action == 'verify':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    # ── Acción: emitir certificado pendiente ─────────────────────────────────
    @action(detail=True, methods=['patch'], url_path='issue',
            permission_classes=[IsTeacherOrAdmin])
    def issue(self, request, pk=None):
        """
        PATCH /api/certificates/{id}/issue/
        Cambia status='pending' → 'issued', registra issued_at y genera PDF.
        """
        certificate = self.get_object()
        if certificate.status == 'issued':
            return Response(
                {'detail': 'Este certificado ya fue emitido.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = CertificateIssueSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        certificate = serializer.save(certificate)

        # Generación automática del PDF
        try:
            from learning.utils.certificate_generator import generate_certificate_pdf
            generate_certificate_pdf(certificate)
        except Exception as e:
            # Loguear el error pero no detener la respuesta si el PDF falla
            print(f"Error generando PDF: {e}")

        return Response(
            CertificateSerializer(certificate, context={'request': request}).data
        )

    # ── Acción: revocar certificado ──────────────────────────────────────────
    @action(detail=True, methods=['patch'], url_path='revoke',
            permission_classes=[IsTeacherOrAdmin])
    def revoke(self, request, pk=None):
        """
        PATCH /api/certificates/{id}/revoke/
        Cambia status → 'revoked'.
        """
        certificate = self.get_object()
        if certificate.status == 'revoked':
            return Response(
                {'detail': 'Este certificado ya está revocado.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        certificate.status = 'revoked'
        certificate.save(update_fields=['status'])
        return Response(
            CertificateSerializer(certificate, context={'request': request}).data
        )

    # ── Acción: verificación pública por código ──────────────────────────────
    @action(detail=False, methods=['get'], url_path='verify/(?P<code>[^/.]+)',
            permission_classes=[permissions.AllowAny])
    def verify(self, request, code=None):
        """
        GET /api/certificates/verify/{code}/
        Endpoint público. Devuelve datos básicos del certificado para verificación externa.
        """
        try:
            certificate = Certificate.objects.select_related(
                'student', 'issued_by'
            ).get(certificate_code=code)
        except Certificate.DoesNotExist:
            return Response(
                {'valid': False, 'detail': 'Certificado no encontrado.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({
            'valid':             certificate.status == 'issued',
            'certificate_code':  certificate.certificate_code,
            'student_name':      certificate.student.get_full_name() or certificate.student.username,
            'level':             certificate.level,
            'title':             certificate.title,
            'status':            certificate.status,
            'issued_at':         certificate.issued_at,
            'certificate_file':  request.build_absolute_uri(certificate.certificate_file.file.url) if (certificate.certificate_file and certificate.certificate_file.file) else None,
        })
