"""
DriveSafe AI — User MongoEngine Model
"""

from datetime import datetime
import bcrypt
from mongoengine import (
    Document, StringField, EmailField, DateTimeField,
    BooleanField, IntField
)


class User(Document):
    meta = {
        "collection": "users",
        "indexes": ["username", "email"]
    }

    username      = StringField(required=True, unique=True, max_length=80)
    email         = EmailField(required=True, unique=True, max_length=120)
    password_hash = StringField(required=True, max_length=128)
    full_name     = StringField(max_length=120, default="")
    created_at    = DateTimeField(default=datetime.utcnow)
    updated_at    = DateTimeField(default=datetime.utcnow)

    # ──────────────────────────────────────────
    # Password helpers
    # ──────────────────────────────────────────

    def set_password(self, password: str) -> None:
        """Hash and store password using bcrypt."""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

    def check_password(self, password: str) -> bool:
        """Verify a plaintext password against stored hash."""
        return bcrypt.checkpw(
            password.encode("utf-8"),
            self.password_hash.encode("utf-8")
        )

    # ──────────────────────────────────────────
    # Serialization
    # ──────────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id":         str(self.id),
            "username":   self.username,
            "email":      self.email,
            "full_name":  self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class UserSettings(Document):
    meta = {
        "collection": "user_settings",
        "indexes": ["user_id"]
    }

    user_id              = StringField(required=True, unique=True)

    # Voice alerts
    voice_alerts_enabled = BooleanField(default=True)

    # Detection
    sensitivity          = StringField(default="medium", max_length=10)  # low / medium / high

    # Camera
    camera_index         = IntField(default=0)

    # UI
    dark_mode            = BooleanField(default=True)

    updated_at           = DateTimeField(default=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "voice_alerts_enabled": self.voice_alerts_enabled,
            "sensitivity":          self.sensitivity,
            "camera_index":         self.camera_index,
            "dark_mode":            self.dark_mode,
        }

    def __repr__(self) -> str:
        return f"<UserSettings user={self.user_id}>"
