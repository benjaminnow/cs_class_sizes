from requests_html import HTMLSession
from bs4 import BeautifulSoup
import pandas as pd
import re

url = "http://crapuler.com/eecs?logname=Spring%2FSummer%2FFall+2021"

session = HTMLSession()

res = session.get(url)
res.html.render(sleep=1)

soup = BeautifulSoup(res.text, 'html.parser')

rows = soup.find("table").find_all("tr")

course_codes = []
course_links = []
course_types = []

for row in rows:
    data = row.find_all("td")
    
    i = 0
    is_fall_2021 = True
    while i < len(data) and is_fall_2021:
        if data[i].span.has_attr("title"):
            if data[i].span["title"] == "Term":
                # making sure fall 2021 course, if not go to next row
                if not "Fall 2021" in data[i].span.text:
                    is_fall_2021 = False
            elif data[i].span["title"] == "Enrollment History":
                # go up one element to get link
                link = row.find("a", href=True)
                course_codes.append(link.text)
                course_links.append("http://crapuler.com/" + link["href"])
            elif data[i].span["title"] == "Section Type":
                course_types.append(data[i].span.text)

        i += 1


# loop over course links to get individual section data

# lists for the dataframe 
course_codes_sections = []
course_types_sections = []
course_instructors_sections = []
course_times_sections = []
course_enrollments = []
course_capacities = []

for i, link in enumerate(course_links):
    res = session.get(link)
    res.html.render(sleep=2)

    soup = BeautifulSoup(res.text, 'html.parser')

    # assuming lecture table always first
    lecture_table = soup.find("table")

    # get table rows
    rows = lecture_table.find_all("tr")

    # check that this is lecture table
    if "Lectures" in rows[0].text:
        # loop rows, skip first 2 which don't have data we want
        for j in range(2, len(rows)):
            # get row data
            row_data = rows[j].find_all("td")

            course_codes_sections.append(course_codes[i])
            course_types_sections.append(course_types[i])
            
            # get instructor names
            instructor_links = row_data[1].find_all("a")
            instructors = []
            for instructor in instructor_links:
                instructors.append(instructor.text.strip())
            # sort so get consistent list of instructor names across sections if
            # need to combine some
            instructors.sort()
            course_instructors_sections.append(instructors)

            # remove whitespace for time
            time = re.sub("\s+", '', row_data[2].text)
            course_times_sections.append(time)

            # assuming enrolled always at index 4
            course_enrollments.append(int(row_data[4].text))
            # assuming capacity always at index 5
            course_capacities.append(int(row_data[5].text))
    else:
        print("at {}, lecture table not first".format(link))



classes_df = pd.DataFrame({"course_code": course_codes_sections, "course_type": course_types_sections, "course_enrollment": course_enrollments, "course_capacity": course_capacities, "course_time": course_times_sections, "course_instructors": course_instructors_sections})
classes_df.to_csv("umich.csv")

print(classes_df)

