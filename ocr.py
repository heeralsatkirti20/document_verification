import os
import pytesseract
from PIL import Image, ImageEnhance, ImageFilter


def setup_tesseract():
    """
    Automatically checks common Windows installation locations.
    """

    environment_path = os.environ.get("TESSERACT_CMD")

    if environment_path and os.path.exists(environment_path):
        pytesseract.pytesseract.tesseract_cmd = environment_path
        return

    possible_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
    ]

    for path in possible_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            return


setup_tesseract()


def preprocess_image(image):
    """
    Improve the image slightly before OCR.
    """

    image = image.convert("RGB")

    width, height = image.size

    # Upscale smaller documents.
    if width < 1600:
        scale = 1600 / width
        image = image.resize(
            (int(width * scale), int(height * scale))
        )

    image = image.convert("L")

    image = ImageEnhance.Contrast(image).enhance(1.5)

    image = image.filter(ImageFilter.SHARPEN)

    return image


def extract_text(image_path):
    """
    Extract text from a document image.
    """

    try:
        image = Image.open(image_path)

        processed = preprocess_image(image)

        text = pytesseract.image_to_string(
            processed,
            config="--psm 6"
        )

        return text.strip()

    except Exception as error:
        raise RuntimeError(
            f"OCR failed: {str(error)}"
        )