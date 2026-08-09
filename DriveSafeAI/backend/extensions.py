"""
DriveSafe AI — SQLAlchemy + JWT Extensions
Separate module to avoid circular imports.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db  = SQLAlchemy()
jwt = JWTManager()
