import re


def identify_document(text):
    text_upper = text.upper()

    # Passport
    if "PASSPORT" in text_upper:
        return "Passport"

    # Driving Licence
    if (
        "DRIVING LICENCE" in text_upper
        or "DRIVING LICENSE" in text_upper
        or "DL NO" in text_upper
        or "LICENCE NO" in text_upper
    ):
        return "Driving Licence"

    # Visa
    if (
        "VISA" in text_upper
        or "ENTRY PERMIT" in text_upper
        or "STAY DURATION" in text_upper
    ):
        return "Visa"

    # ID card
    if (
        "AADHAAR" in text_upper
        or "UNIQUE IDENTIFICATION" in text_upper
        or "DEMO ID CARD" in text_upper
        or "IDENTITY CARD" in text_upper
        or "ID CARD" in text_upper
    ):
        return "Aadhaar / ID"

    return "Unknown"


def find_date(text):
    patterns = [
        r"\b\d{2}[/-]\d{2}[/-]\d{4}\b",
        r"\b\d{4}[/-]\d{2}[/-]\d{2}\b"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group()

    return None


def find_number(text):

    patterns = [

        # Demo passport number
        r"\b[A-Z]\d{7}\b",

        # Demo ID
        r"\bDEMO-\d{4}-\d{4}\b",

        # Demo driving licence
        r"\bDL-DEMO-\d{5}\b",

        # Demo visa
        r"\bVISA-DEMO-\d{5}\b",

        # General alphanumeric number
        r"\b[A-Z]{1,3}[- ]?[A-Z0-9]{4,12}\b",

        # 12 digit number
        r"\b\d{4}[- ]?\d{4}[- ]?\d{4}\b",

        # 8–12 digit number
        r"\b\d{8,12}\b"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            text.upper()
        )

        if match:
            return match.group()

    return None


def validate_document(
    document_type,
    text
):

    text_upper = text.upper()

    checks = {}
    reasons = []

    # =====================================================
    # PASSPORT
    # =====================================================

    if document_type == "Passport":

        checks["Passport keyword"] = (
            "PASSPORT" in text_upper
        )

        checks["Name present"] = bool(
            re.search(
                r"\bNAME\b",
                text_upper
            )
        )

        checks["Date present"] = bool(
            find_date(text)
        )

        checks["Passport number pattern"] = bool(
            re.search(
                r"\b[A-Z][A-Z0-9]{5,9}\b",
                text_upper
            )
        )

        checks["Nationality present"] = (
            "NATIONALITY" in text_upper
        )

    # =====================================================
    # DRIVING LICENCE
    # =====================================================

    elif document_type == "Driving Licence":

        checks["Driving licence keyword"] = (
            "DRIVING LICENCE" in text_upper
            or
            "DRIVING LICENSE" in text_upper
        )

        checks["Name present"] = (
            "NAME" in text_upper
        )

        checks["Date present"] = bool(
            find_date(text)
        )

        checks["Licence number pattern"] = bool(
            find_number(text)
        )

        checks["Validity information"] = (
            "VALID" in text_upper
            or
            "EXPIRY" in text_upper
            or
            "VALIDITY" in text_upper
        )

    # =====================================================
    # VISA
    # =====================================================

    elif document_type == "Visa":

        checks["Visa keyword"] = (
            "VISA" in text_upper
        )

        checks["Date present"] = bool(
            find_date(text)
        )

        checks["Visa number pattern"] = bool(
            find_number(text)
        )

        checks["Entry information"] = (
            "ENTRY" in text_upper
            or
            "ENTRY TYPE" in text_upper
            or
            "ENTRIES" in text_upper
        )

    # =====================================================
    # ID CARD
    # =====================================================

    elif document_type == "Aadhaar / ID":

        checks["Identification keyword"] = (
            "AADHAAR" in text_upper
            or
            "UNIQUE IDENTIFICATION" in text_upper
            or
            "DEMO ID CARD" in text_upper
            or
            "IDENTITY CARD" in text_upper
            or
            "ID CARD" in text_upper
        )

        checks["Name present"] = (
            "NAME" in text_upper
        )

        checks["Date present"] = bool(
            find_date(text)
        )

        checks["ID number pattern"] = bool(
            re.search(
                r"\bDEMO-\d{4}-\d{4}\b",
                text_upper
            )
            or
            re.search(
                r"\b\d{4}\s?\d{4}\s?\d{4}\b",
                text_upper
            )
        )

    # =====================================================
    # UNKNOWN
    # =====================================================

    else:

        checks[
            "Recognized document type"
        ] = False

        reasons.append(
            "The document type could not be recognized."
        )

        return (
            checks,
            False,
            reasons
        )

    # =====================================================
    # FAILED CHECKS
    # =====================================================

    failed_checks = [
        name
        for name, passed in checks.items()
        if not passed
    ]

    for check in failed_checks:

        reasons.append(
            f"Validation check failed: {check}"
        )

    valid = (
        len(failed_checks) == 0
    )

    return (
        checks,
        valid,
        reasons
    )