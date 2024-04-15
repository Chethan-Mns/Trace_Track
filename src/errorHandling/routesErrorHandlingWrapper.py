from functools import wraps
from flask import abort


def asyncWrapper(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            resp = f(*args, **kwargs)
            return resp
        except Exception as e:
            print(e)
            return abort(500, str(e))

    return decorated
