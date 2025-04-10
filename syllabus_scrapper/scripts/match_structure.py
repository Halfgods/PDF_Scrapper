import regex as re
import json

def get_branch_name(raw_text, branch_keywords):
    pattern = "|".join(re.escape(branch) for branch in branch_keywords)
    match = re.search(pattern, raw_text, re.IGNORECASE)
    if match:
        return match.group().strip()
    return "UNKNOWN"

def split_by_semester(text):
    # This regex is intended to capture strings like SEM-I, SEM-II, etc.
    sem_headers = re.findall(r"SEM[-\s]?[IV]+", text, flags=re.IGNORECASE)
    sem_splits = re.split(r"SEM[-\s]?[IV]+", text, flags=re.IGNORECASE)[1:]
    semesters = {}
    for i, sem in enumerate(sem_splits):
        header = sem_headers[i].strip().upper().replace(" ", "").replace("-", "")
        # Only accept if header length is reasonable (e.g., SEMI, SEMII, etc.)
        if header.startswith("SEM") and len(header) <= 7:
            semesters[header] = sem.strip()
    return semesters

def extract_courses(sem_text):
    """
    Scans through sem_text line by line and tries to extract courses.
    A valid course is assumed to have:
     - A course code matching a pattern (e.g., 3 letters + 2 digits + 2-4 letters and optional digits)
     - The next non-skip line is taken as the course name.
     - Any following lines, until a new course code or an empty/skip line, are considered topics/subtopics.
    """
    lines = sem_text.splitlines()
    courses = []

    # Adjust the course code pattern here as needed.
    # This pattern is tuned for things like BSC11CE01, PCC13CE11, etc.
    course_code_pattern = re.compile(r'^[A-Z]{3}[0-9]{2}[A-Z]{2,4}[0-9]*$')
    # Define skip terms to ignore non-course data
    skip_terms = ['MSE', 'ESE', 'ISE', 'TH', 'PR', 'PRJ', 'Marks', 'MCQ', 'Rubrics', 'TU']
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # If the line contains any unwanted term, skip it.
        if any(skip_term in line for skip_term in skip_terms):
            i += 1
            continue

        # Check if the line matches our course code pattern
        if course_code_pattern.match(line):
            code = line
            course_name = ""
            topics = []
            # Look ahead for the course name: first non-empty line that doesn't match a course code.
            j = i + 1
            while j < len(lines):
                next_line = lines[j].strip()
                # Stop if this line is a valid course code (start of a new course), or is empty.
                if course_code_pattern.match(next_line) or not next_line:
                    break
                # Also break if next_line contains a skip term.
                if any(skip_term in next_line for skip_term in skip_terms):
                    j += 1
                    continue
                # If course name not yet set, take this line as course name.
                if not course_name:
                    course_name = next_line
                else:
                    # Otherwise, consider it a topic/subtopic.
                    topics.append(next_line)
                j += 1

            # Only add if we got a course name.
            if code and course_name:
                courses.append({
                    "code": code,
                    "name": course_name,
                    "topics": topics
                })
            i = j
        else:
            i += 1

    return courses

if __name__ == "__main__":
    # Load the raw text that you extracted from the PDF
    with open("output/raw_text.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    branch_keywords = [
        "Computer Engineering",
        "Computer Science and Engineering",
        "Electronics and Computer Science",
        "Mechanical Engineering"
    ]
    branch = get_branch_name(raw_text, branch_keywords)
    print(f"\nBranch: {branch}\n")

    # Split entire text by semester (we assume the curriculum section contains semesters)
    semester_data = split_by_semester(raw_text)
    print("Semesters found:", list(semester_data.keys()))

    # Create a structure to hold our output
    output_data = {
        "branch": branch,
        "semesters": {}
    }

    for sem, content in semester_data.items():
        courses = extract_courses(content)
        output_data["semesters"][sem] = courses

    # Print JSON output nicely formatted
    json_output = json.dumps(output_data, indent=2, ensure_ascii=False)
    print("\nFinal Extracted Data:\n", json_output)
