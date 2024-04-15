from functools import wraps
import sys

sys.path.append('src')
from errorHandling.customAPIsErrors import customApiError


def asyncWrapper(f):
    @wraps(f)
    async def decorated(*args, **kwargs):
        try:
            resp = await f(*args, **kwargs)
            return resp
        except customApiError as error:
            return {
                "message": error.message.split('+') [ 0 ],
                "status_code": int(error.message.split('+') [ 1 ])}
        except Exception as e:
            print(e)
            return {"status": "error occurred", "error": str(e),
                    "message": str(e)+" Contact developer to resolve this problem."}, 500
    return decorated
