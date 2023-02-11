from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty, NumericProperty
from kivy.core.text import LabelBase

# module and libraries for the bot
from chatbot.chatbotClass import Chatbot
from chatbot.voicebotClass import VoiceBot
import openai
import json
import os
from neuralintents import GenericAssistant
import speech_recognition
import pyttsx3 as tts
import sys
import time
import requests

Window.size = (400, 560)
intents = json.loads(open('./chatbot/intents.json').read())

# instantiation of the speech recognition
recognizer = speech_recognition.Recognizer()

# instantiation of text to speech
speaker = tts.init()

# initialization of the voice and speed of voice
voices = speaker.getProperty('voices')
speaker.setProperty('voice', voices[1].id)
speaker.setProperty('rate', 150)

todo_list = []

message = ''

with open("./chatbot/API.txt", "r") as file:
    # API for openAI
    API_openai = file.read()
    os.environ['OPENAI_Key'] = API_openai
    openai.api_key = os.environ['OPENAI_Key']
    file.close()


def speak(audio):
    speaker.say(audio)
    speaker.runAndWait()


# function to get the user's query
def user_says():
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
        speak("I did not understand you. Please try again!")

    # returns string transcription
    return query


# returns date today
def date_today():
    day = time.strftime("%A")
    date = time.strftime("%B %d %Y")
    result = f"Today is {day}, {date}"
    speak(result)


# returns the time right now
def current_time():
    time_today = time.strftime("%I: %M %p")
    result = f"It is {time_today}."
    speak(result)


# returns the weather today
def weather_today():
    global recognizer
    api_key = '987f44e8c16780be8c85e25a409ed07b'
    base_url = "http://api.openweathermap.org/data/2.5/weather?"
    speak("What is your city?")
    city = ''

    try:
        # getting the user's audio
        city = user_says().capitalize()
        speak(f"Okay, one second.")
        complete_url = base_url + "appid=" + api_key + "&q=" + city
        d = requests.get(complete_url)
        data = d.json()
        result = f"The temperature today in {city} is {round(data['main']['temp'] - 273, 2)} celcius.\n" \
                 f"The weather description is {data['weather'][0]['description']}."
        speak(result)

    except speech_recognition.UnknownValueError:
        recognizer = speech_recognition.Recognizer()
        speak("I did not understand you. Please try again!")

    except KeyError:
        speak(f"{city} is not a city nor a province! Please try again.")


# create a txt file
def create_note():
    global recognizer

    speak("What do you want to write onto your note?")

    done = False

    while not done:
        try:
            note = user_says()
            speak("Choose a filename!")
            filename = user_says()

            # write in txt file
            with open(f"{filename}.txt", 'w') as f:
                f.write(note)
                done = True
                speak(f"I successfully created the note {filename}")

        except speech_recognition.UnknownValueError:
            recognizer = speech_recognition.Recognizer()
            speak("I did not understand you. Please try again!")


# add item/s to the list
def add_todo():
    global recognizer
    speak("What to do do you want to add?")

    done = False

    while not done:
        try:
            item = user_says()
            todo_list.append(item)
            done = True
            speak(f"I added {item} to the to do list!")

        except speech_recognition.UnknownValueError:
            recognizer = speech_recognition.Recognizer()
            speak("I did not understand you. Please try again!")


# showing to do list
def show_todos():
    speaker.say("The items on your to do list are the following")
    for item in todo_list:
        speaker.say(item)
    speaker.runAndWait()


def hello():
    speak("Hello, what can I do for you?")


# exiting the program
def quit():
    speak("Good bye! Have a nice day.")
    sys.exit(0)


# speaking the response from the datasets
def response():
    global message
    vb = VoiceBot()
    ints = vb.predict_class(message)
    res = vb.get_response(ints, intents)
    speak(res)


# dictionary for tag and corresponding responses
mappings = {
    "greetings": hello,
    "create_note": create_note,
    "add_todo": add_todo,
    "show_todos": show_todos,
    "goodbye": quit,
    "name": response,
    "thanks": response,
    "programmer": response,
    "okay": response,
    "compliment": response,
    "age": response,
    "regards": response,
    "date": date_today,
    "time": current_time,
    "weather": weather_today,
    "clever": response,
    "bad": response,
    "bot_bad": response,
    "busy": response,
    "help": response,
    "laugh": response,
    "appreciation": response
}

# training the model
assistant = GenericAssistant('./chatbot/intents.json', intent_methods=mappings)
assistant.train_model()


class ChatCommand(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "./ChatScreen/assets/Kanit-Light.ttf"
    font_size = 15


class ChatResponse(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "./ChatScreen/assets/Kanit-Light.ttf"
    font_size = 15


class Bot(MDApp):
    def change_screen(self, name):
        screen_manager.current = name

    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        # screen_manager.add_widget(Builder.load_file("./ChatScreen/Chat.kv"))
        screen_manager.add_widget(Builder.load_file("./CallScreen/Call.kv"))
        # screen_manager.add_widget(Builder.load_file("./HomepageScreen/Homepage.kv"))
        return screen_manager

    def sendChat(self):
        global size, halign, input
        if screen_manager.get_screen('chat').text_input != "":
            input = screen_manager.get_screen('chat').text_input.text
            if len(input) < 6:
                size = .22
                halign = "center"
            elif len(input) < 11:
                size = .32
                halign = "center"
            elif len(input) < 16:
                size = .45
                halign = "center"
            elif len(input) < 21:
                size = .58
                halign = "center"
            elif len(input) < 26:
                size = .71
                halign = "center"
            else:
                size = .77
                halign = "left"

            screen_manager.get_screen('chat').chat_list.add_widget(
                ChatCommand(text=input, size_hint_x=size, halign=halign))
            Clock.schedule_once(self.responseChat, 2)
            screen_manager.get_screen('chat').text_input.text = ""

    def responseChat(self, *args):
        cb = Chatbot()
        ints = cb.predict_class(input)

        # getting the highest intent probability
        probability = float(ints[0]['probability'])

        # comparing the probability to its threshold error
        # if below uncertainty, get the response from openAI
        if probability < 0.98:
            res = openai.Completion.create(engine='text-davinci-003', prompt=input, max_tokens=200)
            res = res['choices'][0]['text']
        # if above uncertainty, get the response from the intents.json dataset
        else:
            res = cb.get_response(ints, intents)

        screen_manager.get_screen('chat').chat_list.add_widget(ChatResponse(text=res, size_hint_x=0.75))

    # function to speak
    def say_something(self):
        global message
        try:
            vb = VoiceBot()
            print("You may speak")
            message = user_says()
            screen_manager.get_screen('call').button_speak.disabled = True
            print(message)
            # predicting the intent of the message
            ints = vb.predict_class(message)

            # getting the highest intent probability
            probability = float(ints[0]['probability'])

            # comparing the probability to its threshold error
            # if below uncertainty, get the response from openAI
            if probability < 0.98:
                res = openai.Completion.create(engine='text-davinci-003', prompt=message, max_tokens=200)
                speak(res['choices'][0]['text'])

            # if above uncertainty, get the response from the intents.json dataset
            else:
                assistant.request(message)
            screen_manager.get_screen('call').button_speak.disabled = False

        except speech_recognition.UnknownValueError:
            recognizer = speech_recognition.Recognizer()
            screen_manager.get_screen('call').button_speak.disabled = True
            speak("I did not understand you. Please try again!")
            screen_manager.get_screen('call').button_speak.disabled = False


if __name__ == '__main__':
    Bot().run()
