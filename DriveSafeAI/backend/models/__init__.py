"""
DriveSafe AI — models __init__
Register all models so SQLAlchemy can create tables.
"""

from models.user    import User, UserSettings   # noqa: F401
from models.session import DrivingSession        # noqa: F401
from models.alert   import Alert                 # noqa: F401
