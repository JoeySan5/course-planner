import json

def get_course_input():
    department = input("Enter department: ").strip()
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

def read_courses_from_file(filename):
    courses = []
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    i = 0
    while i < len(lines):
        department = lines[i].strip()
        number = lines[i + 1].strip()
        title = lines[i + 2].strip()
        credits = int(lines[i + 3].strip())
        
        courseID = f"{department}{number}"
        
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
            "prerequisites": []
        }
        
        courses.append(course)
        i += 5  # Move to the next course block
    
    return courses


def main():
#     courses = []
    
#     while True:
#         course = get_course_input()
#         courses.append(course)
        
#         more_courses = input("Do you want to add another course? (yes/no): ").strip().lower()
#         if more_courses != 'yes':
#             break
  
    # courses = []
    # Read courses from the file
    courses = read_courses_from_file('cse-catalog')
    
    # while True:
    #     course = get_course_input()
    #     courses.append(course)
        
    #     more_courses = input("Do you want to add another course? (yes/no): ").strip().lower()
    #     if more_courses != 'yes':
    #         break
    
    with open('user-input-courses.json', 'w') as json_file:
        json.dump(courses, json_file, indent=4)
    
    print("Courses have been saved to user-input-courses.json")


if __name__ == "__main__":
    main()