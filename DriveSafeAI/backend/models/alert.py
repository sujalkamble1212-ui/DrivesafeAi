"""
DriveSafe AI — Alert MongoEngine Model
"""

from datetime import datetime
from mongoengine import (
    Document, StringField, DateTimeField, FloatField
)


class Alert(Document):
    meta = {
        "collection": "alerts",
        "indexes": [
            "session_id",
            "user_id",
            "-timestamp",
            ("session_id", "-timestamp")
        ]
    }

    session_id      = StringField(required=True)
    user_id         = StringField(required=True)

    # Alert metadata
    alert_type      = StringField(required=True, max_length=50)
    severity        = StringField(default="warning", max_length=10)
    message         = StringField(max_length=500, null=True)
    screenshot_path = StringField(max_length=500, null=True)

    timestamp       = DateTimeField(default=datetime.utcnow)

    # Detection details at time of alert
    eye_status      = StringField(max_length=20, null=True)
    head_pose       = StringField(max_length=30, null=True)
    confidence      = FloatField(null=True)

    def to_dict(self) -> dict:
        return {
            "id":              str(self.id),
            "session_id":      self.session_id,
            "user_id":         self.user_id,
            "alert_type":      self.alert_type,
            "severity":        self.severity,
            "message":         self.message,
            "screenshot_path": self.screenshot_path,
            "timestamp":       self.timestamp.isoformat() if self.timestamp else None,
            "eye_status":      self.eye_status,
            "head_pose":       self.head_pose,
            "confidence":      self.confidence,
        }

    def __repr__(self) -> str:
        return f"<Alert type={self.alert_type} session={self.session_id}>"
