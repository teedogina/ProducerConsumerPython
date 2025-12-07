import random
import xml.etree.ElementTree as ET
from faker import Faker
import os


PROGRAMMES = ["Information Technology", "Software Engineering", "Data Science", "Cybersecurity"]
COURSES = {
    "CSC453": "Database Systems",
    "CSC442": "Operating Systems",
    "CSC408": "Computer Networks",
    "CSC401": "Integrative Programming Technologies",
    "CSC402": "Artificial Intelligence",
    "CSC411": "Software Engineering Principles",
    "CSC422": "Cybersecurity",
    "CSC433": "Digital Forensics"
}
NUM_COURSES = 5
BUFFER_DIR = "xml_buffer"
XML_FILE_COUNT = 10

fake = Faker()

# ITStudent Class


class ITStudent:
    def __init__(self, student_name, student_id, programme, courses):
        self.student_name = student_name
        self.student_id = student_id
        self.programme = programme
        self.courses = courses  
        self.average = self.calculate_average()
        self.result = self.determine_result()

    def calculate_average(self):
        if not self.courses:
            return 0
        return round(sum(self.courses.values()) / len(self.courses), 2)

    def determine_result(self):
        return "PASS" if self.average >= 50 else "FAIL"

    def __str__(self):
        course_lines = "\n".join(
            f"   {code} ({COURSES.get(code,'Unknown')}): {mark}%"
            for code, mark in self.courses.items()
        )
        return (
            f"\nStudent: {self.student_name}\n"
            f"ID: {self.student_id}\n"
            f"Programme: {self.programme}\n"
            f"Courses & Marks:\n{course_lines}\n"
            f"Average: {self.average}%\n"
            f"Result: {self.result}\n"
        )



def generate_random_student():
    name = fake.name()
    year = random.randint(2020, 2025)
    random_part = random.randint(1000, 9999)
    student_id = f"{year}{random_part}"
    programme = random.choice(PROGRAMMES)
    selected_courses = random.sample(list(COURSES.keys()), NUM_COURSES)
    courses_with_marks = {code: random.randint(40, 100) for code in selected_courses}
    return ITStudent(name, student_id, programme, courses_with_marks)

# Wrap / Unwrap XML


def wrap_student_to_xml(student_obj, file_number):
    root = ET.Element("ITStudent")
    root.set("id", student_obj.student_id)
    root.set("programme", student_obj.programme)

    ET.SubElement(root, "StudentName").text = student_obj.student_name
    courses_element = ET.SubElement(root, "Courses")
    for code, mark in student_obj.courses.items():
        course_el = ET.SubElement(courses_element, "Course")
        course_el.set("code", code)
        course_el.set("title", COURSES.get(code,"Unknown"))
        ET.SubElement(course_el, "Mark").text = str(mark)

    os.makedirs(BUFFER_DIR, exist_ok=True)
    file_name = f"student{file_number}.xml"
    file_path = os.path.join(BUFFER_DIR, file_name)

    tree = ET.ElementTree(root)
    ET.indent(tree, space="\t", level=0)
    tree.write(file_path, encoding="utf-8", xml_declaration=True)

   
    return file_name

def unwrap_xml_to_student(file_number):
    file_name = f"student{file_number}.xml"
    file_path = os.path.join(BUFFER_DIR, file_name)
    if not os.path.exists(file_path):
        return None
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()
        student_id = root.get("id")
        programme = root.get("programme")
        student_name = root.find("StudentName").text
        courses_data = {}
        for course_el in root.find("Courses"):
            code = course_el.get("code")
            mark = int(course_el.find("Mark").text)
            courses_data[code] = mark

        
        with open(file_path, "w") as f:
            f.write("")

        return ITStudent(student_name, student_id, programme, courses_data)

    except ET.ParseError:
        print(f"[ERROR] Could not parse {file_name}")
        return None
    except Exception as e:
        print(f"[ERROR] Fatal error unwrapping {file_name}: {e}")
        return None
def student_to_html(student):
    html = f"""
    <html>
    <head><title>{student.student_name}</title></head>
    <body>
        <h2>Student Details</h2>
        <p><b>Name:</b> {student.student_name}</p>
        <p><b>ID:</b> {student.student_id}</p>
        <p><b>Programme:</b> {student.programme}</p>
        <h3>Courses & Marks</h3>
        <table border="1" cellpadding="5">
            <tr><th>Course Code</th><th>Title</th><th>Mark</th></tr>
    """
    for code, mark in student.courses.items():
        html += f"<tr><td>{code}</td><td>{COURSES.get(code,'Unknown')}</td><td>{mark}%</td></tr>"

    html += f"""
        </table>
        <p><b>Average:</b> {student.average}%</p>
        <p><b>Result:</b> {student.result}</p>
    </body>
    </html>
    """
    html_path = os.path.join(BUFFER_DIR, f"{student.student_id}.html")
    with open(html_path, "w") as f:
        f.write(html)

