# THIS IS THE ACCOUNT DATA BASE
import hashlib
import os
from requests import post


# database management for sign up
def signup(filename, email, pwd, confirm_pwd, first_name, api_openai):
    # The email already exists
    with open(filename, "r") as file:
        if any(email in line for line in file):
            return 1

    # Password and confirm password don't match
    if pwd != confirm_pwd:
        return 2

    # Invalid API
    if not isAPIvalid(api_openai):
        return 3

    # encode the password
    hash1 = hashlib.md5(confirm_pwd.encode()).hexdigest()

    # You have registered successfully!
    with open(filename, "a") as file:
        file.write(f"{email}, {hash1}, {first_name}, {api_openai}\n")
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

    if response.status_code == 403:
        return 1    # valid api
    else:
        return 0    # invalid api


# database management for login
def login(filename, email, pwd):
    # Open file for reading
    with open(filename, "r") as file:
        # Check if file is not empty
        if os.path.getsize(filename) > 0:
            # Encode the password
            auth_hash = hashlib.md5(pwd.encode()).hexdigest()

            # Create a dictionary of email as key and password as value
            data = {line.split(", ")[0]: line.split(", ")[1].strip() for line in file}

            # Check if email is in the list of emails
            if email in data:
                # Login successful
                if auth_hash == data[email]:
                    return 3
                # Incorrect password
                else:
                    return 2
            # account does not exist
            else:
                return 1
        # If file is empty then account does not exist
        else:
            return 1

def getAPI(filename, email, password):
    with open(filename, "r") as file:
        contents = file.read()
        lines = contents.splitlines()
        api_openai = ''

        # Loop through each line and split it by comma
        for line in lines:
            fields = line.split(",")

            # Check if "api" is one of the fields
            if email in fields and password in fields:
                # Get the value of "api" and print it
                api_openai = fields[3]
                break  # stop processing lines once "api" is found

        if isAPIvalid(api_openai) == 1:
            return api_openai
        else:
            return 0