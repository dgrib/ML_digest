import spacy
import json
from pymongo import MongoClient


file_name = 'keywords.json'
client = MongoClient('localhost')
db = client['ml_base']
ml_collection = db.ml_collection
nlp = spacy.load('en_core_web_md')

keyword_set = set()
keyword_extended_set = dict()

with open(file_name, 'r') as file:
    file = json.load(file)

    for itm in file:
        keyword_set.add(itm['fields']['name'].lower())
        # keyword_extended_set[itm['fields']['name'].lower()] = itm['fields']['category'].lower() if
    print(1)




for record in ml_collection.find():
    article_content = record['fields']['article_content']
    doc = nlp(article_content.lower())

    possible_tags_set_pos = set()  # проверяет существительные и собств.существ. в ключевых словах
    for token in doc:
        if token.pos_ == 'PROPN' or token.pos_ == 'NOUN':
            if token.text in keyword_set:
                possible_tags_set_pos.add(token.text)

    possible_tags_set_ml = set()  # проверяем леммы в ключевых словах
    for token in doc:
        if token.text in keyword_set:
            possible_tags_set_ml.add(token.text)

    possible_tags_set_text = set()  # прооверяет ключевое слово в тексте статьи
    for keyword in keyword_set:
        if keyword.lower() in article_content.lower():
            possible_tags_set_text.add(keyword)


    print(1)


# doc = nlp(u'I have flown to LA. Now I am flying to Frisco.')
# for token in doc:
#     if token.ent_type != 0:
#         print(token.text, token.ent_type_, token.lemma_)