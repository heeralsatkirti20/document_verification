import os
import uuid
import traceback

from flask import (
    Flask,
    render_template,
    request,
    jsonify
)

from ocr import extract_text

from verification import (
    identify_document,
    validate_document
)

from tampering import (
    detect_tampering
)

from risk_score import (
    calculate_risk_score
)

from database import (
    init_db,
    is_blacklisted,
    save_log,
    get_all_logs
)

from face_verification import (
    compare_faces
)


# =========================================================
# FLASK APP
# =========================================================

app = Flask(__name__)


# =========================================================
# FOLDERS
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

UPLOAD_FOLDER = os.path.join(
    BASE_DIR,
    "uploads"
)

REFERENCE_FOLDER = os.path.join(
    BASE_DIR,
    "reference_docs"
)


os.makedirs(
    UPLOAD_FOLDER,
    exist_ok=True
)

os.makedirs(
    REFERENCE_FOLDER,
    exist_ok=True
)


app.config[
    "UPLOAD_FOLDER"
] = UPLOAD_FOLDER


app.config[
    "MAX_CONTENT_LENGTH"
] = 10 * 1024 * 1024


# =========================================================
# REFERENCE DOCUMENTS
# =========================================================

REFERENCE_DOCUMENTS = {

    "Passport":
        os.path.join(
            REFERENCE_FOLDER,
            "demo_passport.png"
        ),

    "Aadhaar / ID":
        os.path.join(
            REFERENCE_FOLDER,
            "demo_id.png"
        ),

    "Visa":
        os.path.join(
            REFERENCE_FOLDER,
            "demo_visa.png"
        ),

    "Driving Licence":
        os.path.join(
            REFERENCE_FOLDER,
            "demo_dl.png"
        )
}


# =========================================================
# DATABASE
# =========================================================

init_db()


# =========================================================
# HOME
# =========================================================

@app.route("/")
def home():

    return render_template(
        "index.html"
    )


# =========================================================
# SCREEN DOCUMENT
# =========================================================

