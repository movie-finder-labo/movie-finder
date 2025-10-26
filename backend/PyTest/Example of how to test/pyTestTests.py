import requests

#Tilfælde funktion
def exampleFunction(a, b):
    if a > b:
        return a
    elif a == b:
        return a + b
    else:
        return b


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b

class Database:
    def __init__(self):
        self.data = {}

    def addUser(self, username, email):
        if username in self.data:
            raise ValueError("Username already exists")
        self.data[username] = email
        return True

    def getUser(self, username):
        return self.data.get(username)

    def deleteUser(self, username):
        if username in self.data:
            del self.data[username]

def get_weather(city):
    response = requests.get(f"https://api.weather.com/v1/{city}")
    if response.status_code == 200:
        return response.json()
    else:
        raise ValueError("Could not get weather from API")