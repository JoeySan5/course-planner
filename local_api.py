import json
from flask import Flask, request, jsonify
import sys
from course_planner.course import Course
from course_planner.planner import CoursePlanner
from course_planner.graph import Graph


app = Flask(__name__)

@app.route('/', methods=['POST'])
def receive_data():
    # JSON 데이터 수신
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


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
