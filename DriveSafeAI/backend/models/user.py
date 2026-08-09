"""
DriveSafe AI — User SQLAlchemy Model
"""

from datetime import datetime
from extensions import db
import bcrypt


class User(db.Model):
    __tablename__ = "users"

    id           = db.Column(db.Integer, primary_key=True)
    username     = db.Column(db.String(80),  unique=True, nullable=False, index=True)
    email        = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    full_name    = db.Column(db.String(120), nullable=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    sessions     = db.relationship("DrivingSession", backref="user", lazy=True,
                                   cascade="all, delete-orphan")
    settings     = db.relationship("UserSettings",   backref="user", lazy=True,
                                   uselist=False,    cascade="all, delete-orphan")

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
            "id":         self.id,
            "username":   self.username,
            "email":      self.email,
            "full_name":  self.full_name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self) -> str:
        return f"<User {self.username}>"


class UserSettings(db.Model):
    __tablename__ = "user_settings"

    id                   = db.Column(db.Integer, primary_key=True)
    user_id              = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)

    # Voice alerts
    voice_alerts_enabled = db.Column(db.Boolean, default=True)

    # Detection
    sensitivity          = db.Column(db.String(10), default="medium")  # low / medium / high

    # Camera
    camera_index         = db.Column(db.Integer,  default=0)

    # UI
    dark_mode            = db.Column(db.Boolean, default=True)

    updated_at           = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "voice_alerts_enabled": self.voice_alerts_enabled,
            "sensitivity":          self.sensitivity,
            "camera_index":         self.camera_index,
            "dark_mode":            self.dark_mode,
        }
