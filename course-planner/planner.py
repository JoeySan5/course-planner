from graph import Graph
from course import Course

import json

class CoursePlanner:
    def __init__(self, start_semester, end_semester, min_credits_per_semester, max_credits_per_semester):
        self.courses = []
        self.course_graph = None
        self.start_semester = start_semester
        self.end_semester = end_semester
        self.semester_domain = self.find_semester_domain(start_semester, end_semester)
        self.semester_schedules = [[] for _ in range(len(self.semester_domain))]
        self.scheduled_credits = [0] * len(self.semester_domain)
        if min_credits_per_semester >= max_credits_per_semester:
            raise ValueError("Minimum credits per semester must be less than maximum credits per semester")
        self.min_credits_per_semester = min_credits_per_semester
        self.max_credits_per_semester = max_credits_per_semester

    def find_semester_domain(self, start_semester, end_semester):
        # Verify the format of the parameters
        def is_valid_semester(semester):
            year = semester // 100
            suffix = semester % 100
            return 2025 <= year <= 2040 and suffix in {10, 40}

        if not is_valid_semester(start_semester):
            raise ValueError(f"Invalid start semester format: {start_semester}")
        if not is_valid_semester(end_semester):
            raise ValueError(f"Invalid end semester format: {end_semester}")
        if start_semester > end_semester:
            raise ValueError("Start semester must be less than or equal to end semester")

        # Fill out all applicable numbers for the domain
        semesters = []
        start_year = start_semester // 100
        end_year = end_semester // 100
        for year in range(start_year, end_year + 1):
            if year == start_year and start_semester % 100 == 40:
                # If start semester is fall, add only fall of that year
                semesters.append(year * 100 + 40)
            elif year == end_year and end_semester % 100 == 10:
                #  If end semester is spring, add only spring of that year
                semesters.append(year * 100 + 10)
            else:
                semesters.append(year * 100 + 10)
                semesters.append(year * 100 + 40)
        return semesters
    

    # Step 1 functions: Main program should convert database data to Course objects and add them to the CoursePlanner object

    def add_course(self, course):
        # Check for duplicate courseID
        if any(existing_course.courseID == course.courseID for existing_course in self.courses):
            print(f"Course with ID {course.courseID} already exists. Not adding duplicate.")
            return
        self.courses.append(course)

    def remove_course(self, courseID):
        self.courses = [course for course in self.courses if course.courseID != courseID]
        print(f"Course {courseID} removed.")


    def print_debug(self):
        for course in self.courses:
            print(f"\n{course.print_full()}")


    # Step 2 functions: Build the graph of courses

    def build_graph(self):
        self.course_graph = Graph()
        courses_to_schedule = self.courses
        for course in courses_to_schedule:
            self.add_course_as_node(course)

    def add_course_as_node(self, course):
        if self.course_graph.contains(course):
            return
        if course.prerequisites == []:
            self.course_graph.add_node(course)
            return
        else:
            for prereq in course.prerequisites:
                self.add_course_as_node(prereq)
            self.course_graph.add_node(course, course.prerequisites)

    # Step 3 functions: Choose a schedule from the graph

    def choose_schedule(self):
        for i, semester in enumerate(self.semester_domain):
            print(f"\nChoosing schedule for semester {semester}")
            self.choose_schedule_for_semester(i, semester)
        return self.semester_schedules

    def choose_schedule_for_semester(self, i, semester):
        # Find not-yet-selected courses offered this semester
        courses_for_semester = [node for node in self.course_graph.nodes if (not node.selected and node.data.offered_in_semester(semester) and self.course_graph.all_predecessors_selected(node))]
        
        # Sort courses by height
        courses_for_semester.sort(key=lambda course: self.course_graph.super_heuristic(course, self.semester_domain), reverse=True)
        #  TODO: Use better heuristic for sorting courses

        # Add courses to the schedule
        schedule = []
        credits = 0
        for course_node in courses_for_semester:
            course = course_node.data
            if credits + course.credits <= self.max_credits_per_semester:
                schedule.append(course)
                self.course_graph.select_node(course_node)
                credits += course.credits
                if credits == self.max_credits_per_semester:
                    break
        self.scheduled_credits[i] = credits
        self.semester_schedules[i] = schedule

    # Output

    def print_academic_plan(self):
        for i, semester in enumerate(self.semester_domain):
            print(f"\n-----Semester {semester}-----({self.scheduled_credits[i]} credits)")
            for course in self.semester_schedules[i]:
                print(course)


    

def main():
    # Load courses from a JSON file
    with open('sample-courses-1.json', 'r') as file:
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

if __name__ == "__main__":
    main()

    