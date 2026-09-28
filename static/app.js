document.addEventListener("DOMContentLoaded", function () {

    // =========================================================
    // ELEMENTS FROM YOUR CURRENT index.html
    // =========================================================

    const form = document.getElementById("screenForm");

    const documentInput =
        document.getElementById("documentInput");

    const dropZone =
        document.getElementById("dropZone");

    const uploadContent =
        document.getElementById("uploadContent");

    const selectedFile =
        document.getElementById("selectedFile");

    const fileName =
        document.getElementById("fileName");

    const fileSize =
        document.getElementById("fileSize");

    const removeFile =
        document.getElementById("removeFile");

    const screenButton =
        document.getElementById("screenButton");

    const scanningCard =
        document.getElementById("scanningCard");

    const resultsSection =
        document.getElementById("resultsSection");

    const errorBox =
        document.getElementById("errorBox");

    const newScreening =
        document.getElementById("newScreening");

    const progressBar =
        document.getElementById("progressBar");

    const scanPercent =
        document.getElementById("scanPercent");

    const scanTitle =
        document.getElementById("scanTitle");

    const scanDescription =
        document.getElementById("scanDescription");

    const resultDocumentType =
        document.getElementById("resultDocumentType");

    const resultRisk =
        document.getElementById("resultRisk");

    const resultRiskScore =
        document.getElementById("resultRiskScore");

    const resultBlacklist =
        document.getElementById("resultBlacklist");

    const resultTampering =
        document.getElementById("resultTampering");

    const validationStatus =
        document.getElementById("validationStatus");

    const validationGrid =
        document.getElementById("validationGrid");

    const tamperingStatus =
        document.getElementById("tamperingStatus");

    const tamperingGrid =
        document.getElementById("tamperingGrid");

    const riskReasons =
        document.getElementById("riskReasons");

    const ocrText =
        document.getElementById("ocrText");


    // =========================================================
    // SAFETY CHECK
    // =========================================================

    if (!form || !documentInput || !dropZone) {

        console.error(
            "Required upload elements were not found."
        );

        return;
    }


    // =========================================================
    // HTML ESCAPING
    // =========================================================

    function escapeHtml(value) {

        if (
            value === null ||
            value === undefined
        ) {
            return "";
        }

        return String(value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }


    // =========================================================
    // FILE SIZE
    // =========================================================

    function formatFileSize(bytes) {

        if (bytes < 1024) {
            return bytes + " B";
        }

        if (bytes < 1024 * 1024) {
            return (
                (bytes / 1024).toFixed(1)
                + " KB"
            );
        }

        return (
            (bytes / (1024 * 1024)).toFixed(2)
            + " MB"
        );
    }


    // =========================================================
    // ERROR DISPLAY
    // =========================================================

    function showError(message) {

        if (!errorBox) {
            return;
        }

        errorBox.textContent = message;

        errorBox.style.display = "block";
    }


    function clearError() {

        if (!errorBox) {
            return;
        }

        errorBox.textContent = "";

        errorBox.style.display = "none";
    }


    // =========================================================
    // FILE DISPLAY
    // =========================================================

    function showSelectedFile(file) {

        if (!file) {
            return;
        }

        fileName.textContent =
            file.name;

        fileSize.textContent =
            formatFileSize(file.size);

        uploadContent.style.display =
            "none";

        selectedFile.style.display =
            "flex";

        clearError();
    }


    function resetFileSelection() {

        documentInput.value = "";

        selectedFile.style.display =
            "none";

        uploadContent.style.display =
            "block";
    }


    // =========================================================
    // FILE VALIDATION
    // =========================================================

    function validateFile(file) {

        if (!file) {
            return false;
        }

        const allowedTypes = [
            "image/jpeg",
            "image/png"
        ];

        if (
            !allowedTypes.includes(
                file.type
            )
        ) {

            showError(
                "Please select a JPG, JPEG or PNG image."
            );

            return false;
        }


        const maxSize =
            10 * 1024 * 1024;


        if (file.size > maxSize) {

            showError(
                "File is too large. Maximum size is 10 MB."
            );

            return false;
        }


        return true;
    }


    // =========================================================
    // WHEN A FILE IS SELECTED
    // =========================================================

    function handleFile(file) {

        if (!validateFile(file)) {

            resetFileSelection();

            return;
        }

        showSelectedFile(file);
    }


    // =========================================================
    // CLICK UPLOAD AREA
    // =========================================================

    dropZone.addEventListener(
        "click",
        function (event) {

            // Don't reopen file picker when
            // clicking the remove button.

            if (
                event.target === removeFile ||
                removeFile.contains(event.target)
            ) {
                return;
            }

            documentInput.click();
        }
    );


    // =========================================================
    // FILE INPUT CHANGE
    // =========================================================

    documentInput.addEventListener(
        "change",
        function () {

            if (
                documentInput.files &&
                documentInput.files.length > 0
            ) {

                handleFile(
                    documentInput.files[0]
                );
            }
        }
    );


    // =========================================================
    // DRAG OVER
    // =========================================================

    dropZone.addEventListener(
        "dragover",
        function (event) {

            event.preventDefault();

            dropZone.classList.add(
                "drag-over"
            );
        }
    );


    // =========================================================
    // DRAG LEAVE
    // =========================================================

    dropZone.addEventListener(
        "dragleave",
        function () {

            dropZone.classList.remove(
                "drag-over"
            );
        }
    );


    // =========================================================
    // DROP FILE
    // =========================================================

    dropZone.addEventListener(
        "drop",
        function (event) {

            event.preventDefault();

            dropZone.classList.remove(
                "drag-over"
            );


            const files =
                event.dataTransfer.files;


            if (
                files &&
                files.length > 0
            ) {

                handleFile(
                    files[0]
                );
            }
        }
    );


    // =========================================================
    // REMOVE SELECTED FILE
    // =========================================================

    if (removeFile) {

        removeFile.addEventListener(
            "click",
            function (event) {

                event.preventDefault();

                event.stopPropagation();

                resetFileSelection();
            }
        );
    }


    // =========================================================
    // CHECK MARK
    // =========================================================

    function checkMark(value) {

        return value === true
            ? "✓"
            : "✕";
    }


    function checkClass(value) {

        return value === true
            ? "check-pass"
            : "check-fail";
    }


    // =========================================================
    // VALIDATION CHECKS
    // =========================================================

    function renderValidationChecks(
        checks
    ) {

        if (!checks) {
            return "";
        }

        let html = "";

        Object.entries(checks).forEach(
            ([name, passed]) => {

                html += `
                    <div class="check-row">

                        <span class="${checkClass(passed)}">
                            ${checkMark(passed)}
                        </span>

                        <span>
                            ${escapeHtml(name)}
                        </span>

                        <strong>
                            ${passed ? "PASS" : "FAIL"}
                        </strong>

                    </div>
                `;
            }
        );

        return html;
    }


    // =========================================================
    // TAMPERING CHECKS
    // =========================================================

    function renderTamperingChecks(
        checks
    ) {

        if (!checks) {
            return "";
        }


        const fields = [

            [
                "Changed Pixel Percentage",
                checks[
                    "Changed Pixel Percentage"
                ]
            ],

            [
                "ELA Score",
                checks[
                    "ELA Score"
                ]
            ],

            [
                "Editing Software",
                checks[
                    "Editing Software"
                ]
            ],

            [
                "Editing Software Detected",
                checks[
                    "Editing Software Detected"
                ]
            ],

            [
                "Largest Changed Region",
                checks[
                    "Largest Changed Region"
                ]
            ],

            [
                "Localized Max Difference",
                checks[
                    "Localized Max Difference"
                ]
            ],

            [
                "Localized Suspicious",
                checks[
                    "Localized Suspicious"
                ]
            ],

            [
                "Metadata Present",
                checks[
                    "Metadata Present"
                ]
            ],

            [
                "Reference Comparison Available",
                checks[
                    "Reference Comparison Available"
                ]
            ],

            [
                "Reference Difference",
                checks[
                    "Reference Difference"
                ]
            ],

            [
                "Reference Mean Difference",
                checks[
                    "Reference Mean Difference"
                ]
            ],

            [
                "Reference Tampering Detected",
                checks[
                    "Reference Tampering Detected"
                ]
            ]
        ];


        let html = "";


        fields.forEach(
            ([name, value]) => {

                let displayValue =
                    value;


                if (
                    value === null ||
                    value === undefined
                ) {

                    displayValue =
                        "NOT AVAILABLE";
                }

                else if (
                    typeof value === "boolean"
                ) {

                    displayValue =
                        value
                            ? "FLAG"
                            : "CLEAR";
                }


                html += `
                    <div class="check-row">

                        <span class="check-pass">
                            ✓
                        </span>

                        <span>
                            ${escapeHtml(name)}
                        </span>

                        <strong>
                            ${escapeHtml(
                                displayValue
                            )}
                        </strong>

                    </div>
                `;
            }
        );


        return html;
    }


    // =========================================================
    // RISK REASONS
    // =========================================================

    function renderRiskReasons(
        reasons
    ) {

        if (
            !reasons ||
            reasons.length === 0
        ) {

            return `
                <div class="reason-good">
                    ✓ No risk indicators were triggered.
                </div>
            `;
        }


        return reasons
            .map(
                reason => `
                    <div class="reason-item">
                        • ${escapeHtml(reason)}
                    </div>
                `
            )
            .join("");
    }


    // =========================================================
    // SCANNING ANIMATION
    // =========================================================

    function startScanningAnimation() {

        if (!scanningCard) {
            return;
        }


        scanningCard.style.display =
            "flex";


        let progress = 0;


        if (progressBar) {
            progressBar.style.width =
                "0%";
        }


        if (scanPercent) {
            scanPercent.textContent =
                "0%";
        }


        if (scanTitle) {
            scanTitle.textContent =
                "Initializing screening engine...";
        }


        if (scanDescription) {
            scanDescription.textContent =
                "Preparing document analysis.";
        }


        const steps = [

            {
                progress: 25,
                title: "Extracting document text...",
                description:
                    "Running OCR on the uploaded document."
            },

            {
                progress: 50,
                title: "Validating document...",
                description:
                    "Checking detected fields and document structure."
            },

            {
                progress: 75,
                title: "Analyzing possible tampering...",
                description:
                    "Checking image anomalies and reference signals."
            },

            {
                progress: 90,
                title: "Calculating screening risk...",
                description:
                    "Combining validation, tampering and blacklist signals."
            }
        ];


        let index = 0;


        const interval =
            setInterval(
                function () {

                    if (
                        index >= steps.length
                    ) {

                        clearInterval(
                            interval
                        );

                        return;
                    }


                    const step =
                        steps[index];


                    if (progressBar) {
                        progressBar.style.width =
                            step.progress + "%";
                    }


                    if (scanPercent) {
                        scanPercent.textContent =
                            step.progress + "%";
                    }


                    if (scanTitle) {
                        scanTitle.textContent =
                            step.title;
                    }


                    if (scanDescription) {
                        scanDescription.textContent =
                            step.description;
                    }


                    index++;

                },
                450
            );
    }


    function finishScanningAnimation() {

        if (progressBar) {
            progressBar.style.width =
                "100%";
        }


        if (scanPercent) {
            scanPercent.textContent =
                "100%";
        }


        if (scanTitle) {
            scanTitle.textContent =
                "Screening complete";
        }


        if (scanDescription) {
            scanDescription.textContent =
                "Analysis results are ready.";
        }
    }


    // =========================================================
    // RENDER RESULTS
    // =========================================================

    function renderResults(data) {

        if (!resultsSection) {
            return;
        }


        const riskLevel =
            data.risk_level || "LOW";


        const riskScore =
            data.risk_score ?? 0;


        const validationPassed =
            data.document_verified === true;


        const tamperingPassed =
            !data.tampering_suspected;


        const blacklistPassed =
            !data.blacklisted;


        // DOCUMENT TYPE

        if (resultDocumentType) {

            resultDocumentType.textContent =
                data.document_type || "Unknown";
        }


        // RISK

        if (resultRisk) {

            resultRisk.textContent =
                riskLevel;
        }


        if (resultRiskScore) {

            resultRiskScore.textContent =
                "Score: "
                + riskScore
                + " / 100";
        }


        // BLACKLIST

        if (resultBlacklist) {

            resultBlacklist.textContent =
                blacklistPassed
                    ? "CLEAR"
                    : "MATCH";
        }


        // TAMPERING

        if (resultTampering) {

            resultTampering.textContent =
                tamperingPassed
                    ? "NO SIGNIFICANT SIGNS"
                    : "REVIEW";
        }


        // VALIDATION STATUS

        if (validationStatus) {

            validationStatus.textContent =
                validationPassed
                    ? "VALIDATION PASSED"
                    : "VALIDATION NEEDS REVIEW";
        }


        // VALIDATION GRID

        if (validationGrid) {

            validationGrid.innerHTML =
                renderValidationChecks(
                    data.validation_checks
                );
        }


        // TAMPERING STATUS

        if (tamperingStatus) {

            tamperingStatus.textContent =
                tamperingPassed
                    ? "NO SIGNIFICANT SIGNS"
                    : "POTENTIALLY SUSPICIOUS";
        }


        // TAMPERING GRID

        if (tamperingGrid) {

            tamperingGrid.innerHTML =
                renderTamperingChecks(
                    data.tampering_checks
                );
        }


        // RISK REASONS

        if (riskReasons) {

            riskReasons.innerHTML =
                renderRiskReasons(
                    data.risk_reasons
                );
        }


        // OCR

        if (ocrText) {

            ocrText.textContent =
                data.ocr_text ||
                "No text extracted.";
        }


        // SHOW RESULTS

        resultsSection.style.display =
            "block";


        setTimeout(
            function () {

                resultsSection.scrollIntoView({
                    behavior: "smooth",
                    block: "start"
                });

            },
            100
        );
    }


    // =========================================================
    // FORM SUBMISSION
    // =========================================================

    form.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            clearError();


            // CHECK FILE

            if (
                !documentInput.files ||
                documentInput.files.length === 0
            ) {

                showError(
                    "Please select a document first."
                );

                return;
            }


            const file =
                documentInput.files[0];


            if (!validateFile(file)) {
                return;
            }


            // BUTTON

            if (screenButton) {

                screenButton.disabled =
                    true;

                screenButton.innerHTML =
                    "<span>⌕</span> SCREENING...";
            }


            // HIDE OLD RESULTS

            if (resultsSection) {

                resultsSection.style.display =
                    "none";
            }


            // START ANIMATION

            startScanningAnimation();


            // FORM DATA

            const formData =
                new FormData();


            formData.append(
                "document",
                file
            );


            // =================================================
            // OPTIONAL LIVE PHOTO
            // =================================================

            const livePhotoInput =
                document.getElementById(
                    "livephoto"
                );


            if (
                livePhotoInput &&
                livePhotoInput.files &&
                livePhotoInput.files.length > 0
            ) {

                formData.append(
                    "livephoto",
                    livePhotoInput.files[0]
                );
                const livePhotoName =
    document.getElementById(
        "livePhotoName"
    );


if (livePhotoInput) {

    livePhotoInput.addEventListener(
        "change",
        function () {

            if (
                livePhotoInput.files &&
                livePhotoInput.files.length > 0
            ) {

                const file =
                    livePhotoInput.files[0];

                if (livePhotoName) {

                    livePhotoName.textContent =
                        file.name;
                }

            }

            else {

                if (livePhotoName) {

                    livePhotoName.textContent =
                        "No photo selected";
                }
            }

        }
    );
}
            }


            try {

                const response =
                    await fetch(
                        "/screen",
                        {
                            method: "POST",
                            body: formData
                        }
                    );


                let data;


                try {

                    data =
                        await response.json();

                }

                catch {

                    throw new Error(
                        "The server returned an invalid response."
                    );
                }


                if (!response.ok) {

                    throw new Error(
                        data.message ||
                        "Screening failed."
                    );
                }


                if (!data.success) {

                    throw new Error(
                        data.message ||
                        "Screening failed."
                    );
                }


                // FINISH ANIMATION

                finishScanningAnimation();


                // SHOW RESULTS

                renderResults(
                    data
                );


                // HIDE SCANNING CARD

                setTimeout(
                    function () {

                        if (scanningCard) {

                            scanningCard.style.display =
                                "none";
                        }

                    },
                    500
                );


            }

            catch (error) {

                console.error(
                    "Screening error:",
                    error
                );


                if (scanningCard) {

                    scanningCard.style.display =
                        "none";
                }


                showError(
                    error.message ||
                    "Something went wrong while screening the document."
                );

            }


            finally {

                if (screenButton) {

                    screenButton.disabled =
                        false;

                    screenButton.innerHTML =
                        "<span>⌕</span> START SCREENING";
                }
            }

        }
    );


    // =========================================================
    // NEW SCREENING
    // =========================================================

    if (newScreening) {

        newScreening.addEventListener(
            "click",
            function (event) {

                event.preventDefault();


                resetFileSelection();


                clearError();


                if (resultsSection) {

                    resultsSection.style.display =
                        "none";
                }


                if (scanningCard) {

                    scanningCard.style.display =
                        "none";
                }


                window.scrollTo({
                    top: 0,
                    behavior: "smooth"
                });
            }
        );
    }


    // =========================================================
    // INITIAL STATE
    // =========================================================

    resetFileSelection();

});