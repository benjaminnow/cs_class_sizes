from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
import pandas as pd
from time import sleep
import json

# commented code gets class links, titles so can get class sizes in next step

# url = "https://madgrades.com/search?subjects%5B0%5D=266&query=&page="
# pages = 6
# session = HTMLSession()


# class_titles = []
# class_codes = []
# class_links = []

# for page in range(1, pages+1):

#     res = session.get(url + str(page))
#     res.html.render(sleep=1)

#     content = res.html.find("#root", first=True)

#     soup = BeautifulSoup(content.html, 'html.parser')

#     courses = soup.find_all("div", attrs={"class": "ui blue segment"})

#     for course in courses:
#         course_div = course.div
#         course_link = "https://madgrades.com" + course_div.a.get("href") + "?termCode=1222&instructorId=0"
#         spans = course_div.find_all("span")

#         text_data = []
#         for span in spans:
#             if span.parent.name != "span": # don't want nested span
#                 text_data.append(span.text)

#         course_number = re.search("(\d+)$", course_div.text).group(1)
#         text_data.append(course_number)

#         class_titles.append(text_data[0])
#         class_codes.append("".join(text_data[1:-1]) + " " + text_data[-1])
#         class_links.append(course_link)

#     sleep(2)


# classes_df = pd.DataFrame({'class_title': class_titles, 'class_code': class_codes, 'link': class_links})
# # adding class size column
# classes_df["class_size"] = 0
# print(classes_df)
# classes_df.to_csv("uwisc.csv")

classes_df = pd.read_csv("uwisc.csv")

session = HTMLSession()

problem_links = []

for index, row in classes_df.iterrows():
    res = session.get(row["link"])
    print(row["class_code"])
    # taking a second for the graph to load to let the page render for 1 sec
    res.html.render(sleep=1)

    graph = res.html.find(".row", first=True)

    soup = BeautifulSoup(graph.html, 'html.parser')

    grade_labels = soup.find_all("text", attrs={"text-anchor": "middle", "dominant-baseline": "middle"})

    current_sem_labels = grade_labels[7:]

    total_students = 0
    for label in current_sem_labels:
        label_count = re.search("\%(\d+)", label.text)
        if label_count:
            total_students += int(label_count.group(1))
        else:
            problem_links.append(row["link"])
        

    print(total_students)
    classes_df.at[index, "class_size"] = total_students

    # save csv each time just in case
    classes_df.to_csv("uwisc.csv")

    sleep(2)


# writing problem links list to json in case have to examine later
with open("problem_links.json", "w") as f:
    f.write(json.dumps(problem_links))

print(classes_df)
    
        
