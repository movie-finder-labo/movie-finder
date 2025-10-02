from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection

class MovieFinderDB(object):
    """ Database wrapper for MoveFinder """
    def __init__(self, connectionString: str, databaseName: str) -> None:
        """ Creates a new mongodb connection. Creates wrappers for the following collections: User """
        self.client: AsyncMongoClient = AsyncMongoClient(host=connectionString)
        self.db: AsyncDatabase = self.client[databaseName]
        self.users: AsyncCollection = self.db["users"]
    
    async def Connect(self) -> None:
        await self.client.aconnect()

    async def GetUserByUsername(self, username: str) -> dict | None:
        """ Tries to get a user by it's username """
        return await self.users.find_one({username: username})

    async def GetUserByPWH(self, pwh: str) -> dict | None:
        """ Tries to get a user by it's password hash """
        return await self.users.find_one({pwh: pwh})

    # TODO: Maybe integrate the password hashing part with this function
    async def CreateUser(self, username: str, pwh: str) -> dict:
        """ Creates and inserts a new user into the users collection. Make sure to wrap in a `try` clause, as this function can raise exceptions if:
        
        - A user by the given username already exists
        
        """
        if await self.GetUserByUsername(self, username) is not None: raise Exception("User already exists")
        await self.collection.insert_one({username: username, pwh: pwh})