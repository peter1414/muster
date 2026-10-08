"""
Shared extension instances.

Kept in their own module (rather than instantiated in __init__.py) so
blueprints can `from .extensions import db` without triggering circular
imports with the app factory.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_cors import CORS

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
cors = CORS()
