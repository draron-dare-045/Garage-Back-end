from flask import Blueprint
from flask_restful import Api

# This blueprint handles authentication-related routes
auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

# Import routes to register them with the blueprint's Api object
from . import routes
