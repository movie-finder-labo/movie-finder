from dotenv import dotenv_values
from moviefinder.database.mongo import MovieFinderDB
import pymongo
import asyncio

dbConfig = dotenv_values()

async def Test():
    try:
        db = MovieFinderDB(connectionString=dbConfig["MONGO_URI"], databaseName=dbConfig["MONGO_DATABASE"])
        await db.Connect()
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(f"Failed to connect: {err}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        
    print(await db.GetUserByUsername("lol"))

asyncio.run(Test())