import requests
from time import sleep
import pandas as pd

params = {"department": "CMSC", "limit": 300}
cs_courses_data = requests.get("https://api.planetterp.com/v1/courses", params=params).json()

cs_course_nums = []

for course in cs_courses_data:
    cs_course_nums.append(course['department'] + str(course['course_number']))


# create dictionary with key as course name and value as sum of grades in course for most recent semester
course_counts = {}
for course in cs_course_nums:
    course_counts[course] = 0


# get grades for each course in dictionary
semester = "202108" # fall 2021
for course in course_counts.keys():
    params = {"course": course, "semester": semester}

    # for each course returns a list of sections with corresponding grade data
    sections = requests.get("https://api.planetterp.com/v1/grades", params=params).json()

    total_students = 0
    for section in sections:
        # convert section dictionary into list so only preserve items that have grade counts
        section_grades = list(section.items())[4:]
        for grade in section_grades:
            # add number of students who got this grade in this section to total students for class
            total_students += grade[1]

    # print("{}: {}".format(course, total_students))

    course_counts[course] = total_students

    #sleep(0.5)

# create dataframe from course counts
data_dict = {"course_name": course_counts.keys(), "count": course_counts.values()}

courses_df = pd.DataFrame.from_dict(data_dict)

courses_df.to_csv("umd.csv")

print(courses_df)
