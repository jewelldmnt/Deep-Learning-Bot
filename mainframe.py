# modules and libraries for GUI
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty, NumericProperty
from kivy.core.text import LabelBase

# modules and libraries for the bot
from Seri.chatbotClass import Chatbot
from Seri.voicebotClass import VoiceBot
import openai
from json import loads
import os
from speech_recognition import UnknownValueError
import account
import sys

# setting the window size of the screen
Window.size = (400, 560)

# loading the dataset
intents = loads(open('Seri/intents.json').read())
vb = VoiceBot()
message = ''


# class for the user's message in chat screen
class ChatCommand(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "./ChatScreen/assets/Kanit-Light.ttf"
    font_size = 15


# class for the bot response in chat screen
class ChatResponse(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "./ChatScreen/assets/Kanit-Light.ttf"
    font_size = 15


class Bot(MDApp):

    # for changing the current screen
    def change_screen(self, name):
        screen_manager.current = name

    # for building the screens
    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("./StartpageScreen/Startpage.kv"))
        screen_manager.add_widget(Builder.load_file("./HomepageScreen/Homepage.kv"))
        screen_manager.add_widget(Builder.load_file("./SigninScreen/Signin.kv"))
        screen_manager.add_widget(Builder.load_file("./SignupScreen/Signup.kv"))
        screen_manager.add_widget(Builder.load_file("./ChatScreen/Chat.kv"))
        screen_manager.add_widget(Builder.load_file("./CallScreen/Call.kv"))
        return screen_manager

    # sending the user's chat message
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

    # getting the bot's chat response
    def responseChat(self, *args):
        # API for openAI
        API_openai = account.getAPI("credentials.txt")
        os.environ['OPENAI_Key'] = API_openai
        openai.api_key = os.environ['OPENAI_Key']
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

    # function to get the call response
    def responseCall(self):
        # API for openAI
        API_openai = account.getAPI("credentials.txt")
        os.environ['OPENAI_Key'] = API_openai
        openai.api_key = os.environ['OPENAI_Key']

        screen_manager.get_screen('call').image_speaking.opacity = 1

        screen_manager.get_screen('call').button_speak.disabled = True
        # predicting the intent of the message
        ints = vb.predict_class(message)

        # getting the highest intent probability
        probability = float(ints[0]['probability'])

        # comparing the probability to its threshold error
        # if below uncertainty, get the response from openAI
        if probability < 0.98:
            res = openai.Completion.create(engine='text-davinci-003', prompt=message, max_tokens=200)
            vb.speak(res['choices'][0]['text'])

        # if above uncertainty, get the response from the intents.json dataset
        else:
            if ints[0]['intent'] in vb.mappings.keys():
                vb.mappings[ints[0]['intent']]()
        screen_manager.get_screen('call').button_speak.disabled = False
        screen_manager.get_screen('call').image_speaking.opacity = 0
        screen_manager.get_screen('call').image_listening.opacity = 1

    # function to speak
    def say_something(self):
        global message
        try:
            print("You may speak")
            message = vb.user_says()
            print(message)

        except UnknownValueError:
            vb.speak("I did not understand you. Please try again!")
        screen_manager.get_screen('call').image_listening.opacity = 0

    def checkInput(self):
        api_openai = screen_manager.get_screen('signup').api_oai.text
        first_name = screen_manager.get_screen('signup').first_name.text
        email = screen_manager.get_screen('signup').email.text
        password = screen_manager.get_screen('signup').password.text
        confirm_password = screen_manager.get_screen('signup').confirm_password.text

        # if all entry are not empty
        if first_name and api_openai and email and password and confirm_password is not "":
            self.sign_up(api_openai, first_name, email, password, confirm_password)

    def sign_up(self, api_openai, first_name, email, password, confirm_password):
        filename = "credentials.txt"

        # logged in successfully
        if account.signup(filename, email, password, confirm_password, first_name, api_openai) == 4:
            screen_manager.transition.direction = "left"
            screen_manager.current = "homepage"

        # email already exist
        elif account.signup(filename, email, password, confirm_password, first_name, api_openai) == 1:
            screen_manager.get_screen('signup').email.text = ""

        # password and confirm password don't match
        elif account.signup(filename, email, password, confirm_password, first_name, api_openai) == 2:
            screen_manager.get_screen('signup').password.text = ""
            screen_manager.get_screen('signup').confirm_password.text = ""

        # invalid API
        elif account.signup(filename, email, password, confirm_password, first_name, api_openai) == 3:
            screen_manager.get_screen('signup').api_oai.text = ""

    def sign_in(self):
        filename = "credentials.txt"
        email = screen_manager.get_screen('signin').email.text
        password = screen_manager.get_screen('signin').password.text

        if email == "":
            print("Email is empty")
        if password == "":
            print("Password is empty")

        # logged in successfully
        if email and password is not "" and account.login(filename, email, password) == 3:
            screen_manager.transition.direction = "left"
            screen_manager.current = "homepage"

        # account does not exist
        elif account.login(filename, email, password) == 1:
            print("account does not exist!")
            screen_manager.get_screen('signin').email.text = ""
            screen_manager.get_screen('signin').password.text = ""

        # account does not exist
        elif account.login(filename, email, password) == 2:
            print("Incorrect password!")
            screen_manager.get_screen('signin').password.text = ""

    def exit(self):
        sys.exit(0)


if __name__ == '__main__':
    Bot().run()
