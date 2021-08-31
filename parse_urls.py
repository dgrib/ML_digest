import json
import requests
import time
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient
import logging


def get_response(url):
    start_time = time.time()
    while True:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response
        elif response.status_code >= 400:
            print(1)
            return None
        time.sleep(3)
        logging.debug(f"{itm['pk']}___sleeping 3 sec")

        if start_time + 30 < time.time():  # Ожидание ответа от сайта более 30 сек -> выходим
            logging.debug(f"{itm['pk']}___more than 30 sec waiting")
            return None


logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} {levelname:<8} {message}",
    style='{',
    filename='error.log',
    filemode='a'
)
headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36'
}
file_name = 'digest_records_from_2021-7-16_6-17-58_UTC.json'
client = MongoClient('localhost')
db = client['ml_base']
ml_collection = db.ml_collection_20210827

with open(file_name, 'r') as file:
    file = json.load(file)

    for itm in file:
        itm['fields']['processed'] = False
        itm['fields']['processed_tags'] = []
        if ml_collection.count_documents({'pk': itm['pk']}) == 0:
            if itm['fields']['url'][-4:] == '.pdf':  # Если ссылка на pdf (6 ссылок)
                itm['fields']['article_content'] = None
                itm['fields']['content_type'] = 'pdf'
                itm['fields']['download_status'] = 'failed'
                ml_collection.insert_one(itm)
                logging.debug(f"{itm['pk']}___PDF - ARTICLE WASN'T ADDED")
                continue
            elif ('dts.podtrac.com' in itm['fields']['url'] or
                  'cdn.simplecast.com' in itm['fields']['url'] or
                  itm['fields']['url'][-4:] == '.mp3'
            ):  # Если аудиозапись
                itm['fields']['article_content'] = None
                itm['fields']['content_type'] = 'audio'
                itm['fields']['download_status'] = 'failed'
                ml_collection.insert_one(itm)
                logging.debug(f"{itm['pk']}___AUDIO - ARTICLE WASN'T ADDED")
                continue
            elif itm['fields']['url'][-4:] == '.mp4':  # Если видеозапись (14 ссылок)
                itm['fields']['article_content'] = None
                itm['fields']['content_type'] = 'video'
                itm['fields']['download_status'] = 'failed'
                ml_collection.insert_one(itm)
                logging.debug(f"{itm['pk']}___VIDEO - ARTICLE WASN'T ADDED")
                continue

            tries = 5
            while tries:  # Зацикливаю из-за ошибки ConnectionError, повторное подключение через 15 сек. 5 попыток
                try:
                    response = get_response(itm['fields']['url'])
                    break
                except requests.exceptions.ConnectionError as err:
                    logging.debug(f"{itm['pk']}___ERROR {err}")
                    time.sleep(15)
                    tries -= 1
                    continue
            else:
                response = None


            if not response:  # Если сайт отдает 404 или ConnectionError
                itm['fields']['article_content'] = None
                itm['fields']['content_type'] = '404 or ConnectionError'
                itm['fields']['download_status'] = 'failed'
                ml_collection.insert_one(itm)
                logging.debug(f"{itm['pk']}___404 - ARTICLE WASN'T ADDED")
                continue

            soup = bs(response.text, 'lxml')
            article_soup = soup.find('article')
            article_content = ''

            if not article_soup:  # если не нашли тег article
                article_soup = soup
                itm['fields']['content_type'] = 'not_article_tag'
            else:  # если нашли тег article
                itm['fields']['content_type'] = 'article_tag'

            itm['fields']['download_status'] = 'success'
            for paragraph in article_soup.find_all("p"):
                article_content = article_content + paragraph.get_text()

            itm['fields']['article_content'] = article_content
            ml_collection.insert_one(itm)
            logging.info(f"{itm['pk']}___ADDED INTO DB")
