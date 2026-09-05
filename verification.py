import re


def identify_document(text):

    text_lower = text.lower()

    # Aadhaar
    if "aadhaar" in text_lower or "unique identification" in text_lower:
        return "Aadhaar"

    # Passport
    if "passport" in text_lower or "republic of india" in text_lower:
        return "Passport"

    # Driving Licence
    if (
        "driving licence" in text_lower
        or "driving license" in text_lower
    ):
        return "Driving Licence"

    return "Unknown"


def verify_passport(text):

    checks = {}

    # Name
    checks["Name"] = bool(
        re.search(r"name\s*:", text, re.IGNORECASE)
    )

    # Nationality
    checks["Nationality"] = bool(
        re.search(r"nationality\s*:", text, re.IGNORECASE)
    )

    # Date of Birth
    checks["Date of Birth"] = bool(
        re.search(r"date\s+of\s+birth\s*:", text, re.IGNORECASE)
    )

    # Passport Number
    checks["Passport Number"] = bool(
        re.search(r"passport\s*(no|number)\s*:", text, re.IGNORECASE)
    )

    # Place of Birth
    checks["Place of Birth"] = bool(
        re.search(r"place\s+of\s+birth\s*:", text, re.IGNORECASE)
    )

    # Date of Issue
    checks["Date of Issue"] = bool(
        re.search(r"date\s+of\s+issue\s*:", text, re.IGNORECASE)
    )

    # Date of Expiry
    checks["Date of Expiry"] = bool(
        re.search(r"date\s+of\s+expiry\s*:", text, re.IGNORECASE)
    )

    all_valid = all(checks.values())

    return checks, all_valid
def validate_passport(text):

    checks = {}

    # Check passport number
    passport_match = re.search(
        r"passport\s*(no|number)\s*:\s*([A-Z0-9]+)",
        text,
        re.IGNORECASE
    )

    if passport_match:
        passport_number = passport_match.group(2)

        checks["Passport Number Format"] = bool(
            re.fullmatch(r"[A-Z0-9]{6,10}", passport_number)
        )
    else:
        checks["Passport Number Format"] = False


    # Check dates
    date_pattern = r"\d{2}/\d{2}/\d{4}"

    dates = re.findall(date_pattern, text)

    checks["Valid Date Format"] = len(dates) >= 3


    # Final result
    all_valid = all(checks.values())

    return checks, all_valid
def verify_aadhaar(text):

    checks = {}

    # Name
    checks["Name"] = bool(
        re.search(r"name\s*:", text, re.IGNORECASE)
    )

    # Date of Birth
    checks["Date of Birth"] = bool(
        re.search(r"date\s+of\s+birth\s*:", text, re.IGNORECASE)
    )

    # Aadhaar number
    aadhaar_match = re.search(
        r"\b\d{4}\s?\d{4}\s?\d{4}\b",
        text
    )

    checks["Aadhaar Number"] = bool(aadhaar_match)

    all_valid = all(checks.values())

    return checks, all_valid


def verify_driving_licence(text):

    checks = {}

    # Name
    checks["Name"] = bool(
        re.search(r"name\s*:", text, re.IGNORECASE)
    )

    # Date of Birth
    checks["Date of Birth"] = bool(
        re.search(r"date\s+of\s+birth\s*:", text, re.IGNORECASE)
    )

    # Licence number
    licence_match = re.search(
        r"(license|licence)\s*(no|number)\s*:\s*([A-Z0-9-]+)",
        text,
        re.IGNORECASE
    )

    checks["Licence Number"] = bool(licence_match)

    # Validity
    checks["Validity"] = bool(
        re.search(
            r"(valid|expiry|validity)",
            text,
            re.IGNORECASE
        )
    )

    all_valid = all(checks.values())

    return checks, all_valid