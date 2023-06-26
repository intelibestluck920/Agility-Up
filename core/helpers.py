from statistics import mean
from datetime import date

import numpy as np



def sprint_name_convention(name):
    name, number = name.split(' ', 1)
    number = int(number)
    number += 1
    number = str(number)
    return name + " " + number


def sentence_splitter(text):
    from nltk import tokenize

    arr = tokenize.sent_tokenize(text)

    return arr


def sentiment_analysis(text):
    # Imports the Google Cloud client library
    from google.cloud import language_v1

    # Instantiates a client
    client = language_v1.LanguageServiceClient()

    # The text to analyze
    # text = "Hello, world!"
    document = language_v1.Document(
        content=text, type_=language_v1.Document.Type.PLAIN_TEXT
    )

    # Detects the sentiment of the text
    sentiment = client.analyze_sentiment(
        request={"document": document}
    ).document_sentiment

    # print("Text: {}".format(text))
    # print("Sentiment: {}, {}".format(sentiment.score, sentiment.magnitude))

    return sentiment.score


def capitalize(sentence):
    return str.title(sentence)


def tag_return(score):
    if score < -0.25:
        return 'Negative'
    elif score > 0.25:
        return 'Positive'
    elif 0.25 > score > -0.25:
        return 'Neutral'


def average(list):
    avg = []
    for l in list:
        avg.append(l['score'])

    average = mean(avg)
    average = round(average, 1)
    if average > 0:
        arrow = 'up'
    elif average < 0:
        arrow = 'down'
    elif average == 0:
        arrow = 'stable'

    dict = {
        'score': average,
        'arrow': arrow,
        'created_at': date.today().strftime("%b %d %Y")
    }
    return dict

