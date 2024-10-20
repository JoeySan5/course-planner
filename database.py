# this file makes calls to the database & outputs them onto json files
import psycopg2
import json


def getMajorClasses(major):
    print('ghelo')
    # Establishing Connection
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",
        password="9089223654",
        host="database-1.cqqwg6frglat.us-west-2.rds.amazonaws.com",
        port="5432"
    )

    curr = conn.cursor()
    fetch_courses_query = """
    select courseid from major_requirements natural join major_requirements_courses
    where major_requirements.major_requirementid = %s
    """
    curr.execute(fetch_courses_query, (major,))
    courses_data = curr.fetchall()  # This will return a list of tuples (one tuple per course)
    print(courses_data)
    

getMajorClasses("CSE")


# we want to call all courses that are required for a degree audit 