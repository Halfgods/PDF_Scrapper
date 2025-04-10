# scripts/extract_pdf.py

import fitz  # PyMuPDF
import os

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = "\n\n".join([page.get_text() for page in doc])
    doc.close()
    return full_text

if __name__ == "__main__":
    pdf_path = "uploads/syllabus.pdf"
    output_path = "output/raw_text.txt"

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"{pdf_path} not found.")

    text = extract_text_from_pdf(pdf_path)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"[✓] Extracted text saved to: {output_path}")
