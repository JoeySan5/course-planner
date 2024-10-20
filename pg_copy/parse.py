import json
import psycopg2

# Establishing Connection
conn = psycopg2.connect(
    dbname="postgres",
    user="postgres",
    password="9089223654",
    host="database-1.cqqwg6frglat.us-west-2.rds.amazonaws.com",
    port="5432"
)

curr = conn.cursor()

def predict_offered_terms(historic_course_terms):
    odd_spring = True
    even_spring = True
    odd_fall = True
    even_fall = True

    terms_since_2019 = [201910, 201940, 202010, 202040, 202110, 202140, 202210, 202240, 202310, 202340, 202410, 202440, 202510]

    # historic_course_terms = [202010, 202040, 202140, 202240, 202410, 202440]
    historic_course_terms.sort()
    # If the course hasn't been offered since 2019, we assume it will not be offered in the future
    if len(historic_course_terms) == 0:
        return []
    offered_since = historic_course_terms[0]

    spring_suffix = 10
    fall_suffix = 40
    end_year = 2031

    for term in terms_since_2019:
        if term in historic_course_terms:
            # If the course was offered this term, we don't disqualify any categories
            continue
        elif term < offered_since:
            # If this term was before the course was ever offered, we don't disqualify any categories
            continue
        else:
            # If the course was not offered this term, we disqualify some category
            spring = term % 20 == spring_suffix % 20
            fall = term % 20 == fall_suffix % 20
            odd_year = term // 100 % 2 == 1
            even_year = term // 100 % 2 == 0
            if spring and odd_year:
                odd_spring = False
            elif spring and even_year:
                even_spring = False
            elif fall and odd_year:
                odd_fall = False
            elif fall and even_year:
                even_fall = False
            
            

    offered_terms = []
    offered_terms = list(set(historic_course_terms))
    for year in range(2025, end_year):
        odd = year % 2 == 1
        if odd:
            if odd_spring:
                offered_terms.append(year * 100 + spring_suffix)
            if odd_fall:
                offered_terms.append(year * 100 + fall_suffix)
        else:
            if even_spring:
                offered_terms.append(year * 100 + spring_suffix)
            if even_fall:
                offered_terms.append(year * 100 + fall_suffix)
    # Ensure unique terms and sort them
    offered_terms = list(set(offered_terms))
    offered_terms.sort()
    return offered_terms[len(historic_course_terms):]

# first we want to iterate through all the semesters to insert all the courses & their prereqs into db
# we want to enter all the semesters they have been in as well
# we will store the semesters into map with k=subject_course & v=semesterlist
# then we can iterate through map & insert the updated course_semesters

# year = "2019"
# season = "spring"

# # iterate through all json files
# course_semester_map = {}
# for i in range(0, 13):
#     print(i)
    
#     with open(year + "_" + season + ".json", 'r') as file:
#         data = json.load(file)

#         added_courses = set()
#         course_inserts = []
#         semester_inserts = []
#         attr_inserts = []

#         for course in data:
#             # Extract required fields
#             subject_course = course.get('subjectCourse')
#             if subject_course in added_courses:
#                 continue
#             added_courses.add(subject_course)

#             credit_hours = course.get('creditHourLow')
#             department = course.get('subject')
#             semester = course.get('term')

            
#             # we only want to insert into rds if subject_course has not already been inputted
#             # we also only want to insert attributes once for a course
#             if subject_course not in course_semester_map:
#                 course_inserts.append((subject_course, credit_hours, department))
#                 section_attr = course.get("sectionAttributes", [])
#                 for attr in section_attr:
#                     attr_code = attr.get("code")
#                     if attr_code:
#                         attr_inserts.append((subject_course, attr_code))
                
#             # Insert semester information into course_semester table
#             semester_inserts.append((subject_course, semester))

#             # update course_semester_map
#             if subject_course in course_semester_map:
#                 course_semester_map[subject_course].append(int(semester))
#             else:
#                 course_semester_map[subject_course] = [int(semester)]
 
#         # Batch Insert Courses
#         if course_inserts:
#             insert_course_query = """
#             INSERT INTO course (courseid, credits, department)
#             VALUES (%s, %s, %s)
#             ON CONFLICT DO NOTHING;
#             """
#             curr.executemany(insert_course_query, course_inserts)
#             print(f"Inserted {len(course_inserts)} courses into the database.")

#         # Batch Insert Semesters
#         if semester_inserts:
#             insert_semester_query = """
#             INSERT INTO course_semester (courseid, semester)
#             VALUES (%s, %s)
#             ON CONFLICT (courseID, semester) DO NOTHING;
#             """
#             curr.executemany(insert_semester_query, semester_inserts)
#             print(f"Inserted {len(semester_inserts)} semesters into the database.")

#         # Batch Insert Attributes
#         if attr_inserts:
#             insert_attr_query = """
#             INSERT INTO course_attr (courseid, attr_name)
#             VALUES (%s, %s)
#             ON CONFLICT (courseID, attr_name) DO NOTHING;
#             """
#             curr.executemany(insert_attr_query, attr_inserts)
#             print(f"Inserted {len(attr_inserts)} semesters into the database.")

    
#     if season == "spring":
#         season = "fall"
#     else:
#         season = "spring"
#         intyear = int(year)
#         intyear += 1
#         year = str(intyear)

# conn.commit()



# here we are both adding to both prereq table & to (future) semester table
# we only want to iterate through the subject_courses once
# Fetch all courses from the database
fetch_courses_query = "select courseid, semester from course natural join course_semester"
curr.execute(fetch_courses_query)
courses_data = curr.fetchall()  # This will return a list of tuples (one tuple per course)
course_semester = {}
for course,semester  in courses_data:
    if course not in course_semester:
        course_semester[course] = [int(semester)]
    else:
        course_semester[course].append(int(semester))
fetch_courses_query = "select courseid from course"
curr.execute(fetch_courses_query)
all_courses = curr.fetchall() #returns a list of all courses

prereq_inserts = []
term_inserts =[]

for course in all_courses:
    subject_course = course[0]
    with open("course_prereqs.json", 'r') as prereq_file:
        prerequisites = json.load(prereq_file)
        prereq = prerequisites.get(subject_course)

        # now must iterate through prereq list[][] & organize by group
        # i.e all prereq in an inner array are in group 0, then next inner array are in group 1
        groupNum = 0
        if prereq is not None:
            for group in prereq:
                # iterating through each pre req course in a group
                for c in group:
                    if c in course_semester:
                        prereq_inserts.append((subject_course, groupNum, c))

                        groupNum += 1   

    print('we are finding predicted terms for subect' + subject_course)
    print(course_semester[subject_course])
    
    list_of_predicted_terms = predict_offered_terms(course_semester[subject_course])
    print(list_of_predicted_terms)
    for predicted_term in list_of_predicted_terms:
        # insert future semester
        # Insert semester entity
        if predicted_term:
            term_inserts.append((subject_course, predicted_term))
        
print("now inserting")
insert_prereq_query = """
                        INSERT INTO prereq (courseid, groupid, preReqid)
                        VALUES (%s, %s, %s)
                        ON CONFLICT (courseID, groupID, preReqID) DO NOTHING;
                        """
curr.executemany(insert_prereq_query, prereq_inserts)

conn.commit()
print(f"Inserted {len(prereq_inserts)} semesters into the database.")


insert_semester_query = """
        INSERT INTO course_semester (courseid, semester)
        VALUES (%s, %s)
        """
curr.executemany(insert_semester_query, term_inserts)

conn.commit()
print(f"Inserted {len(term_inserts)} semesters into the database.")




curr.close()
conn.close()
