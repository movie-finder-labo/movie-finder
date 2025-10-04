from dotenv import dotenv_values
from moviefinder.mongodb import MovieFinderDB
import pymongo
import asyncio

async def main():
    try:
        dbConfig = dotenv_values()
        db = MovieFinderDB(uri=dbConfig["MONGO_URI"], databaseName=dbConfig["MONGO_DATABASE"])
        await db.Connect()
    except pymongo.errors.ServerSelectionTimeoutError as err:
        print(f"Failed to connect: {err}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")
    except:
        print("An unknown error has occured when connecting to the mongodb database.")
    
    print(await db.DeleteUser("lol"))
    print(await db.GetUserByUsername("lol"))
    try:
        id = await db.CreateUser("lol", "bad password")
        print(id)
        print(await db.GetUserById(id))
    except Exception as ex:
        print(f"User lol already exists: {ex}")
    print(await db.GetUsers())
    print(await db.DeleteUser("lol"))

if __name__ == "__main__":
    asyncio.run(main())