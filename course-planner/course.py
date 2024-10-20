class Course:
    def __init__(self, courseID, department, number, title, credits, attributes, semesters, prerequisites):
        self.courseID = courseID
        self.department = department
        self.number = number
        self.title = title
        self.credits = credits
        self.attributes = attributes
        self.semesters = semesters
        self.prerequisites = prerequisites

    def __str__(self):
        return (f"Course ID: {self.courseID}\n"
                f"{self.department}-{self.number}\n"
                f"Title: {self.title}\n")
                # f"Credits: {self.credits}\n"
                # f"Attributes: {', '.join(self.attributes)}\n"
                # f"Prerequisites: {', '.join(self.prerequisites)}")
    
    def print_full(self):
        prerequisites_str = ', '.join(prereq.courseID for prereq in self.prerequisites)
        return (f"Course ID: {self.courseID}\n"
                f"{self.department}-{self.number}\n"
                f"Title: {self.title}\n"
                f"Credits: {self.credits}\n"
                f"Attributes: {', '.join(self.attributes)}\n"
                f"Prerequisites: {prerequisites_str}")
    
    def add_prerequisite(self, prerequisite):
        if any(prereq.courseID == prerequisite.courseID for prereq in self.prerequisites):
            print(f"Prerequisite Course with ID {prerequisite.courseID} already exists. Not adding duplicate.")
            return
        self.prerequisites.append(prerequisite)

    def offered_in_semester(self, semester):
        return semester in self.semesters
