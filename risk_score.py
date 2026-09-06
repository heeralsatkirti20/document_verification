def calculate_risk_score(document_verified, tampering_suspected, face_match):
    """
    Combines results from Module 2 (validation), Module 3 (tampering),
    and Module 4 (face verification) into one overall risk score.

    Higher score = higher risk. Each module contributes points
    only if something looks wrong.
    """

    risk_points = 0
    reasons = []

    # Module 2: Document validation failed
    if not document_verified:
        risk_points += 30
        reasons.append("Document fields/format did not fully validate")

    # Module 3: Tampering suspected
    if tampering_suspected:
        risk_points += 35
        reasons.append("Signs of tampering detected (editing/metadata)")

    # Module 4: Face does not match
    if not face_match:
        risk_points += 35
        reasons.append("Face does not match document photo")

    # Decide risk level based on total points
    if risk_points == 0:
        risk_level = "LOW"
    elif risk_points <= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"

    return {
        "risk_score": risk_points,
        "risk_level": risk_level,
        "reasons": reasons
    }