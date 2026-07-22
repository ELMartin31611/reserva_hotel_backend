from pathlib import Path

from django.core.exceptions import ValidationError


MAX_IMAGE_SIZE = 2 * 1024 * 1024

ALLOWED_IMAGE_EXTENSIONS = {
    '.jpg',
    '.jpeg',
    '.png',
    '.webp',
}

ALLOWED_IMAGE_CONTENT_TYPES = {
    'image/jpeg',
    'image/png',
    'image/webp',
}

MAX_VIDEO_SIZE = 50 * 1024 * 1024
ALLOWED_VIDEO_EXTENSIONS = {'.mp4', '.webm'}
ALLOWED_VIDEO_CONTENT_TYPES = {'video/mp4', 'video/webm'}


def validate_image_file(image):
    if image is None:
        return

    if image.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            'La imagen no puede superar los 2 MB.'
        )

    extension = Path(image.name).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(
            'Formato no permitido. Usa JPG, JPEG, PNG o WebP.'
        )

    content_type = getattr(image, 'content_type', None)

    if (
        content_type is not None
        and content_type not in ALLOWED_IMAGE_CONTENT_TYPES
    ):
        raise ValidationError(
            'El archivo seleccionado no es una imagen válida.'
        )


def validate_hotel_media_file(media):
    if media is None:
        return

    extension = Path(media.name).suffix.lower()
    content_type = getattr(media, 'content_type', None)

    if extension in ALLOWED_IMAGE_EXTENSIONS:
        return validate_image_file(media)

    if extension not in ALLOWED_VIDEO_EXTENSIONS:
        raise ValidationError(
            'Usa imágenes JPG, PNG, WebP o videos MP4/WebM.'
        )

    if media.size > MAX_VIDEO_SIZE:
        raise ValidationError(
            'El video no puede superar los 50 MB.'
        )

    if (
        content_type is not None
        and content_type not in ALLOWED_VIDEO_CONTENT_TYPES
    ):
        raise ValidationError(
            'El archivo seleccionado no es un video válido.'
        )