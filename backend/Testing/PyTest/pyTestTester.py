#Use one PyTest file per file you're testing(e.g main & test_main, api & api_test)
import pytest
from pyTestTests import *

#To run the test you need to be in the correct directory.
#'cd .\backend\PyTest'      <-- Changes to current directory
#'pytest pyTestTester.py'   <-- Runs tests from "pyTestTester.py"

#Define test function, use testX <-- X = the function you're testing
def testExampleFunction():
    #Assert what is going to be returned. E.g below a > b should return a.
    assert exampleFunction(2, 1) == 2
    assert exampleFunction(2, 2) == 4
    assert exampleFunction(2, 3) == 3

def testDivide():
    #Example of how to test for erros. We know b can't be zero, so we check if we get an error for trying.
    with pytest.raises(ValueError, match="Cannot divide by zero"):
        divide(1, 0)

#A fixture is a setup for tests, that runs before each test begins.
@pytest.fixture
def db():
    database = Database() #Creates database
    yield database #Provides db when function is asked to
    database.data.clear() #Makes sure to clear db, so it doesn't affect other tests


#As a parameter we take a new instance of db, which is then used to create a user
def test_add_user(db):
    assert db.addUser("user1", "user@email.com") == True
    assert db.getUser("user1") == "user@email.com"

def test_add_same_user(db):
    assert db.addUser("user1", "user1@email.com") == True
    with pytest.raises(ValueError, match="Username already exists"):
        db.addUser("user1", "user@email.com") == True

def test_delete_user(db):
    assert db.addUser("user1", "user@email.com") == True
    assert db.deleteUser("user1") is None

#Mocking is used when external Services are in play. That could be anything from an api to the db
#Makes sure test is not dependent on external factors(API, DB) only checks if your code works

def test_get_weather(mocker):
    #The mocker is mocking the requests.get method
    mock_get = mocker.patch("pyTestTests.requests.get")

    #We now give our mocker values to use
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"temperature": 25, "condition": "Sunny"}

    #Assertions
    assert get_weather("Dubai") == {"temperature": 25, "condition": "Sunny"}

    #We can also check if functions are actually used
    #We check if our mocker gets called ONCE with the correct parameter
    mock_get.assert_called_once_with("https://api.weather.com/v1/Dubai")


#Big up this guy https://www.youtube.com/watch?v=EgpLj86ZHFQ, for teaching me how to do this stuff