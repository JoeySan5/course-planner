from flask import Flask, request, jsonify
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

def classify_elective()
    
    
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000)
