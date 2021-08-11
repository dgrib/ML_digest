import json
import re
import requests
import time
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient


def get_response(url):
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        time.sleep(0.5)


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
}

file_name = 'digest_records_from_2021-7-16_6-17-58_UTC.json'

address_set = set()
without_article_tag_count = 0

client = MongoClient('localhost')
db = client['ml_base']
ml_collection = db.ml_collection

with open(file_name, 'r') as file:
    file = json.load(file)

    for itm in file:
        if ml_collection.count_documents({'pk': itm['pk']}) == 0:
            response = get_response(itm['fields']['url'])
            soup = bs(response.text, 'lxml')
            article_soup = soup.find('article')

            article_content = ''
            if article_soup:
                for paragraph in article_soup.find_all("p"):
                    article_content = article_content + paragraph.get_text()
            else:
                article_content = 'No article tag'

            itm['fields']['article_content'] = article_content

            ml_collection.insert_one(itm)
        else:
            continue

        # address = re.findall(r'\/{2}([^\/]*)\/', itm['fields']['url'])
        # address_set.add('.'.join(address[0].split('.')[-2:])) if address else address_set.add('None')
