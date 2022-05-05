import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
from time import sleep
import json


# res = requests.post("https://oscar.gatech.edu/bprod/bwckschd.p_get_crse_unsec",
#     data='term_in=202108&sel_subj=dummy&sel_day=dummy&sel_schd=dummy&sel_insm=dummy&sel_camp=dummy&sel_levl=dummy&sel_sess=dummy&sel_instr=dummy&sel_ptrm=dummy&sel_attr=dummy&sel_subj=CS&sel_crse=&sel_title=&sel_schd=%25&sel_from_cred=&sel_to_cred=&sel_camp=A&sel_ptrm=%25&sel_instr=%25&sel_attr=%25&begin_hh=0&begin_mi=0&begin_ap=a&end_hh=0&end_mi=0&end_ap=a',
#     headers={
#         "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
#         "Accept-Encoding": "gzip, deflate, br",
#         "Accept-Language": "en-US,en;q=0.5",
#         "Connection": "keep-alive",
#         "Content-Type": "application/x-www-form-urlencoded",
#         "DNT": "1",
#         "Origin": "https://oscar.gatech.edu",
#         "Referer": "https://oscar.gatech.edu/bprod/bwckgens.p_proc_term_date",
#         "Sec-Fetch-Dest": "document",
#         "Sec-Fetch-Mode": "navigate",
#         "Sec-Fetch-Site": "same-origin",
#         "Sec-Fetch-User": "?1",
#         "Upgrade-Insecure-Requests": "1",
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:99.0) Gecko/20100101 Firefox/99.0"
#     },
#     cookies={
#         "BIGipServer~BANNER~oscar.coda_443": "572230154.64288.0000"
#     },
#     auth=(),
# )

# # save response in html so don't have to do 10 sec query every time
# with open("gatech.html", "w") as f:
#     f.write(res.text)


# link to class with seats is of form bprod/bwckschd.p_disp_detail_sched?term_in=202108&crn_in=93519
# get all links on page and filter for links like this

f = open("gatech.html", "r")

soup = BeautifulSoup(f, 'html.parser')

links = soup.find_all('a')

class_links = []
class_titles = []

for link in links:
    if link.get('href') != None and "bprod/bwckschd.p_disp_detail_sched?term_in=202108" in link.get('href'):
        class_links.append(link.get('href'))
        class_titles.append(link.get_text())

f.close()

class_data = {"title": class_titles, "link": class_links}

classes_df = pd.DataFrame.from_dict(class_data)

# print(classes_df)

# extracting class name from title which has other junk

classes_df["class_name"] = ""

for index, row in classes_df.iterrows():
    class_name = re.findall("CS \d{4}", row['title'])[0]
    classes_df.at[index, "class_name"] = class_name

# when adding up class counts, make sure to exclude those which are:
# - recitations
# - studios
# - supervised/unsupervised laboratory
# - directed study
# - dissertation
# - thesis
# once go to link, can find class type on page, credit number
# basically only look for lecture type with credits > 0, which can be found on class page


# add columns to classes_df
# - type
# - credits
# - seat_capacity
# - filled_seats

classes_df["type"] = ""
classes_df["credits"] = 0.0
classes_df["seat_capacity"] = 0
classes_df["filled_seats"] = 0

# list of links that had problems:
# will save them to a file after program over
problem_links = []

# go to all the links and fill in these two columns
for index, row in classes_df.iterrows():
    print(row["class_name"])

    link = "https://oscar.gatech.edu" + row["link"]
    res = requests.get(link)

    class_soup = BeautifulSoup(res.content, 'html.parser')

    # page is mostly made up of tables
    tables = class_soup.find_all('table')
    # assuming that the table of interest will always be at index 3, could be problems here
    # if not always true...
    data_table = tables[3]

    match_class_type = re.search("(\w+)\* Schedule Type", data_table.text)
    if match_class_type:
        classes_df.at[index, "type"] = match_class_type.group(1)
    else:
        print("for {} was unable to find class type".format(link))
        problem_links.append(link)

    match_class_credits = re.search("(\d\.\d{3}) Credits", data_table.text)
    if match_class_credits:
        classes_df.at[index, "credits"] = match_class_credits.group(1)
    else:
        print("for {} was unable to find class credits".format(link))
        problem_links.append(link)

    match_class_seats = re.search("Seats\n(\d+)\n(\d+)\n", data_table.text)
    if match_class_seats:
        classes_df.at[index, "seat_capacity"] = match_class_seats.group(1)
        classes_df.at[index, "filled_seats"] = match_class_seats.group(2)
    else:
        print("for {} was unable to find class seats".format(link))
        problem_links.append(link)

    # update at every iteration so no data lost
    classes_df.to_csv("gatech.csv")
    
    sleep(2)
   

classes_df.to_csv("gatech.csv")

# writing problem links list to json in case have to examine later
with open("problem_links.json", "w") as f:
    f.write(json.dumps(problem_links))

print(classes_df)