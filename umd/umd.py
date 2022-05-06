import requests
from time import sleep
import pandas as pd

params = {"department": "CMSC", "limit": 300}
cs_courses_data = requests.get("https://api.planetterp.com/v1/courses", params=params).json()

cs_course_nums = []

for course in cs_courses_data:
    cs_course_nums.append(course['department'] + str(course['course_number']))

class_names = []
class_sizes = []

# get grades for each course in dictionary
semester = "202108" # fall 2021
for course in cs_course_nums:
    params = {"course": course, "semester": semester}

    # for each course returns a list of sections with corresponding grade data
    sections = requests.get("https://api.planetterp.com/v1/grades", params=params).json()

    
    for section in sections:
        total_students_section = 0
        # convert section dictionary into list so only preserve items that have grade counts
        section_grades = list(section.items())[4:]
        for grade in section_grades:
            # add number of students who got this grade in this section to total students in section
            total_students_section += grade[1]
        
        # append section info to lists
        class_names.append(course)
        class_sizes.append(total_students_section)

    sleep(0.5)

# create dataframe from course counts
data_dict = {"course_name": class_names, "count": class_sizes}

courses_df = pd.DataFrame.from_dict(data_dict)

courses_df.to_csv("umd.csv")

print(courses_df)
