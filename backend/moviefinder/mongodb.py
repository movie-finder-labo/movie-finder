from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from bson.objectid import ObjectId

class MovieFinderDB(object):
    """ MongoDB based Database wrapper for MovieFinder """
    def __init__(self, uri: str, databaseName: str) -> None:
        """ Creates a new mongodb connection. Contains functionality for the following collections:
        
        - Users
        """
        self.client: AsyncMongoClient = AsyncMongoClient(host=uri)
        self.db: AsyncDatabase = self.client[databaseName]
        self.users: AsyncCollection = self.db["users"]
    
    async def Connect(self) -> None:
        """ Try the connection to the mongodb database. Not necessary, but can be used for initial error handling. """
        await self.client.aconnect()

    async def GetUsers(self) -> dict[ObjectId, any]:
        """ Gets all the documents from the `users` collection and reads them into a dictionary """
        users = dict()
        async with self.users.find() as cursor:
            async for user in cursor:
                users.update(user)
        
        return users
        
    # TODO: Replace return type from `any` to user class
    async def GetUserByUsername(self, username: str) -> any:
        """ Tries to get a user by it's username """
        return await self.users.find_one({"username": username})

    # TODO: Replace return type from `any` to user class
    async def GetUserByPWH(self, pwh: str) -> any:
        """ Tries to get a user by it's password hash """
        return await self.users.find_one({"pwh": pwh})

    # TODO: Maybe integrate the password hashing algorithim with this function
    # TODO: Replace return type from `any` to user class
    async def CreateUser(self, username: str, pwh: str) -> ObjectId:
        """ Creates and inserts a new user into the users collection. Make sure to wrap in a `try` clause, as this function can raise exceptions if:
        
        - A user by the given username already exists
        """
        if await self.GetUserByUsername(username): raise Exception("User already exists")
        result = await self.users.insert_one({"username": username, "pwh": pwh})
        return result.inserted_id
    
    async def DeleteUser(self, username: str) -> bool:
        """ Deletes a user by the given username. """
        result = await self.users.delete_one({"username": username})
        return bool(result.deleted_count)