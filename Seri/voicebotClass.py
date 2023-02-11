import random
import json
import pickle
import numpy as np
import speech_recognition
import pyttsx3 as tts
import sys
import time
import requests
import openai
import os

import nltk
from nltk.stem import WordNetLemmatizer

from keras.models import load_model

# lemmatizer instantiation
lemmatizer = WordNetLemmatizer()

# loading the dataset
intents = json.loads(open('./Seri/intents.json').read())

# storing the data into its variable
words = pickle.load(open('./Seri/words.pkl', 'rb'))
classes = pickle.load(open('./Seri/classes.pkl', 'rb'))
model = load_model('./Seri/Seri_model.h5')


# for speaker and microphone
# instantiation of the speech recognition
recognizer = speech_recognition.Recognizer()

# instantiation of text to speech
speaker = tts.init()

# initialization of the voice and speed of voice
voices = speaker.getProperty('voices')
speaker.setProperty('voice', voices[1].id)
speaker.setProperty('rate', 150)


todo_list = [""]


# lemmatizing the sentence
class VoiceBot():
    def __init__(self):
        # dictionary for tag and corresponding responses
        self.mappings = {
            "greetings": self.hello,
            "create_note": self.create_note,
            "add_todo": self.add_todo,
            "show_todos": self.show_todos,
            "goodbye": self.quit,
            "name": self.response,
            "thanks": self.response,
            "programmer": self.response,
            "okay": self.response,
            "compliment": self.response,
            "age": self.response,
            "regards": self.response,
            "date": self.date_today,
            "time": self.current_time,
            "weather": self.weather_today,
            "clever": self.response,
            "bad": self.response,
            "bot_bad": self.response,
            "busy": self.response,
            "help": self.response,
            "laugh": self.response,
            "appreciation": self.response
        }

    def clean_up_sentence(self, sentence):
        sentence_words = nltk.word_tokenize(sentence)
        sentence_words = [lemmatizer.lemmatize(word) for word in sentence_words]
        # returns list of words in a sentence
        return sentence_words

    # checking if the word is in the bag of words using 0's and 1's
    def bag_of_words(self, sentence):
        sentence_words = self.clean_up_sentence(sentence)
        bag = [0] * len(words)
        for w in sentence_words:
            for i, word in enumerate(words):
                if word == w:
                    bag[i] = 1
        return np.array(bag)

    # probability of the class
    def predict_class(self, sentence):
        bow = self.bag_of_words(sentence)
        res = model.predict(np.array([bow]))[0]
        ERROR_THRESHOLD = 0.25
        # storing [index, class]
        results = [[i, r] for i, r in enumerate(res) if r > ERROR_THRESHOLD]

        # sorting the probability in reverse order: highest probability first
        results.sort(key=lambda x: x[1], reverse=True)
        self.return_list = []
        for r in results:
            self.return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
        return self.return_list

    # getting response from the data
    def get_response(self, intent_list, intent_json):
        self.result = ''
        tag = intent_list[0]['intent']
        list_of_intents = intent_json['intents']

        for i in list_of_intents:
            if i['tag'] == tag:
                self.result = random.choice(i['responses'])
                break
        return self.result

    # function to speak
    def speak(self,audio):
        speaker.say(audio)
        speaker.runAndWait()

    # function to get the user's query
    def user_says(self):
        global recognizer
        query = ''
        with speech_recognition.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration=0.2)

            # storing the speech to the audio variable
            audio = recognizer.listen(mic)

        try:
            # extract text from the audio
            query = recognizer.recognize_google(audio, language='en-in')
            query.lower()

        except speech_recognition.UnknownValueError:
            recognizer = speech_recognition.Recognizer()
            self.speak("I did not understand you. Please try again!")

        # returns string transcription
        return query

    # returns date today
    def date_today(self):
        day = time.strftime("%A")
        date = time.strftime("%B %d %Y")
        result = f"Today is {day}, {date}"
        self.speak(result)

    # returns the time right now
    def current_time(self):
        time_today = time.strftime("%I: %M %p")
        result = f"It is {time_today}."
        self.speak(result)

    # returns the weather today
    def weather_today(self):
        global recognizer
        api_key = '987f44e8c16780be8c85e25a409ed07b'
        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        self.speak("What is your city?")
        city = ''

        try:
            # getting the user's audio
            city = self.user_says().capitalize()
            self.speak(f"Okay, one second.")
            complete_url = base_url + "appid=" + api_key + "&q=" + city
            d = requests.get(complete_url)
            data = d.json()
            result = f"The temperature today in {city} is {round(data['main']['temp'] - 273, 2)} celcius.\n" \
                     f"The weather description is {data['weather'][0]['description']}."
            self.speak(result)

        except speech_recognition.UnknownValueError:
            recognizer = speech_recognition.Recognizer()
            self.speak("I did not understand you. Please try again!")

        except KeyError:
            self.speak(f"{city} is not a city nor a province! Please try again.")

    # create a txt file
    def create_note(self):
        global recognizer

        self.speak("What do you want to write onto your note?")

        done = False

        while not done:
            try:
                note = self.user_says()
                self.speak("Choose a filename!")
                filename = self.user_says()

                # write in txt file
                with open(f"{filename}.txt", 'w') as f:
                    f.write(note)
                    done = True
                    self.speak(f"I successfully created the note {filename}")

            except speech_recognition.UnknownValueError:
                recognizer = speech_recognition.Recognizer()
                self.speak("I did not understand you. Please try again!")

    # add item/s to the list
    def add_todo(self):
        global recognizer
        self.speak("What to do do you want to add?")

        done = False

        while not done:
            try:
                item = self.user_says()
                todo_list.append(item)
                done = True
                self.speak(f"I added {item} to the to do list!")

            except speech_recognition.UnknownValueError:
                recognizer = speech_recognition.Recognizer()
                self.speak("I did not understand you. Please try again!")

    # showing to do list
    def show_todos(self):
        speaker.say("The items on your to do list are the following")
        for item in todo_list:
            speaker.say(item)
        speaker.runAndWait()

    def hello(self):
        self.speak("Hello, what can I do for you?")

    # exiting the program
    def quit(self):
        self.speak("Good bye! Have a nice day.")
        sys.exit(0)

    # speaking the response from the datasets
    def response(self):
        global message
        ints = self.predict_class(message)
        res = self.get_response(ints, intents)
        self.speak(res)





