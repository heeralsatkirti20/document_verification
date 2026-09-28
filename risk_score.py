def calculate_risk_score(
    document_verified,
    tampering_suspected,
    blacklisted,
    tampering_reasons=None
):

    score = 0

    reasons = []

    # --------------------------------------------------------
    # DOCUMENT VALIDATION
    # --------------------------------------------------------

    if not document_verified:

        score += 30

        reasons.append(
            "One or more document validation checks failed."
        )

    # --------------------------------------------------------
    # TAMPERING
    # --------------------------------------------------------

    if tampering_suspected:

        score += 40

        if tampering_reasons:

            reasons.extend(
                tampering_reasons
            )

        else:

            reasons.append(
                "Possible document tampering detected."
            )

    # --------------------------------------------------------
    # BLACKLIST
    # --------------------------------------------------------

    if blacklisted:

        score += 50

        reasons.append(
            "An identifier matched the demo blacklist."
        )

    # --------------------------------------------------------
    # LIMIT SCORE
    # --------------------------------------------------------

    score = min(
        score,
        100
    )

    # --------------------------------------------------------
    # RISK LEVEL
    # --------------------------------------------------------

    if score < 25:

        level = "LOW"

    elif score < 60:

        level = "MEDIUM"

    else:

        level = "HIGH"

    return {

        "risk_score":
            score,

        "risk_level":
            level,

        "reasons":
            reasons
    }