import fitz  # PyMuPDF
import os

# Terms to skip (case-insensitive)
skip_terms = ['MSE','Credits', 'ESE', 'ISE', 'TH', 'PR', 'PRJ', 'Marks', 'MCQ', 'Rubrics', 'TU','Contact Hours','Examination Marks']

def clean_text(text):
    lines = text.splitlines()
    filtered = []
    found_structure = False

    for line in lines:
        original_line = line
        stripped_line = line.strip()
        upper_line = stripped_line.upper()

        if not found_structure:
            if "SEMESTERWISE CURRICULUM STRUCTURE" in upper_line:
                found_structure = True
                continue

        if not found_structure:
            continue

        if any(term in upper_line for term in skip_terms):
            continue

        if stripped_line.isdigit():
            continue

        if not any(char.isalpha() for char in stripped_line):
            continue

        filtered.append(original_line)

    return filtered


def extract_pdf_text(pdf_path, output_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        full_text += page.get_text()
    doc.close()

    cleaned_lines = clean_text(full_text)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(cleaned_lines))

    print(f"✅ Clean filtered text written to: {output_path}")


if __name__ == "__main__":
    input_pdf = "uploads/syllabus.pdf"
    output_txt = "output/raw_text.txt"  # <- now it has the filtered result
    extract_pdf_text(input_pdf, output_txt)
