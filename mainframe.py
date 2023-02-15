# modules and libraries for GUI
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.uix.screenmanager import ScreenManager
from kivymd.uix.label import MDLabel
from kivy.properties import StringProperty, NumericProperty
from PIL import ImageFont


# modules and libraries for the bot
from speech_recognition import UnknownValueError
from Seri.chatbotClass import Chatbot
from Seri.voicebotClass import VoiceBot
from json import load
import openai
import os
import account
import sys

# Set the window size of the screen
Window.size = (400, 560)

# Load the dataset
with open('Seri/intents.json') as file:
    intents = load(file)

# Create a new instance of VoiceBot
vb = VoiceBot()

# Initialize an empty message string
message = ''


# class for the user's message in chat screen
class ChatCommand(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "./ChatScreen/assets/Kanit-Light.ttf"
    font_size = 15


# class for the bot's response in chat screen
class ChatResponse(MDLabel):
    text = StringProperty()
    size_hint_x = NumericProperty()
    halign = StringProperty()
    font_name = "./ChatScreen/assets/Kanit-Light.ttf"
    font_size = 15


class Bot(MDApp):
    # define screens
    chat_screen = screen_manager.get_screen('chat')
    call_screen = screen_manager.get_screen('call')
    start_screen = screen_manager.get_screen('startpage')
    home_screen = screen_manager.get_screen('home')
    signin_screen = screen_manager.get_screen('signin')
    signup_screen = screen_manager.get_screen('signup')

    # for changing the current screen
    def change_screen(self, name):
        screen_manager.current = name

    # for building the screens
    def build(self):
        global screen_manager
        screen_manager = ScreenManager()
        screen_manager.add_widget(Builder.load_file("./StartpageScreen/Startpage.kv"))
        screen_manager.add_widget(Builder.load_file("./HomepageScreen/Homepage.kv"))
        screen_manager.add_widget(Builder.load_file("./AboutScreen/About.kv"))
        screen_manager.add_widget(Builder.load_file("./GetAPIScreen/GetAPI.kv"))
        screen_manager.add_widget(Builder.load_file("./SigninScreen/Signin.kv"))
        screen_manager.add_widget(Builder.load_file("./SignupScreen/Signup.kv"))
        screen_manager.add_widget(Builder.load_file("./ChatScreen/Chat.kv"))
        screen_manager.add_widget(Builder.load_file("./CallScreen/Call.kv"))
        return screen_manager

    # sending the user's chat message
    def sendChat(self):
        # Define constants and get the user input
        global size, halign, user_message
        text_input = self.chat_screen.text_input.text
        user_message = text_input.strip()

        # Check if the user input is not empty
        if text_input != "":
            # Calculate the input box width based on the user input and font
            font = ImageFont.truetype("./ChatScreen/assets/Kanit-Light.ttf", 15)
            bbox = font.getbbox(user_message)
            input_box_width = ((bbox[2] - bbox[0]) + 40) / 400

            # Determine the size and horizontal alignment of the user's message
            max_input_width = 0.782
            size = max_input_width if input_box_width >= max_input_width else input_box_width
            halign = 'left' if input_box_width >= max_input_width else 'center'

            # Add the user's message to the chat list and schedule the chatbot's response
            self.chat_screen.chat_list.add_widget(ChatCommand(text=user_message, size_hint_x=size, halign=halign))
            Clock.schedule_once(self.responseChat, 2)
            self.chat_screen.text_input.text = ''

    # getting the bot's chat response
    def responseChat(self, *args):
        # API for openAI
        API_openai = account.getAPI("credentials.txt")
        os.environ['OPENAI_Key'] = API_openai
        openai.api_key = os.environ['OPENAI_Key']
        cb = Chatbot()

        # get the predicted intent and probability
        ints = cb.predict_class(user_message)
        probability = float(ints[0]['probability'])

        # check if probability is less than 0.99, get response from OpenAI
        if probability < 0.99:
            res = openai.Completion.create(engine='text-davinci-003', prompt=user_message, max_tokens=200)
            res = res['choices'][0]['text']

        else:
            # get response from intents.json dataset
            res = cb.get_response(ints, intents)

        # clean the response
        res = res.strip()
        lines = res.split("\n")
        line_count = len(lines)
        max_len = max(len(line.strip()) for line in lines)
        max_res = ''

        # get the longest line in the response
        for line in lines:
            if len(line) == max_len:
                max_res = line
                break

        # calculate the size and alignment of the response text
        font = ImageFont.truetype("./ChatScreen/assets/Kanit-Light.ttf", 15)
        bbox = font.getbbox(max_res)
        res_box_width = ((bbox[2] - bbox[0]) + 40) / 400

        # Determine the size and horizontal alignment of the user's message
        max_input_width = 0.782
        size = max_input_width if res_box_width >= max_input_width else res_box_width
        halign = 'left' if res_box_width >= max_input_width else 'center'

        # Add the bot's message to the chat list
        self.chat_screen.chat_list.add_widget(ChatResponse(text=res, size_hint_x=size, halign=halign))

    # function to get the call response
    def responseCall(self):
        # API for OpenAI
        API_openai = account.getAPI("credentials.txt")
        os.environ['OPENAI_Key'] = API_openai
        openai.api_key = os.environ['OPENAI_Key']

        self.call_screen.image_speaking.opacity = 1
        self.call_screen.button_speak.disabled = True

        # get the predicted intent and probability
        ints = vb.predict_class(message)
        probability = float(ints[0]['probability'])

        # check if probability is less than 0.99, get response from OpenAI
        if probability < 0.99:
            res = openai.Completion.create(engine='text-davinci-003', prompt=message, max_tokens=200)
            vb.speak(res['choices'][0]['text'])

        # if above uncertainty, get the response from the intents.json dataset
        else:
            if ints[0]['intent'] in vb.mappings.keys():
                vb.mappings[ints[0]['intent']]()

        self.call_screen.button_speak.disabled = False
        self.call_screen.image_speaking.opacity = 0
        self.call_screen.image_listening.opacity = 1

    # function to speak
    def say_something(self):
        global message
        print("You may speak")
        try:
            message = vb.user_says()
            print(message)

        except UnknownValueError:
            vb.speak("I did not understand you. Please try again!")

        self.chat_screen.image_listening.opacity = 0

    def checkInput(self):
        # get all necessary inputs
        api_openai = self.signup_screen.api_oai.text
        first_name = self.signup_screen.first_name.text
        email = self.signup_screen.email.text
        password = self.signup_screen.password.text
        confirm_password = self.signup_screen.confirm_password.text

        # check if all inputs are not empty
        if all([first_name, api_openai, email, password, confirm_password]):
            self.sign_up(api_openai, first_name, email, password, confirm_password)

    #  to sign up
    def sign_up(self, api_openai, first_name, email, password, confirm_password):
        filename = "credentials.txt"
        # Get the sign-up status using the account.signup() function and store it in a variable
        sign_up_status = account.signup(filename, email, password, confirm_password, first_name, api_openai)

        # Check the status and update the UI accordingly
        if sign_up_status == 4:
            # Clear all the input fields and move to the homepage screen
            self.signup_screen.first_name.text = ""
            self.signup_screen.email.text = ""
            self.signup_screen.password.text = ""
            self.signup_screen.confirm_password.text = ""
            self.signup_screen.api_oai.text = ""
            screen_manager.transition.direction = "left"
            screen_manager.current = "homepage"

        elif sign_up_status == 1:
            # Display error message for email already exists
            self.signup_screen.email.required = True
            self.signup_screen.email.helper_text = "Email already exists!"
            self.signup_screen.email.text = ""

        elif sign_up_status == 2:
            # Display error message for passwords don't match
            self.signup_screen.password.required = True
            self.signup_screen.confirm_password.required = True
            self.signup_screen.confirm_password.helper_text = "The Passwords don't match!"
            self.signup_screen.password.text = ""
            self.signup_screen.confirm_password.text = ""

        elif sign_up_status == 3:
            # Display error message for invalid API
            self.signup_screen.api_oai.required = True
            self.signup_screen.api_oai.helper_text = "Invalid API"
            self.signup_screen.api_oai.text = ""

    # to sign in
    def sign_in(self):
        filename = "credentials.txt"
        email = self.signin_screen.email.text
        password = self.signin_screen.password.text

        # Get the sign-in status using the account.signin() function and store it in a variable
        login_status = account.login(filename, email, password)

        if email and password and login_status == 3:
            self.signin_screen.email.text = ""
            self.signin_screen.password.text = ""
            screen_manager.transition.direction = "left"
            screen_manager.current = "homepage"

        # account does not exist
        elif login_status == 1:
            self.signin_screen.email.required = True
            self.signin_screen.email.helper_text = "Account does not exist!"
            self.signin_screen.email.text = ""

        # incorrect password
        elif login_status == 2:
            self.signin_screen.password.required = True
            self.signin_screen.password.helper_text = "Incorrect Password!"
            self.signin_screen.password.text = ""

    def exit(self):
        sys.exit(0)

    def back(self, screen, direction):
        screen_manager.transition.direction = direction
        screen_manager.current = screen
        Bot().stop()
        Bot().run()


if __name__ == '__main__':
    Bot().run()
