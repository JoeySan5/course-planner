from flask import Flask, request, jsonify
import psycopg2
import re
import json
from datetime import datetime

app = Flask(__name__)

# Establishing Database Connection
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="9089223654",
    host="database-1.cqqwg6frglat.us-west-2.rds.amazonaws.com",
    port="5432"
)
curr = conn.cursor()

def convert_semester_code(semester_str):
    # Converts '2024-Spring' to '202410', '2027-Fall' to '202740'
    year, term = semester_str.split('-')
    term_code = '10' if term == 'Spring' else '40'
    return f"{year}{term_code}"

def CSB_elective_calculation(taken_elective_courses, hss, free, science_tech, cse_electives, csb_electives):
    for course in taken_elective_courses:
        # Step 1: Fetch credit information from the course table
        curr.execute("SELECT credits, department FROM course WHERE courseid = %s", (course,))
        course_info = curr.fetchone()
        
        if course_info:
            credits, department = course_info
        else:
            # If the course is not found, assume it's a transfer and assign 3 credits
            credits = 3
            department = re.match(r"[A-Za-z]+", course).group() if re.match(r"[A-Za-z]+", course) else "TRANSFER"

        # Step 2: Determine the attribute category
        if department in ["CSE", "CSB"]:
            # For CSB majors, treat CSE and CSB courses as electives
            if department == "CSB":
                csb_electives -= credits
                print(f"[DEBUG] Course {course} ({department}) classified as CSB elective, subtracting {credits} credits. Remaining CSB electives: {csb_electives}")
            else:
                cse_electives -= credits
                print(f"[DEBUG] Course {course} ({department}) classified as CSE elective, subtracting {credits} credits. Remaining CSE electives: {cse_electives}")
        else:
            # Check attributes in course_attr table
            curr.execute("SELECT attr_name FROM course_attr WHERE courseid = %s", (course,))
            attributes = [row[0] for row in curr.fetchall()]

            if "HU" in attributes or "SS" in attributes:
                hss -= credits
                print(f"[DEBUG] Course {course} classified as HSS (attributes: {attributes}), subtracting {credits} credits. Remaining HSS: {hss}")
            elif "NS" in attributes:
                science_tech -= credits
                print(f"[DEBUG] Course {course} classified as science_tech (attributes: {attributes}), subtracting {credits} credits. Remaining science_tech: {science_tech}")
            else:
                # Default to free electives if no specific attribute is found
                free -= credits
                print(f"[DEBUG] Course {course} classified as free elective, subtracting {credits} credits. Remaining free electives: {free}")

    return hss, free, science_tech, cse_electives, csb_electives

def CSE_elective_calculation(taken_elective_courses, hss, free, science_tech, cse_electives):
    for course in taken_elective_courses:
        # Step 1: Fetch credit information from the course table
        curr.execute("SELECT credits, department FROM course WHERE courseid = %s", (course,))
        course_info = curr.fetchone()
        
        if course_info:
            credits, department = course_info
        else:
            # If the course is not found, assume it's a transfer and assign 3 credits
            credits = 3
            department = re.match(r"[A-Za-z]+", course).group() if re.match(r"[A-Za-z]+", course) else "TRANSFER"

        # Step 2: Determine the attribute category
        if department == "CSE":
            # Determine if it's a CSE elective or science_tech
            level = int(course[3:])  # Extract course level (e.g., 007, 202)
            if level >= 200:
                cse_electives -= credits
            else:
                science_tech -= credits
        else:
            # Check attributes in course_attr table
            curr.execute("SELECT attr_name FROM course_attr WHERE courseid = %s", (course,))
            attributes = [row[0] for row in curr.fetchall()]

            if "HU" in attributes or "SS" in attributes:
                hss -= credits
            elif "NS" in attributes:
                science_tech -= credits
            else:
                # Default to free electives if no specific attribute is found
                free -= credits
    

    return hss, free, science_tech, cse_electives

