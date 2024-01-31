from PIL import Image
from django.core.exceptions import ValidationError
def validate_icon_size(image):
    if image:
        with Image.open(image) as img:
            if img.width > 70 or img.height > 70:
                raise ValidationError(
                    f"The maximum allowed dimensions for the image are 70x70 - size of image you uploded {img.size}"
                )