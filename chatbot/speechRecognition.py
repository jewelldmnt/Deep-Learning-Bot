from neuralintents import GenericAssistant
import speech_recognition
import pyttsx3 as tts
import sys
import time
import requests
import json
from chatbotClass import Chatbot

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

    done = False

    while not done:
        try:
            with speech_recognition.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic, duration=0.2)

                # storing the speech to the audio variable
                audio = recognizer.listen(mic)

                # extract text from the audio
                city = recognizer.recognize_google(audio)
                city = city.lower().capitalize()

                done = True

                speak(f"Okay, one second.")

        except speech_recognition.UnknownValueError:
            recognizer = speech_recognition.Recognizer()
            speak("I did not understand you. Please try again!")

    complete_url = base_url + "appid=" + api_key + "&q=" + city
    response = requests.get(complete_url)
    x = response.json()
    result = f"The temperature today in {city} is {round(x['main']['temp'] - 273, 2)} celcius.\n" \
             f"The weather description is {x['weather'][0]['description']}."
    speak(result)

# create a txt file
def create_note():
    global recognizer

    speak("What do you want to write onto your note?")

    done = False

    while not done:
        try:
            with speech_recognition.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic, duration=0.2)

                # storing the speech to the audio variable
                audio = recognizer.listen(mic)

                # extract text from the audio
                note = recognizer.recognize_google(audio)
                note = note.lower()

                speak("Choose a filename!")

                recognizer.adjust_for_ambient_noise(mic, duration=0.2)

                # storing the speech to the audio variable
                audio = recognizer.listen(mic)

                # extract the text from the audio
                filename = recognizer.recognize_google(audio)
                filename = filename.lower()

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
            with speech_recognition.Microphone() as mic:
                recognizer.adjust_for_ambient_noise(mic, duration=0.2)

                # storing the speech to the audio variable
                audio = recognizer.listen(mic)

                # extract text from the audio
                item = recognizer.recognize_google(audio)
                item = item.lower()

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
    cb = Chatbot()
    ints = cb.predict_class(message)
    res = cb.get_response(ints, intents)
    speak(res)


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

assistant = GenericAssistant('intents.json', intent_methods=mappings)
assistant.train_model()

while True:
    try:
        with speech_recognition.Microphone() as mic:
            recognizer.adjust_for_ambient_noise(mic, duration=0.2)

            # storing the speech to the audio variable
            audio = recognizer.listen(mic)

            message = recognizer.recognize_google(audio)
            message = message.lower()

        assistant.request(message)

    except speech_recognition.UnknownValueError:
        recognizer = speech_recognition.Recognizer()
        speak("I did not understand you. Please try again!")
