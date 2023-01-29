import random
import json
import pickle
import numpy as np
import requests
import time

import nltk
from nltk.stem import WordNetLemmatizer

from keras.models import load_model

# lemmatizer instantiation
lemmatizer = WordNetLemmatizer()

# storing the json file as a dictionary
intents = json.loads(open('intents.json').read())

# storing the data into its variable
words = pickle.load(open('words.pkl', 'rb'))
classes = pickle.load(open('classes.pkl', 'rb'))
model = load_model('chatbot_model.h5')

# lemmatizing the sentence
def clean_up_sentence(sentence):
    sentence_words = nltk.word_tokenize(sentence)
    sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
    # returns list of words in a sentence
    return sentence_words

# checking if the word is in the bag of words using 0's and 1's
def bag_of_words(sentence):
    sentence_words = clean_up_sentence(sentence)
    bag = [0] * len(words)
    for w in sentence_words:
        for i, word in enumerate(words):
            if word == w:
                bag[i] = 1
    return np.array(bag)

# probability of the class
def predict_class(sentence):
    bow = bag_of_words(sentence)
    res = model.predict(np.array([bow]))[0]
    ERROR_THRESHOLD = 0.25
    # storing [index, class]
    results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

    # sorting the probability in reverse order: highest probability first
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
    return return_list

# getting response from the data
def get_response(intent_list, intent_json):
    result = ''
    tag = intent_list[0]['intent']
    list_of_intents = intent_json['intents']

    for i in list_of_intents:
        if tag == 'weather':
            api_key = '987f44e8c16780be8c85e25a409ed07b'
            base_url = "http://api.openweathermap.org/data/2.5/weather?"
            city_name = input("What is your city?\n").lower().capitalize()
            complete_url = base_url + "appid=" + api_key + "&q=" + city_name
            response = requests.get(complete_url)
            x = response.json()
            result = f"The temperature today in {city_name} city is {round(x['main']['temp'] - 273, 2)} celcius.\n" \
                     f"The weather description is {x['weather'][0]['description']}."
            break

        elif tag == 'date':
            day = time.strftime("%A")
            date = time.strftime("%B %d %Y")
            result = f"Today is {day}, {date}"
            break

        elif tag == 'time':
            time_today = time.strftime("%I: %M %p")
            result = f"It is {time_today}."
            break

        elif i['tag'] == tag:
            result = random.choice(i['responses'])
            break
    return result

print("Talk now")

while True:
    message = input()
    ints = predict_class(message)
    res = get_response(ints, intents)
    print(res)