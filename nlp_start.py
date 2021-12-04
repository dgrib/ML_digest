import spacy


# nlp = spacy.load('en_core_web_sm')
# doc = nlp(u'I am flying to Frisco')
# print([w.text for w in doc])

# import spacy
# nlp = spacy.load('en_core_web_sm')
# doc = nlp(u'this product integrates both libraries for downloading and applying patches')
# for token in doc:
#     print(token.text, token.lemma_)

import spacy
nlp = spacy.load('ru_core_news_sm')
doc = nlp(u'I have flown to LA. Now I am flying to Frisco.')
print([w.text for w in doc if w.tag_ == 'VBG' or w.tag_ == 'VB'])
print([w.text for w in doc if w.pos_ == 'PROPN'])
for token in doc:
 print(token.head.text, token.dep_, token.text)