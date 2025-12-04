import jwt
from flask import request, jsonify
from os import getenv
import datetime

TokenLookup = {}
""" A dictionary that tracks used tokens by a given username. """

def LookupUserToken(username: str) -> str | None:
    """ Returns a jwt associated with a given username if found """
    return TokenLookup.get(username)

def TryFreeToken(username: str) -> bool:
    """ Tries to free a token by the given username in the lookup dictionary """
    if not TokenLookup[username]: return False
    del TokenLookup[username]
    return True

def TokenRequired(f):
    """ Used to verify the provided jwt in a request """
    def decorated(*args, **kwargs):
        data = request.get_json()
        token = data.get('jwt')
        if not token:
            return jsonify({'error': 'user token is missing'}), 401
        try:
            DecodeToken(token)
        except Exception:
            return jsonify({'error': 'user token is invalid/expired'}), 401
        return f(*args, **kwargs)
    return decorated

def DecodeToken(token: str) -> any:
    """ Decode a jwt into its original payload """
    return jwt.decode(token, getenv("FLASK_SECRET_KEY"), algorithms=getenv("TOKEN_ALGORITHIM"))

def CreateToken(username: str) -> str:
    """ Creates a new jwt or reuses an existing jwt """
    token = TokenLookup.get(username)
    if token is not None:
        data = DecodeToken(token)
        if data and datetime.datetime.fromtimestamp(data.get('exp')) > datetime.datetime.utcnow(): return token
        
    token = jwt.encode({
        "username": username,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=int(getenv("SESSION_DURATION")))
        }, getenv("FLASK_SECRET_KEY"), algorithm=getenv("TOKEN_ALGORITHIM"))
    TokenLookup[username] = token
    return token