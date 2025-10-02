from flask import Flask
from moviefinder.database.mongo import MovieFinderDB
import pymongo

app = Flask("TEST")
try:
    global db
    db = MovieFinderDB(app)
except pymongo.errors.ServerSelectionTimeoutError as err:
    print(f"Failed to connect: {err}")
except Exception as ex:
    print(f"Unexpected error: {ex}")
    
print(db.GetUserByUsername("") is None)