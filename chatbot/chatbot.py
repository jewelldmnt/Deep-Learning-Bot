import random
import json
import pickle
import sys

import numpy as np
import requests
import time
import nltk
from nltk.stem import WordNetLemmatizer
from keras.models import load_model
import openai
import os

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
        if tag == 'date':
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

isAPIvalid = False
while not isAPIvalid:
    try:
        # check if user has an API
        with open("API.txt", "r") as file:
            # API for openAI
            API_openai = file.read()
            os.environ['OPENAI_Key'] = API_openai
            openai.api_key = os.environ['OPENAI_Key']
            file.close()
        testing = openai.Completion.create(engine='text-davinci-003', prompt="is it working", max_tokens=200)
        isAPIvalid = True

    except openai.error.AuthenticationError:
        with open("API.txt", "r") as file:
            content = file.read()

        # no API
        if not content:
            print("\nYou have no API. Please copy your API key at https://platform.openai.com/account/api-keys.")
            API_openai_copied = input("Paste your API here: ")
            with open("API.txt", "w") as file:
                # Write some content to the file
                file.write(API_openai_copied)
                file.close()
        else:
            print("\nInvalid API. Please copy your API key at https://platform.openai.com/account/api-keys.")
            API_openai_copied = input("Paste your API here: ")
            with open("API.txt", "w") as file:
                # Write some content to the file
                file.write(API_openai_copied)
                file.close()


print("Chat now")

while True:
    message = input()
    ints = predict_class(message)
    if ints[0]["intent"] == "goodbye":
        res = get_response(ints, intents)
        print(res)
        sys.exit(0)

    # getting the highest intent probability
    probability = float(ints[0]['probability'])

    # comparing the probability to its threshold error
    # if below uncertainty, get the response from openAI
    if probability < 0.98:
        res = openai.Completion.create(engine='text-davinci-003', prompt=message, max_tokens=200)
        print(res['choices'][0]['text'])
    # if above uncertainty, get the response from the intents.json dataset
    else:
        res = get_response(ints, intents)
        print(res)