def build_tuple_list(remaining_courses, dummySubjects):
    result = []

    # Step 1: Iterate over remaining courses and fetch credits from the database
    for course in remaining_courses:
        curr.execute("SELECT credits FROM course WHERE courseid = %s", (course,))
        course_info = curr.fetchone()

        if course_info:
            credits = course_info[0]  # Get the credits from the query result
        else:
            # If the course is not found in the database, assume a default of 3 credits
            credits = 3

        # Add the course and its credits to the result list
        result.append({
            "course": course,
            "credits": credits
        })

    # Step 2: Add dummy subjects to the result list
    result.extend(dummySubjects)

    return result

def make_dummy_subject(hss, free, science_tech, cse_electives, csb_electives):
    dummy_subjects = []
    subject_counter = {
        'HSS': 1,
        'FREE': 1,
        'SCI_TECH': 1,
        'CSE_ELEC': 1,
        'CSB_ELEC': 1
    }

    # Helper function to generate subject names
    def generate_subject_name(category):
        count = subject_counter[category]
        subject_counter[category] += 1
        return f"{category}_{chr(64 + count)}"

    # 1. HSS 처리 (4 크레딧으로 최대한 바인딩 후 남은 것은 3 크레딧으로)
    while hss >= 4:
        dummy_subjects.append({
            "course": generate_subject_name("HSS"),
            "credits": 4
        })
        hss -= 4
    
    if hss > 0:
        dummy_subjects.append({
            "course": generate_subject_name("HSS"),
            "credits": 3
        })
        hss -= 3

    # 2. FREE 처리 (모두 3 크레딧으로)
    while free > 0:
        dummy_subjects.append({
            "course": generate_subject_name("FREE"),
            "credits": 3
        })
        free -= 3

    # 3. SCIENCE TECH 처리 (모두 3 크레딧으로)
    while science_tech > 0:
        dummy_subjects.append({
            "course": generate_subject_name("SCI_TECH"),
            "credits": 3
        })
        science_tech -= 3

    # 4. CSE ELECTIVE 처리 (모두 3 크레딧으로)
    while cse_electives > 0:
        dummy_subjects.append({
            "course": generate_subject_name("CSE_ELEC"),
            "credits": 3
        })
        cse_electives -= 3

    # 5. CSB ELECTIVE 처리 (모두 3 크레딧으로)
    while csb_electives > 0:
        dummy_subjects.append({
            "course": generate_subject_name("CSB_ELEC"),
            "credits": 3
        })
        csb_electives -= 3

    return dummy_subjects

def generate_course_json(final_remaining_courses, selected_semesters):
    result = []

    # Helper function to extract department
    def extract_department(course_id):
        # Extract department from course ID (e.g., CSE017 -> CSE)
        return re.match(r"[A-Za-z]+", course_id).group() if re.match(r"[A-Za-z]+", course_id) else "UNKNOWN"

    # Step: Process final remaining courses
    for course_info in final_remaining_courses:
        course_id = course_info["course"]
        credits = course_info["credits"]
        
        # Set default title to course ID
        title = course_id

        # Extract department
        department = extract_department(course_id)
        
        # Fetch semesters from course_semester table
        curr.execute("SELECT semester FROM course_semester WHERE courseid = %s", (course_id,))
        semesters_data = [row[0] for row in curr.fetchall()]

        # Deduce future semesters based on the pattern and add upcoming semesters
        all_semesters = set()
        current_year = datetime.now().year
        for semester in semesters_data:
            year = int(semester[:4])
            term_code = semester[-2:]
            
            # Add this semester and future semesters up to 4 years from the current year
            for i in range(0, 5):
                future_year = year + i
                if future_year <= current_year + 4:  # Limit to 4 years from now
                    future_semester = f"{future_year}{term_code}"
                    all_semesters.add(future_semester)

        # Add selected upcoming semesters (e.g., 202510)
        for sem in selected_semesters:
            all_semesters.add(str(sem))

        # Sort and convert to list
        sorted_semesters = sorted(list(all_semesters))

        all_prereqs = set()
         # Fetch prereqs from course_semester table
        curr.execute("SELECT * FROM prereq WHERE courseid = %s", (course_id,))
        prereqs = [(row[1],row[2]) for row in curr.fetchall()]
        if prereqs:
            groupNum = prereqs[0][0]
            all_prereqs.add(prereqs[0][1])
            for prereq in prereqs:
                currGroupNum = prereq[0]
                if currGroupNum == groupNum:
                    continue
                else:
                    all_prereqs.add(prereq[1])
            
            sorted_prereqs = sorted(list(all_prereqs))


        # Create course JSON object
        course_data = {
            "courseID": course_id,
            "department": department,
            "number": ''.join(filter(str.isdigit, course_id)),
            "title": title,
            "credits": credits,
            "attributes": [],
            "semesters": sorted_semesters,
            "prerequisites": sorted_prereqs  #TODO
        }
        result.append(course_data)

    return result



