import fitz  # PyMuPDF
import os
import re

# Terms to skip (case-insensitive)
skip_terms = ['MSE', 'Credits', 'ESE', 'ISE', 'TH', 'PR', 'PRJ', 'Marks', 'MCQ', 'Rubrics', 'TU', 'Contact Hours', 'Examination Marks']

def clean_text(text):
    lines = text.splitlines()
    filtered = []
    found_structure = False
    buffer_line = ""
    
    for line in lines:
        original_line = line  # preserve spacing
        stripped_line = line.strip()
        upper_line = stripped_line.upper()

        # Detect starting point by checking if the combined buffer has the header.
        combined = (buffer_line + " " + stripped_line).strip().upper()
        if not found_structure:
            if "SEMESTERWISE CURRICULUM STRUCTURE" in combined:
                print("✅ Found curriculum structure trigger line:", stripped_line)
                found_structure = True
                # Optionally, you could add the current line if needed:
                # filtered.append(original_line)
            buffer_line = stripped_line  # update buffer regardless
            continue  # skip this line until trigger is found

        # After trigger found, log for debugging
        print(f"🔎 DEBUG line after trigger: '{stripped_line}'")

        # Skip if it contains any unwanted term (case-insensitive)
        if any(term in upper_line for term in skip_terms):
            continue

        # Skip standalone numbers
        if stripped_line.isdigit():
            continue
        
        # Skip lines that ONLY contain skip terms
        skip_check = all(term in upper_line for term in skip_terms if term in upper_line)
        if skip_check:
            continue

        # Skip lines that have no alphabet (like "50   100")
        if not any(char.isalpha() for char in stripped_line):
            continue
        
        # If passed all filters, keep the line (preserve original spacing)
        filtered.append(original_line)

    return "\n".join(filtered)

def extract_pdf_text(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()

    doc.close()
    cleaned_text = clean_text(full_text)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print(f"Filtered text written to: {output_path}")

if __name__ == "__main__":
    input_pdf = "uploads/syllabus.pdf"
    output_txt = "output/raw_text.txt"
    extract_pdf_text(input_pdf, output_txt)
