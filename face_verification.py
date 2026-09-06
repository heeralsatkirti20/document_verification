import face_recognition


def extract_face_encoding(image_path):
    """
    Loads an image and returns the face 'encoding' — a set of
    numbers that mathematically describes the face, used for
    comparison. Returns None if no face is found.
    """

    image = face_recognition.load_image_file(image_path)

    face_locations = face_recognition.face_locations(image)

    if len(face_locations) == 0:
        return None

    encodings = face_recognition.face_encodings(
        image,
        known_face_locations=face_locations
    )

    return encodings[0]


def verify_face_match(document_image_path, live_image_path):
    """
    Compares the face on the document to the live/presented photo.
    Returns a checks dict (same style as verification.py) plus a
    match boolean.
    """

    checks = {}

    document_encoding = extract_face_encoding(document_image_path)
    live_encoding = extract_face_encoding(live_image_path)

    if document_encoding is None:
        checks["Face Found on Document"] = False
        return checks, False

    checks["Face Found on Document"] = True

    if live_encoding is None:
        checks["Face Found in Live Photo"] = False
        return checks, False

    checks["Face Found in Live Photo"] = True

    # face_recognition gives a "distance" — LOWER means more similar.
    # 0.6 is the commonly used default threshold.
    face_distance = face_recognition.face_distance(
        [document_encoding],
        live_encoding
    )[0]

    match = bool(face_distance < 0.6)

    checks["Face Match Distance"] = round(float(face_distance), 3)
    checks["Face Match"] = match

    return checks, match