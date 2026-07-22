import os
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from learning.models.media_file import MediaFile

def generate_certificate_pdf(certificate):
    """
    Genera un archivo PDF para el certificado y lo guarda como un MediaFile.
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=landscape(A4),
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()

    # Estilos personalizados
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=36,
        textColor=colors.HexColor("#1A56DB"), # Azul JumpUp
        alignment=1, # Center
        spaceAfter=30
    )

    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=18,
        alignment=1,
        spaceAfter=20
    )

    name_style = ParagraphStyle(
        'NameStyle',
        parent=styles['Normal'],
        fontSize=28,
        alignment=1,
        spaceAfter=20,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['Normal'],
        fontSize=14,
        alignment=1,
        leading=18
    )

    elements = []

    # Logo (opcional si existe en static)
    logo_path = os.path.join(settings.BASE_DIR, 'static', 'img', 'logo_jumpup.png')
    if os.path.exists(logo_path):
        img = Image(logo_path, width=4*cm, height=2*cm)
        elements.append(img)

    elements.append(Spacer(1, 2*cm))
    elements.append(Paragraph("CERTIFICADO DE LOGRO", title_style))
    elements.append(Paragraph("Otorgado con orgullo a:", subtitle_style))
    elements.append(Paragraph(f"{certificate.student.get_full_name() or certificate.student.username}", name_style))

    description = (
        f"Por haber completado satisfactoriamente los requisitos del nivel "
        f"<b>{certificate.level}</b> de acuerdo al Marco Común Europeo de Referencia (MCER).<br/><br/>"
        f"Emitido el: {timezone.now().strftime('%d de %B de %Y')}"
    )
    elements.append(Paragraph(description, body_style))

    elements.append(Spacer(1, 3*cm))

    # Código de verificación
    verify_style = ParagraphStyle('VerifyStyle', parent=styles['Normal'], fontSize=10, alignment=1, textColor=colors.grey)
    elements.append(Paragraph(f"Código de Verificación: {certificate.certificate_code}", verify_style))
    elements.append(Paragraph(f"Verificar en: {settings.FRONTEND_URL}/verify/{certificate.certificate_code}", verify_style))

    # Construir PDF
    doc.build(elements)

    # Guardar en MediaFile
    pdf_content = buffer.getvalue()
    buffer.close()

    filename = f"certificate_{certificate.certificate_code}.pdf"

    media_file = MediaFile.objects.create(
        title=f"Certificado {certificate.level} - {certificate.student.username}",
        file=ContentFile(pdf_content, name=filename),
        file_type='pdf',
        owner=certificate.issued_by or certificate.student
    )

    certificate.certificate_file = media_file
    certificate.issued_at = timezone.now()
    certificate.save(update_fields=['certificate_file', 'issued_at'])

    return media_file
