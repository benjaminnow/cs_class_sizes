import requests
from bs4 import BeautifulSoup
import re

url = "https://oscar.gatech.edu/bprod/bwckschd.p_disp_detail_sched?term_in=202108&crn_in=87695"

res = requests.get(url)

soup = BeautifulSoup(res.content, 'html.parser')

data_table = soup.find_all('table')[3]

print(data_table.text)

match_class_type = re.search("(\w+)\* Schedule Type", data_table.text)

print(match_class_type.group(1))

match_class_credits = re.search("(\d\.\d{3}) Credits", data_table.text)

print(match_class_credits.group(1))

match_class_seats = re.search("Seats\n(\d+)\n(\d+)\n", data_table.text)

print(match_class_seats.group(1))
print(match_class_seats.group(2))