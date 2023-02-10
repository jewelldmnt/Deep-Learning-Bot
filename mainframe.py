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
from chatbot.voicebotClass import Chatbot
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

todo_list = ["Coding"]


with open("./chatbot/API.txt", "r") as file:
    # API for openAI
    API_openai = file.read()
    os.environ['OPENAI_Key'] = API_openai
    openai.api_key = os.environ['OPENAI_Key']
    file.close()

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
        #screen_manager.add_widget(Builder.load_file("./ChatScreen/Chat.kv"))
        screen_manager.add_widget(Builder.load_file("./CallScreen/Call.kv"))
        #screen_manager.add_widget(Builder.load_file("./HomepageScreen/Homepage.kv"))
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

            screen_manager.get_screen('chat').chat_list.add_widget(ChatCommand(text=input, size_hint_x=size, halign=halign))
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











if __name__ == '__main__':
    Bot().run()
