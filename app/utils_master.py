from functools import wraps
from flask import abort
from flask_login import current_user

def requer_master(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_master:
            abort(403)
        return f(*args, **kwargs)
    return decorated
