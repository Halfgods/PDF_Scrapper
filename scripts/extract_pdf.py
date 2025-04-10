import re
import fitz  # PyMuPDF
import os

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = "\n\n".join([page.get_text() for page in doc])
    doc.close()
    return full_text

# Function to filter unwanted content from the raw text
def filter_raw_text(raw_text):
    # Define unwanted terms to be removed
    skip_terms = ['MSE', 'ESE', 'ISE', 'Marks', 'MCQ', 'Rubrics', 'TU', 'PRJ', 'TH']
    
    # Remove lines that contain unwanted terms
    filtered_lines = []
    for line in raw_text.splitlines():
        if not any(skip_term in line for skip_term in skip_terms):
            filtered_lines.append(line)
    
    # Reconstruct the text after removing unwanted lines
    filtered_text = "\n".join(filtered_lines)
    
    # Remove numbers that are standalone (not followed by letters)
    # Keep numbers that are followed by letters, but remove numbers standing alone
    cleaned_text = re.sub(r'\b\d+\b(?![A-Za-z])', '', filtered_text)

    # Optional: Remove extra spaces between words and trim the result
    cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()

    return cleaned_text


if __name__ == "__main__":
    pdf_path = "uploads/syllabus.pdf"
    output_path = "output/raw_text.txt"
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"{pdf_path} not found.")
    
    # Extract text from the PDF
    text = extract_text_from_pdf(pdf_path)

    # Filter the raw text
    cleaned_text = filter_raw_text(text)

    # Save the cleaned text to a file (raw_text.txt)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(cleaned_text)

    print(f"[✓] Extracted and cleaned text saved to: {output_path}")
