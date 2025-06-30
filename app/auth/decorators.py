from functools import wraps
from flask_jwt_extended import get_jwt, verify_jwt_in_request
from flask import jsonify

def role_required(required_role):
    """
    A decorator to protect routes based on user roles.
    `required_role` can be a single role string or a list of allowed roles.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_roles = claims.get('roles', []) # 'roles' claim is set during login

            # Normalize roles to a list
            if not isinstance(user_roles, list):
                user_roles = [user_roles]

            allowed_roles = required_role if isinstance(required_role, list) else [required_role]
            
            # Check if user has any of the required roles
            if not any(role in user_roles for role in allowed_roles):
                return jsonify(msg=f"Access denied: '{', '.join(allowed_roles)}' role required."), 403
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator

# Specific role decorators for convenience
admin_required = role_required('admin')
manager_required = role_required(['admin', 'manager'])
owner_required = role_required(['admin', 'owner'])
