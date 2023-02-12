# THIS IS THE ACCOUNT DATA BASE
import hashlib
import os
from requests import post


# database management for sign up
def signup(filename, email, pwd, confirm_pwd, first_name, api_openai):
    file = open(filename, "a")
    file = open(filename, "r")

    # The email already exist!
    for line in file:
        if email in line.split(", "):
            return 1

    # password and confirm password don't match
    if pwd != confirm_pwd:
        return 2

    # invalid API
    if isAPIvalid(api_openai) == 0:
        return 3

    # You have registered successfully!
    enc = confirm_pwd.encode()
    hash1 = hashlib.md5(enc).hexdigest()
    file = open(filename, "a")
    file.write(f"{email}, {hash1}, {first_name}, {api_openai}\n")
    file.close()
    return 4


def isAPIvalid(api_openai):
    response = post("https://api.openai.com/v1/engines/text-davinci-003/jobs",
                    json={
                        "prompt": "Can I eat cats?",
                        "temperature": 0.5
                    },
                    headers={
                        "Authorization": f"Bearer {api_openai}"
                    })

    if response.status_code == 401:
        return 0
    elif response.status_code == 403:
        return 1
    else:
        return 0


# database management for login
def login(filename, email, pwd):
    file = open(filename, "a")
    file = open(filename, "r")

    # if file is not empty
    if os.path.getsize(filename) > 0:
        # encoding the password 
        auth = pwd.encode()
        auth_hash = hashlib.md5(auth).hexdigest()

        # making a dictionary of email as key and password as value
        data = {}
        for line in file:
            em, pw, fn, api = line.split(", ")
            data[em] = pw.strip()

        # check if email is in the list of emails
        if email in data.keys():
            # login successful
            if auth_hash == data[email]:
                return 3
            # incorrect email or password
            else:
                return 2

    # if file is empty then account does not exist
    file.close()
    return 1

def getAPI(filename):
    file = open(filename, "a")
    file = open(filename, "r")
    api = ''
    for line in file:
        em, pw, fn, api = line.split(", ")
    return api.strip()
