import re
import json
import os

def get_branch_name(raw_text, branch_keywords):
    pattern = "|".join(re.escape(branch) for branch in branch_keywords)
    match = re.search(pattern, raw_text, re.IGNORECASE)
    if match:
        return match.group().strip()
    return "UNKNOWN"

def split_by_semester(text):
    sem_headers = re.findall(r"SEM[-\s]?[IV]+", text, flags=re.IGNORECASE)
    sem_splits = re.split(r"SEM[-\s]?[IV]+", text, flags=re.IGNORECASE)[1:]
    semesters = {}
    for i, sem in enumerate(sem_splits):
        header = sem_headers[i].strip().upper().replace(" ", "").replace("-", "")
        if header.startswith("SEM") and len(header) <= 7:
            semesters[header] = sem.strip()
    return semesters

def extract_courses(sem_text):
    """
    Scans through sem_text line by line and tries to extract courses.
    """
    lines = sem_text.splitlines()
    courses = []

    # Updated pattern for course codes like BSC11CE01, PCC13CE11, etc.
    course_code_pattern = re.compile(r'\b[A-Z]{3}[0-9]{2}[A-Z]{2}[0-9]{0,2}\b|\b[A-Z]{3}[0-9A-Z]{2,3}\b')

    # Skip terms to ignore non-course data
    skip_terms = ['MSE', 'ESE', 'ISE', 'TH', 'PR', 'PRJ', 'Marks', 'MCQ', 'Rubrics', 'TU']

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Skip lines with any unwanted term
        if any(skip_term in line for skip_term in skip_terms):
            i += 1
            continue

        # Check if the line matches our course code pattern
        if course_code_pattern.match(line):
            code = line
            course_lines = []
            j = i + 1
            while j < len(lines):
                candidate = lines[j].strip()

                if not candidate:
                    break  # stop at blank line

                if course_code_pattern.match(candidate) or candidate.isdigit() or any(skip_term in candidate for skip_term in skip_terms):
                    break  # stop at next course or irrelevant data

                course_lines.append(candidate)
                j += 1

            course_name = " ".join(course_lines).strip()

            courses.append({
                "code": code,
                "name": course_name,
                "topics": []  # Topics will be processed later
            })

            # Move pointer ahead
            i = j
        else:
            i += 1

    return courses


def extract_course_name(course_details):
    course_info = course_details[1:]
    course_name = max(course_info, key=len)
    return course_name

if __name__ == "__main__":
    # Load the raw text that you extracted from the PDF
    with open("output/raw_text.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Define branch keywords for identifying the course branch
    branch_map = {
    "CE": "Computer Engineering",
    "CS": "Computer Science and Engineering",
    "EC": "Electronics and Communication",
    "ME": "Mechanical Engineering",
    
}

    
    # Get the branch name
    branch = get_branch_name(raw_text, branch_map)
    print(f"\nBranch: {branch}\n")

    # Split the text into semesters
    semester_data = split_by_semester(raw_text)
    print(f"Semesters found: {list(semester_data.keys())}")

    # Create a structure to hold the output data
    output_data = {
        "branch": branch,
        "semesters": {}
    }

    # Process each semester's content and extract courses
    for sem, content in semester_data.items():
        print(f"\nProcessing {sem}...")  # Debugging line to track progress
        courses = extract_courses(content)
        
        # Add the extracted courses to the output
        output_data["semesters"][sem] = courses
        print(f"Extracted {len(courses)} courses from {sem}")  # Debugging line

    # Save the output as a JSON file in the output folder
    output_file_path = "output/extracted_data.json"
    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)
    with open(output_file_path, "w", encoding="utf-8") as json_file:
        json.dump(output_data, json_file, indent=2, ensure_ascii=False)

    print(f"\nFinal Extracted Data has been saved to: {output_file_path}\n")
    # Also print the JSON to the console for review
    print(json.dumps(output_data, indent=2, ensure_ascii=False))
