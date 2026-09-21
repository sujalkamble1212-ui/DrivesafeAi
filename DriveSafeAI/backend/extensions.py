"""
DriveSafe AI — Database + JWT Extensions
Separate module to avoid circular imports.
"""

import logging
from mongoengine import connect
from flask_jwt_extended import JWTManager

logger = logging.getLogger(__name__)

jwt = JWTManager()


def init_db(app):
    """Initialize MongoEngine connection using MONGODB_URI and MONGODB_DB."""
    mongodb_uri = app.config.get("MONGODB_URI", "mongodb://localhost:27017/drivesafe_ai")
    db_name     = app.config.get("MONGODB_DB", "drivesafe_ai")
    try:
        connect(db=db_name, host=mongodb_uri)
        logger.info("Connected to MongoDB successfully.")
    except Exception as exc:
        logger.error(f"Failed to connect to MongoDB: {exc}")
        raise exc
