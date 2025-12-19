import pytest
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(ROOT_DIR))

from libs.database.mongodb import MovieFinderDB, User
from libs.database.csv import InitializeMovieData


HOST = "localhost:27017"
DB_NAME = "Test_MovieFinder"

TEST_AGE = 20
TEST_GENRES = ["Action", "Drama"]

CSV_PATH = "data"

@pytest.fixture
def db():
    database = MovieFinderDB(HOST, DB_NAME)
    database.DeleteAllUsers()
    yield database


@pytest.fixture
def movieData():
    return InitializeMovieData(CSV_PATH)


# TESTS

def test_singleton(db):
    db2 = MovieFinderDB(HOST, DB_NAME)
    assert db2 is db


def test_CreateUser(db):
    db.CreateUser("user123@email.com", "1234", TEST_AGE, TEST_GENRES)

    user = db.GetUserByUsername("user123@email.com")

    assert user.username == "user123@email.com"
    assert user.pwh != "1234"                 
    assert isinstance(user.pwh, (bytes, bytearray))
    assert user.age == TEST_AGE
    assert user.genres == TEST_GENRES

def test_add_same_user(db):
    db.CreateUser("user123@email.com", "1234", TEST_AGE, TEST_GENRES)

    with pytest.raises(Exception, match="user already exists"):
        db.CreateUser("user123@email.com", "1234", TEST_AGE, TEST_GENRES)


def test_DeleteUser(db):
    db.CreateUser("user123@email.com", "1234", TEST_AGE, TEST_GENRES)

    assert db.DeleteUser("user123@email.com") is True
    assert db.GetUserByUsername("user123@email.com") is None


def test_GetUserBy(db):
    db.CreateUser("user123@email.com", "1234", TEST_AGE, TEST_GENRES)

    user_by_username = db.GetUserBy("username", "user123@email.com")
    user_by_age = db.GetUserBy("age", TEST_AGE)

    assert user_by_username.username == "user123@email.com"
    assert user_by_age.age == TEST_AGE


def test_GetUsers(db):
    db.CreateUser("user1@email.com", "1234", TEST_AGE, TEST_GENRES)
    db.CreateUser("user2@email.com", "1234", TEST_AGE, TEST_GENRES)
    db.CreateUser("user3@email.com", "1234", TEST_AGE, TEST_GENRES)

    users = db.GetUsers()
    assert len(users) == 3
