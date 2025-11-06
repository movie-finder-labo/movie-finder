import pytest
import bcrypt

from bson import ObjectId
from backend.libs.database.mongodb import MovieFinderDB

@pytest.fixture
async def db():
    database = MovieFinderDB("localhost:27017", "Test_MovieFinder")
    await database.DeleteAllUsers()
    yield database


async def test_CreateUser(db):
    user_id = await db.CreateUser(
        "user123@email.com", "1234", "User 123", 25, ["Action", "Drama"]
    )
    assert isinstance(user_id, ObjectId)

    user = await db.GetUserByEmail("user123@email.com")
    assert user["email"] == "user123@email.com"
    assert "pwh" in user
    assert bcrypt.checkpw("1234".encode("utf-8"), user["pwh"].encode("utf-8"))
    assert user["fullname"] == "User 123"
    assert user["age"] == 25
    assert "created" in user

async def test_add_same_user(db):
    await db.CreateUser("user123@email.com", "1234", "User 123", 25, ["Action"])

    with pytest.raises(Exception, match="user already exists"):
        await db.CreateUser("user123@email.com", "1234", "User 123", 25, ["Action"])


async def test_DeleteUser(db):
    await db.CreateUser("user123@email.com", "1234", "User 123", 25, ["Action"])

    assert await db.DeleteUser("user123@email.com") is True
    assert await db.GetUserByEmail("user123@email.com") is None

async def test_GetUserBy(db):
    await db.CreateUser("user123@email.com", "1234", "User 123", 25, ["Action"])
    user = await db.GetUserByEmail("user123@email.com")

    user_by_email = await db.GetUserBy("email", "user123@email.com")

    assert user_by_email["email"] == user["email"]

async def test_GetUsers(db):
    await db.CreateUser("user1@email.com", "1234", "User 1", 21, ["Action"])
    await db.CreateUser("user2@email.com", "1234", "User 2", 22, ["Drama"])
    await db.CreateUser("user3@email.com", "1234", "User 3", 23, ["Comedy"])

    result = await db.GetUsers()
    assert len(result) == 3
    user1 = await db.GetUserByEmail("user1@email.com")
    user2 = await db.GetUserByEmail("user2@email.com")
    user3 = await db.GetUserByEmail("user3@email.com")

    assert result[user1["_id"]] == user1
    assert result[user2["_id"]] == user2
    assert result[user3["_id"]] == user3

async def test_Connect(db):
    await db.Connect()

async def test_GetUserById(db):
    user_id = await db.CreateUser("user456@email.com", "pw", "User 456", 30, ["Action"])
    user = await db.GetUserById(user_id)
    assert user["email"] == "user456@email.com"

async def test_VerifyUserPassword(db):
    await db.CreateUser("user789@email.com", "my_password", "User 789", 25, ["Comedy"])
    assert await db.VerifyUserPassword("user789@email.com", "my_password") is True
    assert await db.VerifyUserPassword("user789@email.com", "wrong_password") is False
    assert await db.VerifyUserPassword("nonexistent@email.com", "pw") is False

def test_hash_and_verify_password():
    pw = "secret"
    hashed = MovieFinderDB.hash_password(pw)
    assert isinstance(hashed, bytes)
    assert MovieFinderDB.verify_password(hashed, pw) is True
    assert MovieFinderDB.verify_password(hashed, "wrong") is False
