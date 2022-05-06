from requests_html import HTMLSession
from bs4 import BeautifulSoup
import re
from time import sleep

session = HTMLSession()
cs_url = "https://madgrades.com/courses/3795cfcc-807e-3ca7-8348-d4a909a42f06?termCode=1222&instructorId=0"

res = session.get(cs_url)
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
    

print(total_students)

