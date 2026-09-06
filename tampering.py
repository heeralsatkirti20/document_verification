from PIL import Image, ImageChops, ExifTags
import numpy as np
import os


def error_level_analysis(image_path, save_path="ela_output.png", quality=90):
    """
    Resaves the image at a known JPEG quality and compares it
    to the original. Edited regions usually show up brighter
    in the difference image because they were compressed at a
    different 'generation' than the rest of the photo.
    """

    original = Image.open(image_path).convert("RGB")

    temp_path = "temp_resaved.jpg"
    original.save(temp_path, "JPEG", quality=quality)

    resaved = Image.open(temp_path)

    diff = ImageChops.difference(original, resaved)

    diff_array = np.array(diff)

    # Look at the strongest differences
    pixel_brightness = np.max(diff_array, axis=2)

    # Focus on the strongest 1% of differences
    ela_score = float(np.percentile(pixel_brightness, 99))

    # Make ELA output easier to see
    scale = 10
    visual_diff = diff.point(lambda p: min(255, p * scale))
    visual_diff.save(save_path)

    os.remove(temp_path)

    return ela_score, save_path


def check_metadata(image_path):
    """
    Looks at the image's EXIF metadata for signs of editing
    or missing camera/scanner info.
    """

    checks = {}

    image = Image.open(image_path)

    exif_data = image._getexif() if hasattr(image, "_getexif") else None

    if not exif_data:
        checks["Has Metadata"] = False
        checks["Editing Software Detected"] = False
        return checks

    checks["Has Metadata"] = True

    software_used = None

    for tag_id, value in exif_data.items():
        tag_name = ExifTags.TAGS.get(tag_id, tag_id)

        if tag_name == "Software":
            software_used = str(value)

    suspicious_tools = ["photoshop", "gimp", "snapseed", "picsart"]

    if software_used and any(
        tool in software_used.lower() for tool in suspicious_tools
    ):
        checks["Editing Software Detected"] = True
        checks["Software Name"] = software_used
    else:
        checks["Editing Software Detected"] = False

    return checks


def detect_tampering(image_path):
    """
    Combines ELA + metadata checks into one result,
    matching the same 'checks dict' style as verification.py
    """

    checks = {}

    ela_score, ela_image_path = error_level_analysis(image_path)

    # This threshold is a starting point — you'll likely tune it
    # after testing a few real vs edited images.
    checks["ELA Score"] = round(ela_score, 2)
    checks["Likely Tampered (ELA)"] = ela_score > 15

    metadata_checks = check_metadata(image_path)
    checks.update(metadata_checks)

    tampering_suspected = (
        checks["Likely Tampered (ELA)"]
        or checks.get("Editing Software Detected", False)
    )

    return checks, tampering_suspected, ela_image_path