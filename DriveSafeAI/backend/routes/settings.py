"""
DriveSafe AI — Settings Routes
=================================
Endpoints:
  GET  /api/settings   — get user settings
  PUT  /api/settings   — update settings
"""

from flask              import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions      import db
from models.user     import UserSettings

settings_bp = Blueprint("settings", __name__, url_prefix="/api/settings")

VALID_SENSITIVITIES = {"low", "medium", "high"}


@settings_bp.route("", methods=["GET"])
@jwt_required()
def get_settings():
    """Return current user settings."""
    user_id  = int(get_jwt_identity())
    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if not settings:
        # Create defaults on-the-fly if somehow missing
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)
        db.session.commit()

    return jsonify({"settings": settings.to_dict()}), 200


@settings_bp.route("", methods=["PUT"])
@jwt_required()
def update_settings():
    """
    Update user settings.
    Body (all fields optional):
      {
        voice_alerts_enabled : bool,
        sensitivity          : "low" | "medium" | "high",
        camera_index         : int,
        dark_mode            : bool,
      }
    """
    user_id  = int(get_jwt_identity())
    data     = request.get_json(silent=True) or {}
    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if not settings:
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)

    if "voice_alerts_enabled" in data:
        settings.voice_alerts_enabled = bool(data["voice_alerts_enabled"])

    if "sensitivity" in data:
        if data["sensitivity"] not in VALID_SENSITIVITIES:
            return jsonify({"error": f"sensitivity must be one of {VALID_SENSITIVITIES}"}), 400
        settings.sensitivity = data["sensitivity"]

    if "camera_index" in data:
        settings.camera_index = int(data["camera_index"])

    if "dark_mode" in data:
        settings.dark_mode = bool(data["dark_mode"])

    db.session.commit()

    return jsonify({
        "message":  "Settings updated.",
        "settings": settings.to_dict(),
    }), 200
