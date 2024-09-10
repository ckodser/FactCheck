import json
import time

import requests
from bs4 import BeautifulSoup
import jdatetime
import datetime
import pandas as pd

url = "https://nabzebourse.com/fa/news/29381/stock-symbols-news#h_8583877259761626265858786"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

body = soup.find_all('div', class_='body')[0]
group_names=body.find_all("h2")[1:]
tables = body.find_all("table")
print(len(tables), len(group_names))
stock_names={}
for group, table in zip(group_names, tables):
    name=group.get_text()
    stock_names[name]=[]
    for stockwithlink in table.find_all("a"):
        stock_names[name].append(stockwithlink.get_text())

with open('data/stock_names.json', 'w', encoding='utf-8') as json_file:
    json.dump(stock_names, json_file, indent=4)
# for post_text_div in post_text_divs:
#     for p in post_text_div.find_all("p"):
#         text += p.get_text() + "\n"
#
# dateti = soup.find_all("i", class_="fa-calendar")[0].parent
# date = dateti.get_text().split()[:3]

