import os
from functools import wraps
import sys

sys.path.append('src')
from errorHandling.customAPIsErrors import customApiError
from utill.helperFunctions import getDateTime, utcfromtimestamp
from dotenv import load_dotenv
from flask import request, abort
from controllers.userToServer import userToServer

load_dotenv()
import jwt

appController = userToServer()


def token_required(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        if not request.cookies.get('token'):
            return abort(401, 'Token is missing')
        token = request.cookies.get('token')
        if not len(token):
            return abort(401, 'No Value in Token')
        data = jwt.decode(token, os.environ.get('secret_key'), algorithms=[ "HS256" ])
        if 'exp' in data and getDateTime() > utcfromtimestamp(data [ 'exp' ]):
            return abort(401, "Token has expired. Please Login Again")
        current_user = appController.getUserByUserId(data [ 'userId' ])
        if current_user is None:
            return abort(401, "Invalid Authentication token!")
        # if not current_user [ 1 ] [ 'userStatus' ]:
        #     return {
        #         "message": "Your account is disabled by admin. Please contact admin"
        #     }, 401
        current_user = current_user [ 'name' ]
        return f(current_user, *args, **kwargs)

    return decorated


def token_required_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not request.cookies.get('token'):
            return abort(401, 'Token is missing')
        token = request.cookies.get('token')
        if not len(token):
            return abort(401, 'No Value in Token')
        data = jwt.decode(token, os.environ.get('secret_key'), algorithms=[ "HS256" ])
        if 'exp' in data and getDateTime() > utcfromtimestamp(data [ 'exp' ]):
            return abort(401, "Token has expired. Please Login Again")
        current_user = appController.getUserByUserId(data [ 'userId' ])
        if current_user is None or current_user [ 'type' ] != 'admin':
            return abort(401, "Invalid Authentication token or user is not admin ")
        # if not current_user [ 1 ] [ 'userStatus' ]:
        #     return {
        #         "message": "Your account is disabled by admin. Please contact admin"
        #     }, 401
        current_user = current_user [ 'name' ]
        return f(current_user, *args, **kwargs)

    return decorated
