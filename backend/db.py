from dotenv import dotenv_values
from flask import Flask
from flask_pymongo import PyMongo

dbConfig = dotenv_values(".env")

def InitializeDatabase(app: Flask):
    app.config["MONGO_URI"] = dbConfig["MONGO_URI"]
    app.db = PyMongo(app)