@app.route('/', methods=['POST'])
def requirements_calculation():
    data = request.json
    print("Received Data:", data)
    
    goal_major = data['goalMajor'] # Major goal
    
    # Courses already taken by the user
    taken_courses = set(data['takenCourses'])

    # If there are ENGL001 or ENGL002, change them to WRT001, WRT002 - Special case due to a change in the course name
    if "ENGL001" in taken_courses:
        taken_courses.remove("ENGL001")
        taken_courses.add("WRT001")
    if "ENGL002" in taken_courses:
        taken_courses.remove("ENGL002")
        taken_courses.add("WRT002")

    selected_credits = data['selectedCredits']
    
    start_semester = convert_semester_code(data['startSemester'])
    end_semester = convert_semester_code(data['endSemester'])
    
    # Additional user preferences (currently not used but preserved in the data structure)
    user_preferences = data['userPreferences']
    
    # Retrieve required courses for the major from the database
    curr.execute("SELECT courseid FROM major_requirements_courses WHERE major_requirementid = %s", (goal_major,))
    required_courses = set([row[0] for row in curr.fetchall()])

    # Fetch additional major information from the database
    curr.execute("SELECT hss, free, science_tech, cse_electives, csb_electives FROM major_requirements WHERE major_requirementid = %s", (goal_major,))
    major_info = curr.fetchone()

    # Filter out courses that have not been taken
    remaining_courses = list(required_courses - taken_courses)
    electives_taken = list(taken_courses - required_courses)
    
    if "CSE007" not in remaining_courses:
        # Remove CSE003, 004
        if "CSE003" in remaining_courses:
            remaining_courses.remove("CSE003")
        if "CSE004" in remaining_courses:
            remaining_courses.remove("CSE004")
    elif "CSE004" in remaining_courses or "CSE003" in remaining_courses:
        if "CSE007" in remaining_courses:
            remaining_courses.remove("CSE003")

    # Return all relevant data as a response
    mock_data = {
        'goalMajor': goal_major,
        'remainingCourses': remaining_courses,
        'takenElectiveCourses': electives_taken,
        'startSemester': start_semester,
        'endSemester': end_semester,
        'selectedCredits': selected_credits,
        'userPreferences': user_preferences,
        'hss': major_info[0],
        'free': major_info[1],
        'science_tech': major_info[2],
        'cse_electives': major_info[3],
        'csb_electives': major_info[4]
    }
    
    # Apply additional CSE-specific logic
    if goal_major == "CSE":
        mock_data['hss'], mock_data['free'], mock_data['science_tech'], mock_data['cse_electives'] = CSE_elective_calculation(
            electives_taken, mock_data['hss'], mock_data['free'], mock_data['science_tech'], mock_data['cse_electives']
        )
    elif goal_major == "CSB":
        mock_data['hss'], mock_data['free'], mock_data['science_tech'], mock_data['cse_electives'], mock_data['csb_electives'] = CSB_elective_calculation(
            electives_taken, mock_data['hss'], mock_data['free'], mock_data['science_tech'], mock_data['cse_electives'], mock_data['csb_electives']
        )

    # Generate dummy subjects for remaining requirements
    mock_data['dummySubjects'] = make_dummy_subject(
        mock_data['hss'], mock_data['free'], mock_data['science_tech'], mock_data['cse_electives'], mock_data['csb_electives']
    )

    # Build a list of tuples for the remaining courses and dummy subjects
    final_remaining_courses = build_tuple_list(mock_data['remainingCourses'], mock_data['dummySubjects'])
    final_json = generate_course_json(final_remaining_courses, [202510])
    print("--------------------------------------") 
    print("Final Remaining Courses:", final_json)

    return 

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
