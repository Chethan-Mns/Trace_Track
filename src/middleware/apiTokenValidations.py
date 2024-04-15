import os
from functools import wraps
import sys

sys.path.append('src')
from errorHandling.customAPIsErrors import customApiError
from utill.helperFunctions import getDateTime, utcfromtimestamp
from dotenv import load_dotenv
from controllers.userToServer import userToServer

load_dotenv()
import jwt
from fastapi import Request, Query, HTTPException

appController = userToServer()


async def get_current_user(request: Request):
    cookie_token = request.query_params.get('token')
    if cookie_token is None:
        raise HTTPException(status_code=401, detail="Token is missing")
    data = jwt.decode(cookie_token, os.environ.get('secret_key'), algorithms=[ "HS256" ])
    if 'exp' in data and getDateTime() > utcfromtimestamp(data [ 'exp' ]):
        raise HTTPException(detail="Token has expired. Please Login Again", status_code=401)
    current_user = appController.getUserByUserId(data [ 'userId' ])
    # Return the user_id from the payload
    return current_user


def token_required(f):
    @wraps(f)
    async def decorated(request: Request, *args, **kwargs):
        print(request.query_params)
        if not request.query_params.get('token'):
            raise customApiError("Token is missing", 401)
        token = request.query_params.get('token')
        if not len(token):
            raise customApiError('No Value in Token', 401)
        data = jwt.decode(token, os.environ.get('secret_key'), algorithms=[ "HS256" ])
        if 'exp' in data and getDateTime() > utcfromtimestamp(data [ 'exp' ]):
            raise customApiError("Token has expired. Please Login Again", 401)
        current_user = appController.getUserByUserId(data [ 'userId' ])
        if current_user is None:
            raise customApiError("Invalid Authentication token!", 401)
        # if not current_user [ 1 ] [ 'userStatus' ]:
        #     return {
        #         "message": "Your account is disabled by admin. Please contact admin"
        #     }, 401
        return await f(request, *args, **kwargs)

    return decorated
