from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from bson.objectid import ObjectId
from datetime import datetime, timezone
from os import getenv
import threading
import bcrypt

# As simple as possible for this project. A shorthand for bcrypt.hashpw so you don't have to import bcrypt outside this module.
def PWHash(pw: bytes, s: bytes) -> bytes:
    """ Hashing & salting function. Pass the bytes encoded from the raw string (e.g `<string pw>.encode()`) and the salt associated with the password generated using `bcrypt.gensalt()`"""
    return bcrypt.hashpw(pw, s)

class User(object):
    """ User wrapper object """
    def __init__(self, id: ObjectId, pwh: bytes, salt: bytes, username: str, age: int, genres: list[str], created: datetime):
        if not ObjectId.is_valid(id): raise ValueError("BAD ID")
        self.id: ObjectId = id
        self.pwh: bytes = pwh
        self.salt: bytes = salt
        self.username: str = username
        self.age: int = age
        self.genres: list[str] = genres
        self.created: datetime = created
    
    @staticmethod
    def fromDict(dict: dict | None):
        if dict is None: return None
        """ Creates a user object from a dictionary. All the arguments for __init__ is expected to exists as keys by the same names in the dictionary."""
        return User(dict.get("_id", None), dict.get("pwh", None), dict.get("salt", None), dict.get("username", "bad_username"), dict.get("age", -1), dict.get("genres", []), dict.get("created", datetime.now(timezone.utc)))
    
    def __str__(self):
        return f"User \"{self.username}\" [{str(self.id)}]"
    
    def __repr__(self):
        self.__str__()

class DuplicateUsername(Exception):
    pass

class MovieFinderDB(object):
    """ A thread-safe singleton class wrapping a single `AsyncMongoClient` instance. Call constructor to get an existing instance or initialize it if it doesn't yet exist. Currently supports the following collections:
    
    - `Users`
    """
    _instance = None
    _lock = threading.Lock()
    client: AsyncMongoClient = None
    db: AsyncDatabase = None
    users: AsyncCollection = None
    
    # Create a new static instance or just return the already existing one
    def __new__(self, uri: str | None=None, databaseName: str | None=None):
        # First check outside the lock for performance
        if self._instance is not None:
            return self._instance
        with self._lock:
            # Second check inside the lock to see if another thread may have already created an instance
            if self._instance is not None:
                return self._instance
            self._instance = super(MovieFinderDB, self).__new__(self)
            if not uri: uri = getenv("MONGO_URI")
            if not databaseName: databaseName = getenv("MONGO_DATABASE")
            self._instance.client = AsyncMongoClient(host=uri)
            self._instance.db = self._instance.client[databaseName]
            self._instance.users = self._instance.db["users"]
            return self._instance
        
    def __str__(self):
        return f"MovieFinderDB [{self.db.name}]"
   
    async def Connect(self) -> None:
        """ Try the connection to the mongodb database. Not necessary, but can be used for initial error handling. """
        await self.client.aconnect()

    async def GetUsers(self) -> dict[ObjectId, User]:
        """ Gets all the documents from the `users` collection and reads them into a dictionary """
        users = dict()
        async with self.users.find() as cursor:
            async for user in cursor:
                users[ObjectId(user.get("_id"))] = User.fromDict(user)
        return users
    
    async def GetUserBy(self, attr: str, needle: any) -> User | None:
        """ Get user by a given attribute and a corresponding needle """
        return User.fromDict(await self.users.find_one({attr: needle}))
    
    async def GetUserByUsername(self, username: str) -> User | None:
        """ Tries to get a user by it's username """
        return await self.GetUserBy("username", username)

    async def GetUserById(self, id: ObjectId) -> User | None:
        return await self.GetUserBy("_id", id)

    async def CreateUser(self, username: str, password: str, age: int, genres: list[str]) -> User:
        """ Creates and inserts a new user into the users collection. Make sure to wrap in a `try` clause, as this function can raise exceptions if:
        
        - A user by the given username already exists
        """
        if await self.GetUserByUsername(username) is not None: raise DuplicateUsername("user already exists")
        createdDate = datetime.now(timezone.utc)
        salt = bcrypt.gensalt()
        pwh = PWHash(password.encode(), salt)
        result = await self.users.insert_one({"username": username, "pwh": pwh, "salt": salt, "created": createdDate, "age": age, "genres": genres})
        return await self.GetUserById(result.inserted_id)
    
    async def DeleteUser(self, username: str) -> bool:
        """ Deletes a user by the given username. """
        result = await self.users.delete_one({"username": username})
        return bool(result.deleted_count)

    async def DeleteAllUsers(self):
        result = await self.users.drop()
        return result