from functools import wraps
from flask import abort
from flask_login import current_user

def role_required(role_name):
    def decorator(f):
        @wraps(f)
        def wrapped_function(*args, **kwargs):
            # ユーザーがログインしていない、または指定された役割を持っていない場合、403エラーを返す
            if not current_user.is_authenticated or not current_user.has_role(role_name):
                abort(403)  # Forbiddenエラー
            return f(*args, **kwargs)
        return wrapped_function
    return decorator
