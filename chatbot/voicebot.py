from neuralintents import GenericAssistant
import speech_recognition
import pyttsx3 as tts
import sys
import time
import requests
import json
from voicebotClass import Chatbot
import openai
import os


# instantiation of the speech recognition
recognizer = speech_recognition.Recognizer()

# instantiation of text to speech
speaker = tts.init()

# initialization of the voice and speed of voice
voices = speaker.getProperty('voices')
speaker.setProperty('voice', voices[1].id)
speaker.setProperty('rate', 150)

# loading the dataset
intents = json.loads(open('intents.json').read())
cb = Chatbot()

todo_list = ["Coding"]


# function to speak
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
    ints = cb.predict_class(message)
    res = cb.get_response(ints, intents)
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
assistant = GenericAssistant('intents.json', intent_methods=mappings)
assistant.train_model()

# checking the validity of the user's openAI API
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
            speak("You have no API. See the link below to copy your API key.")
            print("\nPlease copy your API key at: https://platform.openai.com/account/api-keys.")
            API_openai_copied = input("Paste your API here: ")
            with open("API.txt", "w") as file:
                # Write some content to the file
                file.write(API_openai_copied)
                file.close()
        else:
            speak("Invalid API. See the link below to copy your API key.")
            print("\nPlease copy your API key at https://platform.openai.com/account/api-keys.")
            API_openai_copied = input("Paste your API here: ")
            with open("API.txt", "w") as file:
                # Write some content to the file
                file.write(API_openai_copied)
                file.close()

print("IMIK NA ANTEH KUNG AYAW MONG MABARIL")
speak("imik na anteh kung ayaw mong mabaril")

while True:
    try:
        message = user_says()
        print(message)
        # predicting the intent of the message
        ints = cb.predict_class(message)

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

    except speech_recognition.UnknownValueError:
        recognizer = speech_recognition.Recognizer()
        speak("I did not understand you. Please try again!")
