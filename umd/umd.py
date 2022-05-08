import requests
from time import sleep
import pandas as pd


# get list of cs courses
params = {"department": "CMSC", "limit": 300}
cs_courses_data = requests.get("https://api.planetterp.com/v1/courses", params=params).json()

cs_course_nums = []

for course in cs_courses_data:
    cs_course_nums.append(course['department'] + str(course['course_number']))

# list of professors for each course so can get grades for each professor of the
# course during a specific semester to see how big lectures arec
course_professors = []

for course in cs_courses_data:
    course_professors.append(course["professors"])

class_names = []
class_sizes = []
class_profs = []

# get grades for each course in dictionary
semester = "202108" # fall 2021
for i, course in enumerate(cs_course_nums):
    for prof in course_professors[i]:
        params = {"course": course, "semester": semester, "professor": prof}

        # for each course returns a list of sections with corresponding grade data
        sections = requests.get("https://api.planetterp.com/v1/grades", params=params).json()

        print("{} {}".format(course, prof))
        for section in sections:
            # didn't get back a dictionary on the api call for some reason so skip
            # the reason seems to be inconsistent naming of professors so some
            # names of the same professor return nothing
            if not type(section) is dict:
                print("skipping")
                continue
            total_students_section = 0
            # convert section dictionary into list so only preserve items that have grade counts
            section_grades = list(section.items())[4:]
            for grade in section_grades:
                # add number of students who got this grade in this section to total students in section
                total_students_section += grade[1]
            
            # append section info to lists
            class_names.append(course)
            class_profs.append(prof)
            class_sizes.append(total_students_section)

        sleep(0.5)

# create dataframe from course counts
data_dict = {"course_name": class_names, "professor": class_profs, "count": class_sizes}

courses_df = pd.DataFrame.from_dict(data_dict)

courses_df.to_csv("umd.csv")

print(courses_df)
