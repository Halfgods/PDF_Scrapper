import re
import json
import os
from collections import Counter

def extract_semester_blocks(raw_text):
    lines = raw_text.splitlines()
    semester_blocks = []
    current_block = []
    current_sem = ""
    total_counter = 0

    for line in lines:
        stripped = line.strip()
        if re.match(r"SEM[- ]?[IVXLCDM]+", stripped.upper()):
            if total_counter >= 3 and current_block:
                semester_blocks.append((current_sem, current_block))
            current_sem = stripped.upper().replace(" ", "-")
            current_block = [stripped]
            total_counter = 0
        else:
            current_block.append(stripped)
            if "TOTAL" in stripped.upper():
                total_counter += 1

    if total_counter >= 3 and current_block:
        semester_blocks.append((current_sem, current_block))

    return semester_blocks


def extract_courses_from_block(lines):
    course_pattern = re.compile(r'^[A-Z]{3}\d{2}[A-Z]{2}\d{2}$')
    course_dict = {}
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if course_pattern.match(line):
            code = line
            name_candidates = []

            for j in range(i + 1, min(i + 7, len(lines))):
                lookahead_line = lines[j].strip()

                # Stop if next course code appears
                if course_pattern.match(lookahead_line):
                    break

                if lookahead_line:
                    name_candidates.append(lookahead_line)

            if name_candidates:
                # Find the longest line
                longest_name = max(name_candidates, key=len)
                # If longest line looks like course code → unknown
                if course_pattern.match(longest_name):
                    course_dict[code] = "UNKNOWN"
                else:
                    course_dict[code] = longest_name.strip()
            else:
                course_dict[code] = "UNKNOWN"

            i += 1  # still go line by line
        else:
            i += 1

    return course_dict


def infer_branch_code(course_dict, branch_map):
    codes = list(course_dict.keys())
    middle_parts = [code[5:7] for code in codes if len(code) >= 7]
    if not middle_parts:
        return "UNKNOWN", "UNKNOWN"

    most_common_code = Counter(middle_parts).most_common(1)[0][0]
    branch_name = branch_map.get(most_common_code, "UNKNOWN")
    return most_common_code, branch_name


if __name__ == "__main__":
    with open("output/raw_text.txt", "r", encoding="utf-8") as f:
        raw_text = f.read()

    branch_map = {
        "CE": "Computer Engineering",
        "CS": "Computer Science and Engineering",
        "EC": "Electronics and Communication",
        "ME": "Mechanical Engineering"
    }

    semester_blocks = extract_semester_blocks(raw_text)

    semester_courses = {}
    for sem_name, sem_lines in semester_blocks:
        courses = extract_courses_from_block(sem_lines)
        semester_courses[sem_name] = courses

    all_courses_flat = {k: v for sem in semester_courses.values() for k, v in sem.items()}
    branch_code, branch_name = infer_branch_code(all_courses_flat, branch_map)

    result = {
        "inferred_branch_code": branch_code,
        "inferred_branch_name": branch_name,
        "semesters": semester_courses
    }

    output_path = "output/courses.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Saved semester-wise structured courses to {output_path}\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))