@app.route(
    "/screen",
    methods=["POST"]
)
def screen_document():

    try:

        # -------------------------------------------------
        # DOCUMENT UPLOAD CHECK
        # -------------------------------------------------

        if "document" not in request.files:

            return jsonify({
                "success": False,
                "message":
                    "No document was uploaded."
            }), 400


        document = request.files[
            "document"
        ]


        if document.filename == "":

            return jsonify({
                "success": False,
                "message":
                    "Please select a document."
            }), 400


        # -------------------------------------------------
        # ALLOWED IMAGE TYPES
        # -------------------------------------------------

        allowed_extensions = {
            ".jpg",
            ".jpeg",
            ".png"
        }


        original_name = (
            document.filename
        )


        extension = os.path.splitext(
            original_name
        )[1].lower()


        if extension not in allowed_extensions:

            return jsonify({
                "success": False,
                "message":
                    "Only JPG, JPEG and PNG files are allowed."
            }), 400


        # -------------------------------------------------
        # SAVE DOCUMENT
        # -------------------------------------------------

        unique_filename = (
            "document_"
            + str(uuid.uuid4())
            + extension
        )


        file_path = os.path.join(
            UPLOAD_FOLDER,
            unique_filename
        )


        document.save(
            file_path
        )


        print("\n")
        print("=" * 70)
        print("DOCUMENT SCREENING")
        print("=" * 70)


        print(
            "Uploaded file:"
        )

        print(
            file_path
        )


        # =================================================
        # OCR
        # =================================================

        extracted_text = extract_text(
            file_path
        )


        print("\nOCR TEXT:")
        print(
            extracted_text
        )


        # =================================================
        # DOCUMENT CLASSIFICATION
        # =================================================

        document_type = identify_document(
            extracted_text
        )


        print(
            "\nDocument Type:",
            document_type
        )


        # =================================================
        # DOCUMENT VALIDATION
        # =================================================

        (
            validation_checks,
            document_verified,
            validation_reasons
        ) = validate_document(
            document_type,
            extracted_text
        )


        # =================================================
        # REFERENCE DOCUMENT
        # =================================================

        reference_path = (
            REFERENCE_DOCUMENTS.get(
                document_type
            )
        )


        print("\nREFERENCE FILE:")


        if reference_path:

            print(
                reference_path
            )

            if os.path.exists(
                reference_path
            ):

                print(
                    "REFERENCE STATUS: FOUND"
                )

            else:

                print(
                    "REFERENCE STATUS: NOT FOUND"
                )

                reference_path = None

        else:

            print(
                "No reference document configured."
            )


        if reference_path:

            print(
                "REFERENCE COMPARISON: ENABLED"
            )

        else:

            print(
                "REFERENCE COMPARISON: DISABLED"
            )


        # =================================================
        # TAMPERING ANALYSIS
        # =================================================

        (
            tampering_checks,
            tampering_suspected,
            tampering_reasons
        ) = detect_tampering(
            file_path,
            reference_path
        )


        print("\nTAMPERING RESULTS:")


        print(
            "Reference Available:",
            tampering_checks.get(
                "Reference Comparison Available"
            )
        )


        print(
            "Reference Difference:",
            tampering_checks.get(
                "Reference Difference"
            )
        )


        print(
            "Changed Pixel Percentage:",
            tampering_checks.get(
                "Changed Pixel Percentage"
            )
        )


        print(
            "Reference Tampering:",
            tampering_checks.get(
                "Reference Tampering Detected"
            )
        )


        print(
            "Tampering Suspected:",
            tampering_suspected
        )


        # =================================================
        # BLACKLIST
        # =================================================

        (
            blacklisted,
            blacklist_match
        ) = is_blacklisted(
            extracted_text
        )


        # =================================================
        # RISK SCORE
        # =================================================

        risk_result = calculate_risk_score(

            document_verified=
                document_verified,

            tampering_suspected=
                tampering_suspected,

            blacklisted=
                blacklisted,

            tampering_reasons=
                tampering_reasons
        )


        all_reasons = list(
            risk_result[
                "reasons"
            ]
        )


        if blacklisted:

            all_reasons.append(
                "Matched demo blacklist identifier: "
                + str(
                    blacklist_match
                )
            )


        # =================================================
        # OPTIONAL FACE VERIFICATION
        # =================================================

        face_result = {

            "available": False,

            "match": False,

            "similarity": 0,

            "message":
                "Face verification was not requested."
        }


        live_photo = request.files.get(
            "livephoto"
        )


        if (
            live_photo
            and
            live_photo.filename
        ):

            live_extension = os.path.splitext(
                live_photo.filename
            )[1].lower()


            if live_extension not in allowed_extensions:

                return jsonify({

                    "success": False,

                    "message":
                        "Live photo must be JPG, JPEG or PNG."

                }), 400


            live_filename = (
                "live_"
                + str(uuid.uuid4())
                + live_extension
            )


            live_photo_path = os.path.join(
                UPLOAD_FOLDER,
                live_filename
            )


            live_photo.save(
                live_photo_path
            )


            print(
                "\nFACE VERIFICATION:"
            )


            face_result = compare_faces(

                file_path,

                live_photo_path
            )


            print(
                "Face available:",
                face_result[
                    "available"
                ]
            )


            print(
                "Face match:",
                face_result[
                    "match"
                ]
            )


            print(
                "Face similarity:",
                face_result[
                    "similarity"
                ]
            )


        # =================================================
        # SAVE LOG
        # =================================================

        save_log(

            document_type,

            risk_result[
                "risk_level"
            ],

            risk_result[
                "risk_score"
            ],

            all_reasons
        )


        # =================================================
        # FINAL RESULT
        # =================================================

        print("\nFINAL RESULT:")


        print(
            "Risk Score:",
            risk_result[
                "risk_score"
            ]
        )


        print(
            "Risk Level:",
            risk_result[
                "risk_level"
            ]
        )


        print(
            "Tampering:",
            tampering_suspected
        )


        print(
            "Face Verification:",
            face_result
        )


        print(
            "=" * 70
        )


        # =================================================
        # RESPONSE
        # =================================================

        return jsonify({

            "success":
                True,


            "document_type":
                document_type,


            "document_verified":
                document_verified,


            "validation_checks":
                validation_checks,


            "validation_reasons":
                validation_reasons,


            "ocr_text":
                extracted_text,


            "tampering_checks":
                tampering_checks,


            "tampering_suspected":
                tampering_suspected,


            "tampering_reasons":
                tampering_reasons,


            "blacklisted":
                blacklisted,


            "blacklist_match":
                blacklist_match,


            "face_verification":
                face_result,


            "risk_score":
                risk_result[
                    "risk_score"
                ],


            "risk_level":
                risk_result[
                    "risk_level"
                ],


            "risk_reasons":
                all_reasons
        })


    except Exception as error:

        print("\n")
        print("=" * 70)
        print("SCREENING ERROR")
        print("=" * 70)


        traceback.print_exc()


        return jsonify({

            "success":
                False,

            "message":
                "Could not process the uploaded document: "
                + str(error)

        }), 500


# =========================================================
# LOGS
# =========================================================

@app.route("/logs")
def logs():

    all_logs = get_all_logs()


    return render_template(

        "logs.html",

        logs=all_logs
    )


# =========================================================
# RUN SERVER
# =========================================================

if __name__ == "__main__":

    app.run(
        debug=True
    )