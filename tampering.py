import os
import cv2
import numpy as np

from PIL import Image, ImageChops, ImageEnhance
from skimage.metrics import structural_similarity


def calculate_ela(image_path, quality=90):

    original = Image.open(
        image_path
    ).convert("RGB")

    temp_path = os.path.join(
        os.path.dirname(image_path),
        "ela_temp.jpg"
    )

    original.save(
        temp_path,
        "JPEG",
        quality=quality
    )

    compressed = Image.open(
        temp_path
    ).convert("RGB")

    difference = ImageChops.difference(
        original,
        compressed
    )

    extrema = difference.getextrema()

    max_difference = max(
        value[1]
        for value in extrema
    )

    if max_difference == 0:
        max_difference = 1

    scale = 255 / max_difference

    ela_image = ImageEnhance.Brightness(
        difference
    ).enhance(scale)

    ela_array = np.array(
        ela_image
    )

    ela_score = float(
        np.mean(ela_array)
    )

    try:
        os.remove(temp_path)
    except:
        pass

    return round(
        ela_score,
        2
    )


def localized_analysis(image_path):

    image = cv2.imread(
        image_path
    )

    if image is None:

        return {
            "Localized Analysis Available": False,
            "Localized Max Difference": 0,
            "Localized Suspicious": False
        }

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    blurred = cv2.GaussianBlur(
        gray,
        (5, 5),
        0
    )

    difference = cv2.absdiff(
        gray,
        blurred
    )

    height, width = difference.shape

    block_size = 32

    max_difference = 0

    for y in range(
        0,
        height,
        block_size
    ):

        for x in range(
            0,
            width,
            block_size
        ):

            block = difference[
                y:y + block_size,
                x:x + block_size
            ]

            if block.size == 0:
                continue

            block_mean = float(
                np.mean(block)
            )

            if block_mean > max_difference:
                max_difference = block_mean

    return {
        "Localized Analysis Available": True,

        "Localized Max Difference":
            round(
                max_difference,
                2
            ),

        "Localized Suspicious":
            max_difference > 20
    }


def metadata_analysis(image_path):

    try:

        image = Image.open(
            image_path
        )

        metadata = image.getexif()

        software_detected = False
        software_name = None

        if metadata:

            for value in metadata.values():

                if not isinstance(
                    value,
                    str
                ):
                    continue

                value_lower = value.lower()

                editing_software = [
                    "photoshop",
                    "gimp",
                    "snapseed",
                    "picsart"
                ]

                for software in editing_software:

                    if software in value_lower:

                        software_detected = True
                        software_name = software

                        break

                if software_detected:
                    break

        return {

            "Metadata Present":
                bool(metadata),

            "Editing Software Detected":
                software_detected,

            "Editing Software":
                software_name
        }

    except Exception:

        return {

            "Metadata Present": False,

            "Editing Software Detected":
                False,

            "Editing Software":
                None
        }


