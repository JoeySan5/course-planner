import json

def get_course_input():
    number = input("Enter course number: ").strip()
    title = input("Enter course title: ").strip()
    credits = input("Enter course credits: ").strip()
    prereqs_input = input("Enter prerequisites (comma-separated course numbers, or leave empty if none): ").strip()
    
    # Convert credits to int or float
    if ',' in credits:
        credits = float(credits.replace(',', '.'))
    else:
        credits = int(credits)
    
    # Generate courseID
    department = "CSE"
    courseID = f"{department}{number}"
    
    # Process prerequisites
    prereqs = [f"{department}{prereq.strip()}" for prereq in prereqs_input.split(',')] if prereqs_input else []
    
    # Create course dictionary
    course = {
        "courseID": courseID,
        "department": department,
        "number": number,
        "title": title,
        "credits": credits,
        "attributes": [],
        "semesters": [
            202410,
            202440,
            202510,
            202540,
            202610,
            202640,
            202710,
            202740,
            202810,
            202840
        ],
        "prerequisites": prereqs
    }
    
    return course

def main():
    courses = []
    
    while True:
        course = get_course_input()
        courses.append(course)
        
        more_courses = input("Do you want to add another course? (yes/no): ").strip().lower()
        if more_courses != 'yes':
            break
    
    with open('user-input-courses.json', 'w') as json_file:
        json.dump(courses, json_file, indent=4)
    
    print("Courses have been saved to user-input-courses.json")

if __name__ == "__main__":
    main()