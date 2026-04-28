from functools import wraps
from flask import jsonify, g

def jwt_required(optional=False):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if not getattr(g, 'user_id', None) and not optional:
                return jsonify({"msg": "Missing Authorization Header o token inválido"}), 401
            return fn(*args, **kwargs)
        return decorator
    return wrapper

def role_required(required_role):
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if not getattr(g, 'user_id', None):
                return jsonify({"msg": "No autenticado"}), 401
            if getattr(g, 'role', None) != required_role:
                return jsonify({"msg": "Acceso denegado. Rol insuficiente."}), 403
            return fn(*args, **kwargs)
        return decorator
    return wrapper
