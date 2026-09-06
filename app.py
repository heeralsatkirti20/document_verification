from flask import Flask, render_template, request, jsonify
from ocr import extract_text
from risk_score import calculate_risk_score
from verification import (
    identify_document,
    verify_passport,
    validate_passport,
    verify_aadhaar,
    verify_driving_licence
)
from tampering import detect_tampering
from face_verification import verify_face_match
import os

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/verify", methods=["POST"])
def verify():

    if "document" not in request.files:
        return jsonify({
            "success": False,
            "message": "No document uploaded."
        })

    if "livephoto" not in request.files:
        return jsonify({
            "success": False,
            "message": "No live/selfie photo uploaded."
        })

    document = request.files["document"]
    live_photo = request.files["livephoto"]

    if document.filename == "":
        return jsonify({
            "success": False,
            "message": "Please select a document."
        })

    if live_photo.filename == "":
        return jsonify({
            "success": False,
            "message": "Please select a live/selfie photo."
        })

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        document.filename
    )

    document.save(file_path)

    live_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        live_photo.filename
    )

    live_photo.save(live_path)

    extracted_text = extract_text(file_path)

    document_type = identify_document(extracted_text)
    checks = {}
    verified = False

    if document_type == "Passport":

        checks, verified = verify_passport(extracted_text)

        format_checks, format_verified = validate_passport(
        extracted_text
        )

        checks.update(format_checks)

        verified = verified and format_verified

    elif document_type == "Aadhaar":

        checks, verified = verify_aadhaar(extracted_text)


    elif document_type == "Driving Licence":

        checks, verified = verify_driving_licence(extracted_text)

    tampering_checks, tampering_suspected, ela_image_path = detect_tampering(
        file_path
    )

    face_checks, face_match = verify_face_match(file_path, live_path)

    risk_result = calculate_risk_score(
    document_verified=verified,
    tampering_suspected=tampering_suspected,
    face_match=face_match
)
    
    return jsonify({
    "success": True,
    "document_type": document_type,
    "checks": checks,
    "verified": verified,
    "text": extracted_text,
    "tampering_checks": tampering_checks,
    "tampering_suspected": tampering_suspected,
    "face_checks": face_checks,
    "face_match": face_match,
    "risk_score": risk_result["risk_score"],
    "risk_level": risk_result["risk_level"],
    "risk_reasons": risk_result["reasons"]
})


if __name__ == "__main__":
    app.run(debug=True)