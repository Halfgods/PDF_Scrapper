import re
import json
import os

def extract_course_codes(text):
    # Matches codes like PCC13CE11, BSC11MA, INT01, etc.
    pattern = re.compile(r'\b[A-Z]{3}[0-9]{2}[A-Z]{2}[0-9]{0,2}\b|\b[A-Z]{3}[0-9A-Z]{2,3}\b')
    return pattern.findall(text)

def infer_branch_code(course_codes, branch_map):
    for code in course_codes:
        match = re.search(r'[A-Z]{3}[0-9]{2}([A-Z]{2})', code)
        if match:
            possible_code = match.group(1)
            if possible_code in branch_map:
                return possible_code, branch_map[possible_code]
    return "UNKNOWN", "UNKNOWN"

if __name__ == "__main__":
    # Load the raw syllabus text
    with open("output/raw_text.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    # Branch code to full name mapping
    branch_map = {
        "CE": "Computer Engineering",
        "CS": "Computer Science and Engineering",
        "EC": "Electronics and Communication",
        "ME": "Mechanical Engineering"
    }

    # Step 1: Extract all course codes
    course_codes = extract_course_codes(raw_text)

    # Step 2: Infer branch from course codes
    branch_code, branch_name = infer_branch_code(course_codes, branch_map)

    # Step 3: Store results
    result = {
        "inferred_branch_code": branch_code,
    }
    output_path = "output/courses.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Saved inferred branch and course codes to {output_path}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
