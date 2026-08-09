"""
DriveSafe AI — Alert SQLAlchemy Model
"""

from datetime import datetime
from extensions import db


class Alert(db.Model):
    __tablename__ = "alerts"

    id              = db.Column(db.Integer, primary_key=True)
    session_id      = db.Column(db.Integer, db.ForeignKey("driving_sessions.id"), nullable=False)
    user_id         = db.Column(db.Integer, db.ForeignKey("users.id"),            nullable=False)

    # Alert metadata
    alert_type      = db.Column(db.String(50),  nullable=False)
    # Possible values:
    #   "drowsiness"       – eyes closed too long
    #   "distraction"      – looking away too long
    #   "phone_detected"   – phone in frame
    #   "yawn_detected"    – yawning

    severity        = db.Column(db.String(10),  default="warning")
    # "info" | "warning" | "danger"

    message         = db.Column(db.String(500), nullable=True)
    screenshot_path = db.Column(db.String(500), nullable=True)

    timestamp       = db.Column(db.DateTime, default=datetime.utcnow)

    # Detection details at time of alert
    eye_status      = db.Column(db.String(20), nullable=True)
    head_pose       = db.Column(db.String(30), nullable=True)
    confidence      = db.Column(db.Float,      nullable=True)

    def to_dict(self) -> dict:
        return {
            "id":              self.id,
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
