import pytest
from backend.libs.database.mongodb import MovieFinderDB


@pytest.fixture 
async def db(): 
    database = MovieFinderDB("localhost:27017", "Test_MovieFinder") 
    await database.DeleteAllUsers() 
    yield database 

async def test_CreateUser(db):
    await db.CreateUser("user123@email.com", "1234") 
    user = await db.GetUserByEmail("user123@email.com") 
    assert user['username'] == "user123@email.com" 
    assert user['pwh'] == "1234" 

async def test_add_same_user(db): 
    await db.CreateUser("user123@email.com", "1234") 
    with pytest.raises(Exception, match="user already exists"): 
        await db.CreateUser("user123@email.com", "1234") 
    

async def test_DeleteUser(db): 
    await db.CreateUser("user123@email.com", "1234")

    assert await db.DeleteUser("user123@email.com") is True 
    assert await db.GetUserByEmail("user123@email.com") is None 

async def test_GetUserBy(db): 
    await db.CreateUser("user123@email.com", "1234") 
    user = await db.GetUserByEmail("user123@email.com") 
    user_by_username = await db.GetUserBy("username", "user123@email.com") 
    user_by_password = await db.GetUserBy("pwh", "1234") 
    
    assert user_by_username["username"] == user["username"] 
    assert user_by_password["pwh"] == user["pwh"] 

async def test_GetUsers(db): 
    await db.CreateUser("user1@email.com", "1234") 
    await db.CreateUser("user12@email.com", "1234") 
    await db.CreateUser("user123@email.com", "1234") 
    
    result = await db.GetUsers() 
    user1 = await db.GetUserByEmail("user1@email.com") 
    user12 = await db.GetUserByEmail("user12@email.com") 
    user123 = await db.GetUserByEmail("user123@email.com") 
    
    assert len(result) == 3 
    assert result[user1["_id"]] == user1 
    assert result[user12["_id"]] == user12 
    assert result[user123["_id"]] == user123