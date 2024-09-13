import json
import os
import time
from os.path import isfile

import requests
from bs4 import BeautifulSoup
import jdatetime
import datetime
import pandas as pd

arabic_to_persian = {
    'ك': 'ک',
    'ي': 'ی',
    'ة': 'ه',
    'ئ': 'ی',
    'ؤ': 'و',
    'أ': 'ا',
    'إ': 'ا',
    'آ': 'آ',
    'ء': 'ء',
    'ا': 'ا',
    'ب': 'ب',
    'پ': 'پ',
    'ت': 'ت',
    'ث': 'ث',
    'ج': 'ج',
    'چ': 'چ',
    'ح': 'ح',
    'خ': 'خ',
    'د': 'د',
    'ذ': 'ذ',
    'ر': 'ر',
    'ز': 'ز',
    'ژ': 'ژ',
    'س': 'س',
    'ش': 'ش',
    'ص': 'ص',
    'ض': 'ض',
    'ط': 'ط',
    'ظ': 'ظ',
    'ع': 'ع',
    'غ': 'غ',
    'ف': 'ف',
    'ق': 'ق',
    'ک': 'ک',
    'گ': 'گ',
    'ل': 'ل',
    'م': 'م',
    'ن': 'ن',
    'و': 'و',
    'ه': 'ه',
    'ی': 'ی',
    '۰': '۰',
    '۱': '۱',
    '۲': '۲',
    '۳': '۳',
    '۴': '۴',
    '۵': '۵',
    '۶': '۶',
    '۷': '۷',
    '۸': '۸',
    '۹': '۹',
}

def convert_arabic_to_persian(text):
    # Replace each Arabic character with its corresponding Persian character
    return ''.join(arabic_to_persian.get(char, char) for char in text)

# page-link
def get_next_page_url(soup, next_page):
    page_links = soup.find_all('a', class_='page-link')
    filtered_links = [link.get('href') for link in page_links if link.get_text().rstrip().lstrip() == str(next_page)]
    print(filtered_links)
    return filtered_links[0]


def get_news_in_page(soup):
    post_image_divs = soup.find_all('div', class_='post-meta')

    links = []
    for div in post_image_divs:
        # Find all <a> tags within the current <div>
        spans = div.find_all('span')
        for span in spans:
            is_good = False
            urls = []
            for a in span.find_all('a'):
                link = a.get('href')
                if link:
                    urls.append(link)
                buttons = a.find_all("button")
                if len(buttons) == 1 and buttons[0].get_text() == "آزاد":
                    is_good = True
            if is_good:
                links += urls
    return links


def parse_news(soup):
    text = ""
    blockquotes = soup.find_all('blockquote')
    for blockquote in blockquotes:
        text += blockquote.get_text() + "\n"
        break
    print("blockquites:")
    print(text)
    print("X"*40)
    post_text_divs = soup.find_all('div', class_='post-text')
    last_image=None
    for post_text_div in post_text_divs:
        for p in post_text_div.find_all("p"):
            text += p.get_text() + "\n"
        for a in post_text_div.find_all("a", class_='lightbox'):
            for img in a.find_all("img", class_='img-fluid'):
                last_image=img
    if last_image is not None:
        last_image=img['src']
        if last_image.startswith("/"):
            last_image="https://www.bourse24.ir"+last_image

    dateti = soup.find_all("i", class_="fa-calendar")[0].parent
    date = dateti.get_text().split()
    hourmin = date[4].split(":")
    months = "فروردین اردیبهشت خرداد تیر مرداد شهریور مهر آبان آذر دی بهمن اسفند".split()
    persian_date = jdatetime.datetime(int(date[2]), months.index(date[1]) + 1, int(date[0]), int(hourmin[0]),
                                      int(hourmin[1]))

    # Convert to Gregorian date
    gregorian_date = persian_date.togregorian()
    new_row = {"date": gregorian_date,
               "persian_date": str(persian_date),
               "text": text,
               "img":last_image}
    return new_row


def get_links(key, max_page=5):
    all_links = []
    url = f'https://www.bourse24.ir/news/tag/{key}'
    for i in range(1, max_page):
        # Send a GET request to the website
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML content of the page with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            page_links = get_news_in_page(soup)
            all_links += page_links
            for link in page_links:
                print(link)
            print("X" * 40)
            time.sleep(0.01)
            try:
                url = get_next_page_url(soup, i + 1)
            except:
                break

        else:
            print(f"Failed to retrieve the page. Status code: {response.status_code}")
    return all_links


def is_exist_tag(key):
    url = f'https://www.bourse24.ir/news/tag/{key}'
    response = requests.get(url)
    return response.url != "https://www.bourse24.ir/news"


if __name__ == '__main__':
    with open('data\stock_names.json', 'r', encoding='utf-8') as json_file:
        stock_names = json.load(json_file)

    for group in reversed(list(stock_names.keys())):
        for key in reversed(stock_names[group]):
            key=convert_arabic_to_persian(key)
            if isfile(f"ndata/all_news_{key}.json"):
                all_news = pd.read_json(f"ndata/all_news_{key}.json")
                continue
            if is_exist_tag(key):
                all_news = pd.DataFrame(columns=['text', 'persian_date', 'date', 'key', 'url', 'img', 'img_text'])
                print("crawl ", key)

                all_links = get_links(key, max_page=10)

                for link_id, link in enumerate(all_links):
                    if link not in all_news['url'].values:
                        response = requests.get(link)

                        # Check if the request was successful
                        if response.status_code == 200:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            news = parse_news(soup)
                            news['key'] = key
                            news['url'] = link
                            news['img_text'] = ""
                            all_news = all_news.append(news, ignore_index=True)
                            all_news.to_json(f"ndata/all_news_{key}.json", orient="records", force_ascii=False)
                            print(news['text'])
                            print(news['img'])
                            print("*" * 50)
                            # print(news)
                        time.sleep(0.1)
            else:
                print("DELETE", key)
                if isfile(f"ndata/all_news_{key}.json"):
                    os.remove(f"ndata/all_news_{key}.json")
                    print("really DELETE", key)
                    time.sleep(0.1)
                # if link_id==4:
                #     break
            # print(all_links)

            #
