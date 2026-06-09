import hashlib
import io
import mimetypes
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:  # pragma: no cover
    Image = None
    UnidentifiedImageError = Exception

MAX_UPLOAD_SIZE = 20 * 1024 * 1024
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp', 'pdf'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'webp'}
ALLOWED_MIME_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
    'application/pdf',
}


def get_extension(filename):
    filename = filename.strip().lower()
    if '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[-1]


def _normalize_filename(filename):
    filename = filename.replace('\\', '/').split('/')[-1]
    return filename.strip().replace('\x00', '')


def validate_filename(filename):
    normalized = _normalize_filename(filename)
    if normalized != filename:
        raise ValidationError(_('Nombre de archivo inválido.'))
    if filename.startswith('.'):
        raise ValidationError(_('Nombre de archivo inválido.'))
    if filename.count('.') != 1:
        raise ValidationError(_('El nombre de archivo no puede contener doble extensión.'))
    return normalized


def validate_content_type(uploaded_file, extension):
    content_type = getattr(uploaded_file, 'content_type', None)
    guessed_type, _ = mimetypes.guess_type(uploaded_file.name)
    if content_type:
        normalized = content_type.split(';')[0].strip().lower()
    else:
        normalized = guessed_type

    if normalized is None:
        raise ValidationError(_('No se pudo determinar el tipo MIME del archivo.'))
    if normalized not in ALLOWED_MIME_TYPES:
        raise ValidationError(_('Tipo de archivo no permitido: %(mime)s.'), params={'mime': normalized})

    if extension in ALLOWED_IMAGE_EXTENSIONS and not normalized.startswith('image/'):
        raise ValidationError(_('El archivo debe ser una imagen válida.'))
    if extension == 'pdf' and normalized != 'application/pdf':
        raise ValidationError(_('El archivo debe ser un PDF válido.'))


def calculate_sha256(uploaded_file):
    uploaded_file.seek(0)
    sha = hashlib.sha256()
    for chunk in uploaded_file.chunks():
        sha.update(chunk)
    uploaded_file.seek(0)
    return sha.hexdigest()


def validate_uploaded_file(uploaded_file):
    if uploaded_file is None:
        return

    filename = _normalize_filename(uploaded_file.name)
    extension = get_extension(filename)

    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(_('Extensión no permitida: %(ext)s.'), params={'ext': extension})

    validate_filename(filename)

    if uploaded_file.size > MAX_UPLOAD_SIZE:
        limit = MAX_UPLOAD_SIZE // (1024 * 1024)
        raise ValidationError(_('El archivo excede el tamaño máximo de %(size)d MB.'), params={'size': limit})

    validate_content_type(uploaded_file, extension)

    if extension in ALLOWED_IMAGE_EXTENSIONS:
        if Image is None:
            raise ValidationError(_('Pillow no está instalado y es necesario para procesar imágenes.'))
        try:
            image_data = uploaded_file.read()
            uploaded_file.seek(0)
            image = Image.open(io.BytesIO(image_data))
            image.verify()
            uploaded_file.seek(0)
        except UnidentifiedImageError:
            raise ValidationError(_('La imagen está corrupta o no es válida.'))
        except Exception:
            raise ValidationError(_('No se pudo validar la imagen.'))
