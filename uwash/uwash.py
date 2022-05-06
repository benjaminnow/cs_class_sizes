import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

res = requests.get("https://www.washington.edu/students/timeschd/AUT2021/cse.html")

soup = BeautifulSoup(res.content, 'html.parser')

# tables will be table elements with class headings
# class enrollment information in tables between headings tables
# lectures have credits > 0 associated with them, discussions seem to have QZ as credits
class_heading_tables = soup.find_all("table", attrs={"bgcolor": "#ffcccc"})

all_tables = soup.find_all("table")

# in all_tables list get index where class heading table starts
start_index = 0
while all_tables[start_index] != class_heading_tables[0]:
    start_index += 1

# dictionary with key as class heading table and values as list of tables between current class
# heading and next class heading
associated_tables = {}

current_class_table = 0
current_table = start_index + 1
current_class_associated_tables = []

while current_table < len(all_tables):
    # add class heading table to dictionary if no associated classes yet, empty list
    if len(current_class_associated_tables) == 0:
        associated_tables[class_heading_tables[current_class_table]] = []

    if current_class_table < len(class_heading_tables) - 1:
        if not all_tables[current_table] == class_heading_tables[current_class_table + 1]:
            current_class_associated_tables.append(all_tables[current_table])
        else:
            # add associated tables to current class heading table in dict
            associated_tables[class_heading_tables[current_class_table]] = current_class_associated_tables
            # clear out associated tables because moving on to new class
            current_class_associated_tables = []
            # increase current class table
            current_class_table += 1
    else: # on last class heading table
        # just add class tables to associated list and then add list to dict after while loop over
        current_class_associated_tables.append(all_tables[current_table])

    current_table += 1

# for last class heading
associated_tables[class_heading_tables[current_class_table]] = current_class_associated_tables



# first_class_tables = list(associated_tables.keys())[0]

# text = first_class_tables.text

# print(text)

# group 1 - CSE
# group 2 - course number
# group 3 - course name, with a P at the end sometimes lol
course_search = "([A-Z]+)\s+(\d+)\s+((?:[A-Z]+\s*)+)"

# group 1 - credits either listed as 1, 1-1, or QZ
# group 2 - seats filled
# group 3 - seat capacity
section_search = "\d+\s+[A-Z0-9]+\s+([A-Z]+|\d+-\d+|\d+).*\s+(\d+)/\s+(\d+)"


class_codes = []
class_names = []
class_filled = []
class_capacity = []

for course in associated_tables:
    section_tables = associated_tables[course]
    
    heading_matches = re.search(course_search, course.text)
    print("{} {} {}".format(heading_matches.group(1), heading_matches.group(2), heading_matches.group(3)))
    
    for section in section_tables:
        section_matches = re.search(section_search, section.text)
        section_credits = section_matches.group(1)
        # checking that credits are numbers to indicate that it's a lecture, not discussion
        credits_num_search = re.search("\d+-\d+|\d+", section_credits)
        if credits_num_search:
            print("{} / {}".format(int(section_matches.group(2)), int(section_matches.group(3))))
            class_codes.append(heading_matches.group(1) + " " + heading_matches.group(2))
            class_names.append(heading_matches.group(3))
            class_filled.append(int(section_matches.group(2)))
            class_capacity.append(int(section_matches.group(3)))

classes_df = pd.DataFrame({"class_code": class_codes, "class_name": class_names, "class_filled": class_filled, "class_capacity": class_capacity})

print(classes_df)

classes_df.to_csv("uwash.csv")