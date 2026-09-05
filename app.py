from flask import Flask, render_template, request, jsonify
from ocr import extract_text
from verification import (
    identify_document,
    verify_passport,
    validate_passport,
    verify_aadhaar,
    verify_driving_licence
)
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

    document = request.files["document"]

    if document.filename == "":
        return jsonify({
            "success": False,
            "message": "Please select a document."
        })

    file_path = os.path.join(
        app.config["UPLOAD_FOLDER"],
        document.filename
    )

    document.save(file_path)

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
    return jsonify({
    "success": True,
    "document_type": document_type,
    "checks": checks,
    "verified": verified,
    "text": extracted_text
})


if __name__ == "__main__":
    app.run(debug=True)