from flask import Flask, request, jsonify
import psycopg2
import re
import json

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
    # Debugging: print the response data
    print("Response Data:", mock_data)
    
    return jsonify(mock_data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