def reference_comparison(
    image_path,
    reference_path
):

    empty_result = {

        "Reference Comparison Available":
            False,

        "Reference Difference":
            0,

        "Reference Mean Difference":
            0,

        "Changed Pixel Percentage":
            0,

        "Largest Changed Region":
            0,

        "Reference Tampering Detected":
            False
    }

    if not reference_path:

        return empty_result

    if not os.path.exists(
        reference_path
    ):

        return empty_result

    image = cv2.imread(
        image_path
    )

    reference = cv2.imread(
        reference_path
    )

    if image is None or reference is None:

        return empty_result

    # --------------------------------------------------
    # Resize uploaded image to reference dimensions
    # --------------------------------------------------

    image = cv2.resize(
        image,
        (
            reference.shape[1],
            reference.shape[0]
        ),
        interpolation=cv2.INTER_AREA
    )

    # --------------------------------------------------
    # Convert both images to grayscale
    # --------------------------------------------------

    image_gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )

    reference_gray = cv2.cvtColor(
        reference,
        cv2.COLOR_BGR2GRAY
    )

    # --------------------------------------------------
    # Slight blur removes tiny JPEG compression noise
    # --------------------------------------------------

    image_gray = cv2.GaussianBlur(
        image_gray,
        (3, 3),
        0
    )

    reference_gray = cv2.GaussianBlur(
        reference_gray,
        (3, 3),
        0
    )

    # --------------------------------------------------
    # STRUCTURAL SIMILARITY
    #
    # This is much more tolerant of:
    # PNG -> JPEG
    # JPEG compression
    # small image noise
    # slight camera/image processing differences
    # --------------------------------------------------

    similarity_score = structural_similarity(
        reference_gray,
        image_gray,
        data_range=255
    )

    structural_difference = (
        1 - similarity_score
    ) * 100

    # --------------------------------------------------
    # Pixel difference for DISPLAY INFORMATION ONLY
    #
    # We do NOT use raw pixel difference alone to decide
    # whether the document is tampered.
    # --------------------------------------------------

    difference = cv2.absdiff(
        image_gray,
        reference_gray
    )

    # Higher threshold prevents normal JPEG compression
    # from being treated as a meaningful modification.

    _, threshold = cv2.threshold(
        difference,
        45,
        255,
        cv2.THRESH_BINARY
    )

    changed_pixels = np.count_nonzero(
        threshold
    )

    total_pixels = threshold.size

    changed_percentage = (

        changed_pixels /
        total_pixels

        if total_pixels > 0
        else 0
    )

    # --------------------------------------------------
    # Find largest changed region
    # --------------------------------------------------

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    largest_region = 0

    for contour in contours:

        area = cv2.contourArea(
            contour
        )

        if area > largest_region:

            largest_region = area

    # --------------------------------------------------
    # REFERENCE TAMPERING DECISION
    #
    # SSIM is the main signal.
    #
    # 0.985 means 98.5% structural similarity.
    #
    # A normal PNG/JPEG conversion should normally remain
    # highly structurally similar.
    # --------------------------------------------------

    reference_tampering = bool(
        similarity_score < 0.985
    )

    return {

        "Reference Comparison Available":
            True,

        "Reference Difference":
            round(
                structural_difference,
                2
            ),

        "Reference Mean Difference":
            round(
                structural_difference,
                2
            ),

        "Changed Pixel Percentage":
            round(
                changed_percentage * 100,
                2
            ),

        "Largest Changed Region":
            round(
                largest_region,
                2
            ),

        "Reference Tampering Detected":
            reference_tampering
    }


def detect_tampering(
    image_path,
    reference_path=None
):

    ela_score = calculate_ela(
        image_path
    )

    localized = localized_analysis(
        image_path
    )

    metadata = metadata_analysis(
        image_path
    )

    reference = reference_comparison(
        image_path,
        reference_path
    )

    checks = {

        "ELA Score":
            ela_score,

        "Localized Max Difference":
            localized[
                "Localized Max Difference"
            ],

        "Localized Suspicious":
            localized[
                "Localized Suspicious"
            ],

        "Metadata Present":
            metadata[
                "Metadata Present"
            ],

        "Editing Software Detected":
            metadata[
                "Editing Software Detected"
            ],

        "Editing Software":
            metadata[
                "Editing Software"
            ],

        "Reference Comparison Available":
            reference[
                "Reference Comparison Available"
            ],

        "Reference Difference":
            reference[
                "Reference Difference"
            ],

        "Reference Mean Difference":
            reference[
                "Reference Mean Difference"
            ],

        "Changed Pixel Percentage":
            reference[
                "Changed Pixel Percentage"
            ],

        "Largest Changed Region":
            reference[
                "Largest Changed Region"
            ],

        "Reference Tampering Detected":
            reference[
                "Reference Tampering Detected"
            ]
    }

    tampering_reasons = []

    normal_signals = 0

    # --------------------------------------------------
    # ELA
    # --------------------------------------------------

    if ela_score > 15:

        normal_signals += 1

        tampering_reasons.append(
            "Elevated ELA difference detected."
        )

    # --------------------------------------------------
    # Localized analysis
    # --------------------------------------------------

    if localized[
        "Localized Suspicious"
    ]:

        normal_signals += 1

        tampering_reasons.append(
            "Localized image differences detected."
        )

    # --------------------------------------------------
    # Editing software metadata
    # --------------------------------------------------

    if metadata[
        "Editing Software Detected"
    ]:

        normal_signals += 1

        tampering_reasons.append(
            "Image metadata indicates possible editing software."
        )

    # --------------------------------------------------
    # Reference comparison
    # --------------------------------------------------

    reference_signal = reference[
        "Reference Tampering Detected"
    ]

    if reference_signal:

        tampering_reasons.append(
            "Uploaded document differs significantly from the clean demo reference."
        )

    # --------------------------------------------------
    # FINAL TAMPERING DECISION
    # --------------------------------------------------

    tampering_suspected = (

        reference_signal

        or

        normal_signals >= 2
    )

    if tampering_suspected:

        if not tampering_reasons:

            tampering_reasons.append(
                "Possible document tampering detected."
            )

    return (
        checks,
        tampering_suspected,
        tampering_reasons
    )