import json
import re
import sys

import requests
import time
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient


def get_response(url):
    start_time = time.time()
    while True:
        response = requests.get(url, headers=headers, verify=False)
        if response.status_code == 200:
            return response
        time.sleep(3)

        if start_time + 30 < time.time():  # Ожидание ответа от сайта более 30 сек -> выходим
            return None


headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
}
file_name = 'digest_records_from_2021-7-16_6-17-58_UTC.json'
client = MongoClient('localhost')
db = client['ml_base']
ml_collection = db.ml_collection

with open(file_name, 'r') as file:
    file = json.load(file)

    for itm in file:
        if ml_collection.count_documents({'pk': itm['pk']}) == 0:
            if itm['fields']['url'][-4:] == '.pdf':  # Если ссылка на pdf (6 ссылок)
                itm['fields']['article_content'] = 'pdf'
                itm['fields']['download_status'] = 'failed'
                ml_collection.insert_one(itm)
                continue
            elif ('dts.podtrac.com' in itm['fields']['url'] or
                  'cdn.simplecast.com' in itm['fields']['url'] or
                  itm['fields']['url'][-4:] == '.mp3'
            ):  # Если аудиозапись
                itm['fields']['article_content'] = 'audio'
                itm['fields']['download_status'] = 'failed'
                ml_collection.insert_one(itm)
                continue
            elif itm['fields']['url'][-4:] == '.mp4':  # Если видеозапись (14 ссылок)
                itm['fields']['article_content'] = 'video'
                itm['fields']['download_status'] = 'failed'
                ml_collection.insert_one(itm)
                continue

            while True:  # Зацикливаю из-за ошибки ConnectionError, повторное подключение через 15 сек.
                try:
                    response = get_response(itm['fields']['url'])
                    break
                except requests.exceptions.ConnectionError:
                    print("Connection refused by the server. Let me sleep for 15 seconds.", file=sys.stderr)
                    time.sleep(15)
                    print("Was a nice sleep, now let me continue...")
                    continue

            if not response:  # Если сайт отдает 404
                itm['fields']['article_content'] = '404'
                itm['fields']['download_status'] = 'failed'
                ml_collection.insert_one(itm)
                continue

            soup = bs(response.text, 'lxml')
            article_soup = soup.find('article')
            article_content = ''

            if not article_soup:  # если не нашли тег article
                article_soup = soup
                itm['fields']['download_status'] = 'not_article'
            else:  # если нашли тег article
                itm['fields']['download_status'] = 'article'

            for paragraph in article_soup.find_all("p"):
                article_content = article_content + paragraph.get_text()

            itm['fields']['article_content'] = article_content
            ml_collection.insert_one(itm)

        # address = re.findall(r'\/{2}([^\/]*)\/', itm['fields']['url'])
        # address_set.add('.'.join(address[0].split('.')[-2:])) if address else address_set.add('None')

# 14278 не хватает в url https://istio.io/
# сильно плохо если verify=False
