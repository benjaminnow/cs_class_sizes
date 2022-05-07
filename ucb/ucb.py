from bs4 import BeautifulSoup
from requests_html import HTMLSession
import json
import time
import pandas as pd

url = "https://classes.berkeley.edu/search/class?page="
url2 = "&f[0]=im_field_subject_area%3A483&f[1]=im_field_term_name%3A2208"
pages = 5
session = HTMLSession()

course_names = []
course_codes = []
course_enrollments = []
course_capacities = []

for i in range(0, pages):
    res = session.get(url + str(i) + url2)
    res.html.render(sleep=1)

    soup = BeautifulSoup(res.text, 'html.parser')

    results = soup.find_all("li", {"class": "search-result"})


    results_data = []

    for result in results:
        # cross listed courses in tag data-json, if not cross listed, will not be key in json
        # data-json has combined enrollment counts, and enrollment for just cs version
        # course link in tag data-node, but not needed since already have enrollment counts in data-json
        results_data.append(json.loads(result.div['data-json']))

    # key - course code
    # value - list of cross listed course links so can visit pages later and enrollment counts
    cross_listing_links = {}

    for data in results_data:
        course_names.append(data["class"]["course"]["title"])
        course_codes.append(data["class"]["course"]["displayName"])
        course_enrollments.append(data["enrollmentStatus"]["enrolledCount"])
        course_capacities.append(data["enrollmentStatus"]["maxEnroll"])

        if "crossListing" in data:
            links = []
            for attribute, value in data["crossListing"].items():
                links.append("https://classes.berkeley.edu/" + data["crossListing"][attribute]["path"])

            cross_listing_links[data["class"]["course"]["displayName"]] = links

    # handle cross listed courses by getting their enrollment info by visiting the links

    for course_code in cross_listing_links:
        for link in cross_listing_links[course_code]:
            res = session.get(link)
            res.html.render(sleep=1)
            soup = BeautifulSoup(res.text, 'html.parser')
            data = json.loads(soup.find("div", {"class": "handlebarData theme_is_whitehot"})["data-json"])
            
            # add cross listed course data
            course_names.append(data["class"]["course"]["title"])
            course_codes.append(data["class"]["course"]["displayName"])
            course_enrollments.append(data["enrollmentStatus"]["enrolledCount"])
            course_capacities.append(data["enrollmentStatus"]["maxEnroll"])

            time.sleep(1)

    # sleep for each page
    time.sleep(1)


classes_df = pd.DataFrame({"course_code": course_codes, "course_name": course_names, "course_enrollment": course_enrollments, "course_capacity": course_capacities})
classes_df.to_csv("ucb.csv")
print(classes_df)