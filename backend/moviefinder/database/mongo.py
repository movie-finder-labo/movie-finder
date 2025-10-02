from dotenv import dotenv_values
from flask import Flask
from flask_pymongo import PyMongo
from pymongo.collection import Collection

dbConfig = dotenv_values()

class MovieFinderDB(object):
    """ Database wrapper for MoveFinder """
    def __init__(self, app: Flask) -> None:
        """ Creates a new mongodb connection. Creates wrappers for the following collections: User """
        app.config["MONGO_URI"] = dbConfig["MONGO_URI"]
        self.app = app
        self.mongo = PyMongo(app)
        self.users = self.mongo.db.get_collection("users")

    def ServerInfo(self):
        """ Shorthand for calling MongoClient.server_info(). Forces the MongoClient to try to connect, use a try clause w/ pymongo.errors.ServerSelectionTimeoutError exception """
        self.mongo.cx.server_info()
    
    def GetUserByUsername(self, username: str) -> dict | None:
        """ Tries to get a user by it's username """
        return self.users.find_one({username: username})

    def GetUserByPWH(self, pwh: str) -> dict | None:
        """ Tries to get a user by it's password hash """
        return self.users.find_one({pwh: pwh})

    # TODO: Maybe integrate the password hashing part with this function
    def CreateUser(self, username: str, pwh: str) -> dict:
        """ Creates and inserts a new user into the users collection. Make sure to wrap in a `try` clause, as this function can raise exceptions if:
        
        - A user by the given username already exists
        
        """
        if self.GetUserByUsername(self, username) is not None: raise Exception("User already exists")
        self.collection.insert_one({username: username, pwh: pwh})