import json
from flask import Flask, request, jsonify
import sys
from course_planner.course import Course
from course_planner.planner import CoursePlanner
from course_planner.graph import Graph

import psycopg2
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
    # '2024-Spring' -> '202410', '2027-Fall' -> '202740'
    year, term = semester_str.split('-')
    term_code = '10' if term == 'Spring' else '40'
    return f"{year}{term_code}"

@app.route('/', methods=['POST'])
def requirements_calculation():
    data = request.json
    print("Received Data:", data)
    
    # 성공 메시지 응답
    return jsonify({"message": "Data received successfully!"}), 200
@app.route('/', methods=['GET'])
def help():
    # JSON 데이터 수신
    
    
    # 성공 메시지 응답
    return jsonify({"message": "Data received successfully!"}), 200

@app.route('/test', methods=['GET'])
def test():


    # Load courses from a JSON file
    with open('course_planner/sample-courses-1.json', 'r') as file:
        courses_data = json.load(file)

    MIN_CREDITS = 12
    MAX_CREDITS = 18
    planner = CoursePlanner(start_semester=202510, end_semester=202610, min_credits_per_semester=MIN_CREDITS, max_credits_per_semester=MAX_CREDITS)

    # Create a dictionary to store Course objects by courseID
    courses_dict = {}


    # First pass: Create Course objects without prerequisites
    for course_data in courses_data:
        course = Course(
            courseID=course_data["courseID"],
            department=course_data["department"],
            number=course_data["number"],
            title=course_data["title"],
            credits=course_data["credits"],
            attributes=course_data["attributes"],
            semesters=course_data["semesters"],
            prerequisites=[]  # We'll add prerequisites in the second pass
        )
        courses_dict[course.courseID] = course
        planner.add_course(course)

    # Second pass: Add prerequisites to Course objects
    for course_data in courses_data:
        course = courses_dict[course_data["courseID"]]
        for prereq_id in course_data["prerequisites"]:
            course.add_prerequisite(courses_dict[prereq_id])

    # planner.print_debug()
    planner.build_graph()

    planner.choose_schedule()

    planner.print_academic_plan()
    # Iterate through planner.course_schedule and build a 2D array
    course_schedule_json = []
    for semester in planner.semester_schedules:
        semester_courses = []
        for course in semester:
            # Assuming course is an object, you can extract its attributes
            semester_courses.append({
                "courseID": course.courseID,
                "department": course.department,
            })
        course_schedule_json.append(semester_courses)
    # 성공 메시지 응답
    return jsonify(course_schedule_json), 200

    goal_major = data['goalMajor'] #Major goal
    
    # 사용자가 이미 수강한 과목들
    taken_courses = set(data['takenCourses'])

    # if there are ENGL001 or ENGL002, then change is WRT001, WRT002 - Special... becuase of the change in the course name
    if "ENGL001" in taken_courses:
        taken_courses.remove("ENGL001")
        taken_courses.add("WRT001")
    if "ENGL002" in taken_courses:
        taken_courses.remove("ENGL002")
        taken_courses.add("WRT002")

    selected_credits = data['selectedCredits']
    
    start_semester = convert_semester_code(data['startSemester'])
    end_semester = convert_semester_code(data['endSemester'])
    
    # 사용자의 추가적인 선호도 (현재는 사용하지 않지만 데이터 구조를 유지)
    user_preferences = data['userPreferences']
    
    # 데이터베이스에서 해당 전공의 필수 과목들을 가져오기
    curr.execute("SELECT courseid FROM major_requirements_courses WHERE major_requirementid = %s", (goal_major,))
    required_courses = set([row[0] for row in curr.fetchall()])

    # 데이터베이스에서 추가 전공 정보 가져오기
    curr.execute("SELECT hss, free, science_tech, cse_electives FROM major_requirements WHERE major_requirementid = %s", (goal_major,))
    major_info = curr.fetchone()

    # 수강하지 않은 과목들만 필터링
    remaining_courses = list(required_courses - taken_courses)
    eletives_taken = list(taken_courses - required_courses)
    if goal_major == "CSE":
        if "CSE007" not in remaining_courses:
            # delete CSE003, 004
            if "CSE003" in remaining_courses:
                remaining_courses.remove("CSE003")
            if "CSE004" in remaining_courses:
                remaining_courses.remove("CSE004")
        elif "CSE004" in remaining_courses or "CSE003" in remaining_courses:
            if "CSE007" in remaining_courses:
                remaining_courses.remove("CSE003")

    # 모든 데이터를 포함하여 결과 반환
    response_data = {
        'goalMajor': goal_major,
        'remainingCourses': remaining_courses,
        'takenElectiveCourses': eletives_taken,
        'startSemester': start_semester,
        'endSemester': end_semester,
        'selectedCredits': selected_credits,
        'userPreferences': user_preferences,
        'hss': major_info[0],
        'free': major_info[1],
        'science_tech': major_info[2],
        'cse_electives': major_info[3]
    }
    
    # 디버깅을 위한 응답 출력
    print("Response Data:", response_data)
    
    return jsonify(response_data)

    
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
