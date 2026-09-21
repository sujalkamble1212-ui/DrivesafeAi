"""
DriveSafe AI — DrivingSession MongoEngine Model
"""

from datetime import datetime
from mongoengine import (
    Document, StringField, DateTimeField, FloatField,
    IntField, BooleanField
)


class DrivingSession(Document):
    meta = {
        "collection": "driving_sessions",
        "indexes": [
            "user_id",
            "-start_time",
            ("user_id", "-start_time")
        ]
    }

    user_id          = StringField(required=True)

    # Timing
    start_time       = DateTimeField(default=datetime.utcnow)
    end_time         = DateTimeField(null=True)
    duration_seconds = FloatField(default=0.0)

    # Scores (0–100)
    safety_score     = FloatField(default=100.0)
    attention_score  = FloatField(default=100.0)

    # Event counters
    eye_closure_count = IntField(default=0)
    yawn_count        = IntField(default=0)
    phone_usage_count = IntField(default=0)
    total_alerts      = IntField(default=0)

    # Report
    report_path      = StringField(null=True)
    is_active        = BooleanField(default=True)

    # ──────────────────────────────────────────
    # Computed property
    # ──────────────────────────────────────────

    @property
    def duration_formatted(self) -> str:
        """Return duration as HH:MM:SS string."""
        total = int(self.duration_seconds or 0)
        hours   = total // 3600
        minutes = (total % 3600) // 60
        seconds = total % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def to_dict(self) -> dict:
        return {
            "id":                 str(self.id),
            "user_id":            self.user_id,
            "start_time":         self.start_time.isoformat() if self.start_time else None,
            "end_time":           self.end_time.isoformat()   if self.end_time   else None,
            "duration_seconds":   self.duration_seconds,
            "duration_formatted": self.duration_formatted,
            "safety_score":       round(self.safety_score,    2) if self.safety_score is not None else 100.0,
            "attention_score":    round(self.attention_score, 2) if self.attention_score is not None else 100.0,
            "eye_closure_count":  self.eye_closure_count,
            "yawn_count":         self.yawn_count,
            "phone_usage_count":  self.phone_usage_count,
            "total_alerts":       self.total_alerts,
            "report_path":        self.report_path,
            "is_active":          self.is_active,
        }

    def __repr__(self) -> str:
        return f"<DrivingSession id={self.id} user={self.user_id}>"
