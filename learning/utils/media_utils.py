import io
import mimetypes
import os
import uuid
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError
from django.utils.text import slugify

from learning.models.validators import (
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_MIME_TYPES,
    calculate_sha256,
    get_extension,
    validate_uploaded_file,
)

try:
    from PIL import Image, UnidentifiedImageError
except ImportError:  # pragma: no cover
    Image = None
    UnidentifiedImageError = Exception


def generate_media_path(instance, filename):
    filename = os.path.basename(filename)
    extension = get_extension(filename)
    return os.path.join(
        'media',
        slugify(str(uuid.uuid4()))[:16],
        f'{uuid.uuid4().hex}.{extension}'
    )


def _read_file_bytes(uploaded_file):
    uploaded_file.seek(0)
    content = uploaded_file.read()
    uploaded_file.seek(0)
    return content


def _normalize_extension(extension):
    return extension.lower().lstrip('.')


def _guess_mime_type(filename, extension):
    guessed, _ = mimetypes.guess_type(filename)
    if guessed:
        return guessed
    if extension == 'pdf':
        return 'application/pdf'
    if extension in ALLOWED_IMAGE_EXTENSIONS:
        return f'image/{extension if extension != "jpg" else "jpeg"}'
    return 'application/octet-stream'


def create_thumbnail(image):
    if Image is None:
        raise ValidationError('Pillow no está disponible. Imposible crear miniaturas.')

    thumbnail = image.copy()
    thumbnail.thumbnail((300, 300), Image.LANCZOS)
    buffer = io.BytesIO()
    thumbnail.save(buffer, format='WEBP', quality=70, method=6)
    buffer.seek(0)
    return buffer.read()


def process_image_bytes(raw_bytes, extension):
    if Image is None:
        raise ValidationError('Pillow no está disponible. Imposible procesar imágenes.')

    source = io.BytesIO(raw_bytes)
    try:
        image = Image.open(source)
        image.verify()
    except UnidentifiedImageError:
        raise ValidationError('La imagen está corrupta o no es válida.')
    except Exception:
        raise ValidationError('No se pudo leer la imagen.')

    source.seek(0)
    image = Image.open(source)
    if image.mode not in ('RGB', 'RGBA'):
        image = image.convert('RGB')

    max_size = (2048, 2048)
    image.thumbnail(max_size, Image.LANCZOS)

    output = io.BytesIO()
    image.save(output, format='WEBP', quality=85, method=6)
    output.seek(0)

    thumbnail_bytes = create_thumbnail(image)
    return {
        'data': output.read(),
        'mime_type': 'image/webp',
        'extension': 'webp',
        'width': image.width,
        'height': image.height,
        'thumbnail_bytes': thumbnail_bytes,
    }


def process_media_file(uploaded_file):
    if uploaded_file is None:
        raise ValidationError('No se proporcionó ningún archivo.')

    validate_uploaded_file(uploaded_file)

    filename = os.path.basename(uploaded_file.name)
    extension = _normalize_extension(get_extension(filename))
    raw_bytes = _read_file_bytes(uploaded_file)
    checksum = calculate_sha256(uploaded_file)
    mime_type = _guess_mime_type(filename, extension)
    size = len(raw_bytes)

    if extension in ALLOWED_IMAGE_EXTENSIONS:
        image_result = process_image_bytes(raw_bytes, extension)
        return {
            'original_name': filename,
            'data': image_result['data'],
            'mime_type': image_result['mime_type'],
            'extension': image_result['extension'],
            'size': size,
            'checksum': checksum,
            'width': image_result['width'],
            'height': image_result['height'],
            'thumbnail': image_result['thumbnail_bytes'],
        }

    return {
        'original_name': filename,
        'data': raw_bytes,
        'mime_type': mime_type,
        'extension': extension,
        'size': size,
        'checksum': checksum,
        'width': None,
        'height': None,
        'thumbnail': None,
    }
