import pickle
import numpy as np
from newspaper import Article
import nltk
nltk.download('punkt')

import os
import re
import string

here = os.path.dirname(os.path.abspath(__file__))

vector_form = pickle.load(open(os.path.join(here, 'model/vector.pkl'), 'rb'))
load_model = pickle.load(open(os.path.join(here, 'model/model.pkl'), 'rb'))

def wordopt(text):
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub("\\W"," ",text)
    text = re.sub('https?://\S+|www\.\S+', '', text)
    text = re.sub('<.*?>+', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\n', '', text)
    text = re.sub('\w*\d\w*', '', text)
    return text

def determine_bias(content):
    content = wordopt(content)
    input_data = [content]
    vector_form1 = vector_form.transform(input_data)
    prediction = load_model.predict(vector_form1)
    if prediction[0] == "right":
        return 0
    elif prediction[0] == "left":
        return 2
    else:
        return 1

def handle_incoming_url(url):
    # find the following information from the url:
    # url, title, favicon, top_img, date, summary, ai_rating, user_rating
    # ai_rating is the prediction from the model
    res_map = {}

    article = Article(url)
    try:
        article.download()
        article.parse()
        article.nlp()

        # print the type of the article
        print(type(url))
        print(type(article.summary))
        print(type(article.meta_favicon))
        print(type(article.top_image))
        print(type(article.publish_date))
        print(type(article.summary))

        res_map['url'] = url
        res_map['title'] = article.title
        res_map['favicon'] = article.meta_favicon
        res_map['top_img'] = article.top_image
        res_map['date'] = article.publish_date
        res_map['summary'] = article.summary
        res_map['ai_rating'] = determine_bias(article.text)
        # user_rating will start as None
        res_map['user_rating'] = None
        return res_map

    except:
        print("Error: article not downloaded")
        return None
