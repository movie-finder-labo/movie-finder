from pymongo import MongoClient, UpdateOne
from pymongo.database import Database
from pymongo.collection import Collection
from bson.objectid import ObjectId
from datetime import datetime, timezone
from .csv import InitializeMovieData
from os import getenv
import threading
import bcrypt

# As simple as possible for this project. A shorthand for bcrypt.hashpw so you don't have to import bcrypt outside this module.
def PWHash(pw: bytes, s: bytes) -> bytes:
    """ Hashing & salting function. Pass the bytes encoded from the raw string (e.g `<string pw>.encode()`) and the salt associated with the password generated using `bcrypt.gensalt()`"""
    return bcrypt.hashpw(pw, s)

class User(object):
    """ User wrapper object """
    def __init__(self, id: ObjectId, pwh: bytes, salt: bytes, username: str, age: int, genres: list[str], ratings: dict[str, int], created: datetime):
        if not ObjectId.is_valid(id): raise ValueError("BAD ID")
        self.id: ObjectId = id
        self.pwh: bytes = pwh
        self.salt: bytes = salt
        self.username: str = username
        self.age: int = age
        self.genres: list[str] = genres
        self.ratings: dict[str, int] = ratings
        self.created: datetime = created
    
    @staticmethod
    def fromDict(dict: dict | None):
        """ Creates a user object from a dictionary. All the arguments for __init__ is expected to exists as keys by the same names in the dictionary."""
        if dict is None: return None
        return User(dict.get("_id", None), dict.get("pwh", None), dict.get("salt", None), dict.get("username", "bad_username"), dict.get("age", -1), dict.get("genres", []), dict.get("ratings", {}), dict.get("created", datetime.now(timezone.utc)))
    
    def RateMovie(self, movieId, rating: int) -> bool:
        rating = max(0, min(rating, 5))
        if not InitializeMovieData().get(movieId): raise LookupError("Movie not found")
        db = MovieFinderDB()
        try:
            success = db.UpdateUserMovieRating(self.username, movieId, rating)
        except Exception as err:
            print(f"Failed to rate movie for user {self.username}: {err}")
            return False
        self.ratings.append((movieId, rating))
        return success
        
    def Querify(self) -> str:
        """ Produces a query string usable for an AI prompt. Takes `ratings`, `genres` and `age` into account """
        return f"As of now I only have these preferences: {self.QuerifyGenres()}, {self.QuerifyRatings()} and the user's age which is {self.age or 'N/A'}. Ignore anything that is \"N/A\""
        
    def QuerifyGenres(self) -> str:
        """ Formats all genres into an AI prompt query """
        return "the following genres, if any: \"" + ",".join(self.genres) + "\""

    def QuerifyRatings(self) -> str:
        """ Formats all ratings into an AI prompt query """
        movies = InitializeMovieData()
        ratings = []
        for r in self.ratings:
            movie = movies.get(r.get('movieId'))
            if not movie: continue
            ratings.append(f"{movie.get('title', 'N/A')} ({movie.get('year', 'N/A')}) [{r.get('rating', 'N/A')}/5]")
        return "the following movie ratings (<title> (<year>) [<rating>/5]), if any: \"" + ",".join(ratings) + "\""
    
    def __str__(self):
        return f"User \"{self.username}\" [{str(self.id)}]"
    
    def __repr__(self):
        return self.__str__()

class DuplicateUsernameError(Exception):
    pass

class MovieFinderDB(object):
    """ A thread-safe singleton class wrapping a single `MongoClient` instance. Call constructor to get an existing instance or initialize it if it doesn't yet exist. Currently supports the following collections:
    
    - `Users`
    """
    _instance = None
    _lock = threading.Lock()
    client: MongoClient = None
    db: Database = None
    users: Collection = None
    
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
            self._instance.client = MongoClient(host=uri)
            self._instance.db = self._instance.client[databaseName]
            self._instance.users = self._instance.db["users"]
            return self._instance
        
    def __str__(self):
        return f"MovieFinderDB [{self.db.name}]"
   
    def Connect(self) -> None:
        """ Try the connection to the mongodb database. Not necessary, but can be used for initial error handling. """
        self.client.aconnect()

    def GetUsers(self) -> dict[ObjectId, User]:
        """ Gets all the documents from the `users` collection and reads them into a dictionary """
        users = dict()
        with self.users.find() as cursor:
            for user in cursor:
                users[ObjectId(user.get("_id"))] = User.fromDict(user)
        return users
    
    def GetUserBy(self, attr: str, needle: any) -> User | None:
        """ Get user by a given attribute and a corresponding needle """
        return User.fromDict(self.users.find_one({attr: needle}))
    
    def GetUserByUsername(self, username: str) -> User | None:
        """ Tries to get a user by it's username """
        return self.GetUserBy("username", username)

    def GetUserById(self, id: ObjectId) -> User | None:
        """ Tries to get a user by it's object ID """
        return self.GetUserBy("_id", id)

    def UpdateUserMovieRating(self, username: str, movieId: str, rating: int) -> bool:
        """ Updates or inserts a user rating """
        update = UpdateOne(
            filter={"username": username, "ratings.movieId": movieId},
            update={"$set": {"ratings.$[elem].rating": rating}},
            array_filters=[{"elem.movieId": movieId}],
        )
        insert = UpdateOne(
            filter={"username": username, "ratings.movieId": {"$ne": movieId}},
            update={"$push": {"ratings": {"movieId": movieId, "rating": rating}}},
        )
        # Tries to update any existing rating first, pushes new rating otherwise
        result = self.users.bulk_write([update, insert])
        return bool(result.modified_count)

    def CreateUser(self, username: str, password: str, age: int, genres: list[str]) -> User:
        """ Creates and inserts a new user into the users collection. Make sure to wrap in a `try` clause, as this function can raise exceptions if:
        
        - A user by the given username already exists
        """
        if self.GetUserByUsername(username) is not None: raise DuplicateUsernameError("user already exists")
        createdDate = datetime.now(timezone.utc)
        salt = bcrypt.gensalt()
        pwh = PWHash(password.encode(), salt)
        result = self.users.insert_one({"username": username, "pwh": pwh, "salt": salt, "created": createdDate, "age": age, "genres": genres, "ratings": []})
        return self.GetUserById(result.inserted_id)
    
    def DeleteUser(self, username: str) -> bool:
        """ Deletes a user by the given username. """
        result = self.users.delete_one({"username": username})
        return bool(result.deleted_count)

    def DeleteAllUsers(self):
        result = self.users.drop()
        return result