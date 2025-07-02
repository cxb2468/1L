from flask import abort
from flask_login import current_user
from functools import wraps

def permission_required(module):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_admin:
                return f(*args, **kwargs)
            if not current_user.permissions:
                abort(403)
            perms = [p.strip() for p in current_user.permissions.split(',') if p.strip()]
            if module not in perms:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator 