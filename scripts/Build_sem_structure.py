import json

# Load the cleaned list you got from test.py
from test import extract_semester_blocks
def build_semester_structure(data):
    sem_structure = {}
    
    for semester_block in data:
        # Detect semester name (e.g., SEM-I)
        sem_name = None
        for line in semester_block:
            if "SEM" in line.upper():
                sem_name = line.strip().split()[0]  # Get "SEM-I"
                break

        if not sem_name:
            continue

        sem_structure[sem_name] = {}
        current_course_code = None
        current_course_name = None
        course_chapters = []

        for line in semester_block:
            line = line.strip()
            
            # Detect course code & course name
            if len(line) >= 6 and "-" in line and line.split("-")[0].strip().isalnum():
                if current_course_code:
                    # Save the previous course
                    sem_structure[sem_name][current_course_code] = {
                        "name": current_course_name,
                        "chapters": course_chapters
                    }
                    course_chapters = []

                parts = line.split("-")
                current_course_code = parts[0].strip()
                current_course_name = "-".join(parts[1:]).strip()

            elif current_course_code:
                # Treat everything after course name as chapter/topic
                if line and not line.lower().startswith("total"):
                    course_chapters.append(line)

        # Add the last course in the block
        if current_course_code and current_course_code not in sem_structure[sem_name]:
            sem_structure[sem_name][current_course_code] = {
                "name": current_course_name,
                "chapters": course_chapters
            }

    return sem_structure

if __name__ == "__main__":
    structured_data = build_semester_structure(extract_semester_blocks)
    
    with open("output/extracted_data.json","w") as f:
        json.dump(structured_data, f, indent=4)

    print("✅ Structured data written to output/final_sem_structure.json")
