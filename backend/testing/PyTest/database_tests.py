import pytest
# Import parent directory so we can access libs package
import sys
from pathlib import Path

libdir = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(libdir))

from libs.database.mongodb import MovieFinderDB, User
from libs.database.csv import InitializeMovieData

host = "localhost:27017"
dbName =  "Test_MovieFinder"
csvPath = "data" # Relative to the "../backend/testing" folder

@pytest.fixture
def db():
    database = MovieFinderDB(host, dbName)
    database.DeleteAllUsers()
    movieData = InitializeMovieData(csvPath)
    yield database, movieData

def test_singleton(db):
    db2 = MovieFinderDB(host, dbName)
    assert db2 is db

def test_CreateUser(db):
    db.CreateUser("user123@email.com", "1234")
    user = db.GetUserByUsername("user123@email.com")

    assert user['username'] == "user123@email.com"
    assert user['pwh'] == "1234"

def test_RateMovie(db, movieData):
    value = 2
    user: User = db.CreateUser("user123@email.com", "1234")
    movie = movieData[0]
    user.RateMovie(movie.movieId, value)
    
    assert user.ratings.get(movie.movieId) is value

def test_add_same_user(db):
    db.CreateUser("user123@email.com", "1234")

    with pytest.raises(Exception, match="user already exists"):
        db.CreateUser("user123@email.com", "1234")

def test_DeleteUser(db):
    db.CreateUser("user123@email.com", "1234")

    assert db.DeleteUser("user123@email.com") is True
    assert db.GetUserByUsername("user123@email.com") is None

def test_GetUserBy(db):
    db.CreateUser("user123@email.com", "1234")
    user = db.GetUserByUsername("user123@email.com")

    user_by_username = db.GetUserBy("username", "user123@email.com")
    user_by_password = db.GetUserBy("pwh", "1234")

    assert user_by_username["username"] == user["username"]
    assert user_by_password["pwh"] == user["pwh"]

def test_GetUsers(db):
    db.CreateUser("user1@email.com", "1234")
    db.CreateUser("user12@email.com", "1234")
    db.CreateUser("user123@email.com", "1234")

    result = db.GetUsers()

    user1 = db.GetUserByUsername("user1@email.com")
    user12 = db.GetUserByUsername("user12@email.com")
    user123 = db.GetUserByUsername("user123@email.com")

    assert len(result) == 3
    assert result[user1["_id"]] == user1
    assert result[user12["_id"]] == user12
    assert result[user123["_id"]] == user123