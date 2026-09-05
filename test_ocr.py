import pytesseract
from PIL import Image

# Tesseract location
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Open document
image = Image.open(
    r"C:\Users\Heeral Satkirti\OneDrive\Desktop\Document verification\sample.png"
)

# Extract text
text = pytesseract.image_to_string(image)

print("========== EXTRACTED TEXT ==========")
print(text)

# Expected details
expected_name = "Rahul Sharma"
expected_id = "ABC12345"
expected_department = "Computer Science"

# Convert OCR text to lowercase for easier comparison
ocr_text = text.lower()

# Check details
name_found = expected_name.lower() in ocr_text
id_found = expected_id.lower() in ocr_text
department_found = expected_department.lower() in ocr_text

print("\n========== VERIFICATION RESULT ==========")

if name_found and id_found and department_found:
    print("DOCUMENT VERIFIED SUCCESSFULLY")
else:
    print("DOCUMENT VERIFICATION FAILED")

print("\nDetails:")
print("Name:", "Matched" if name_found else "Not Matched")
print("ID:", "Matched" if id_found else "Not Matched")
print("Department:", "Matched" if department_found else "Not Matched")