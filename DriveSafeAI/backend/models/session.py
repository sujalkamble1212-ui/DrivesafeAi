"""
DriveSafe AI — DrivingSession SQLAlchemy Model
"""

from datetime import datetime
from extensions import db


class DrivingSession(db.Model):
    __tablename__ = "driving_sessions"

    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # Timing
    start_time      = db.Column(db.DateTime, default=datetime.utcnow)
    end_time        = db.Column(db.DateTime, nullable=True)
    duration_seconds = db.Column(db.Float, default=0.0)

    # Scores (0–100)
    safety_score    = db.Column(db.Float, default=100.0)
    attention_score = db.Column(db.Float, default=100.0)

    # Event counters
    eye_closure_count = db.Column(db.Integer, default=0)
    yawn_count        = db.Column(db.Integer, default=0)
    phone_usage_count = db.Column(db.Integer, default=0)
    total_alerts      = db.Column(db.Integer, default=0)

    # Report
    report_path     = db.Column(db.String(500), nullable=True)
    is_active       = db.Column(db.Boolean, default=True)

    # Relationships
    alerts          = db.relationship("Alert", backref="session", lazy=True,
                                      cascade="all, delete-orphan")

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
            "id":               self.id,
            "user_id":          self.user_id,
            "start_time":       self.start_time.isoformat() if self.start_time else None,
            "end_time":         self.end_time.isoformat()   if self.end_time   else None,
            "duration_seconds": self.duration_seconds,
            "duration_formatted": self.duration_formatted,
            "safety_score":     round(self.safety_score,    2),
            "attention_score":  round(self.attention_score, 2),
            "eye_closure_count": self.eye_closure_count,
            "yawn_count":       self.yawn_count,
            "phone_usage_count": self.phone_usage_count,
            "total_alerts":     self.total_alerts,
            "report_path":      self.report_path,
            "is_active":        self.is_active,
        }

    def __repr__(self) -> str:
        return f"<DrivingSession id={self.id} user={self.user_id}>"
