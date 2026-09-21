"""
DriveSafe AI — Sessions Routes
=================================
Endpoints:
  GET  /api/sessions              — list user's sessions (paginated)
  GET  /api/sessions/<session_id> — single session with alerts
  DELETE /api/sessions/<session_id> — delete a session
"""

import math
from flask              import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.session import DrivingSession
from models.alert   import Alert

sessions_bp = Blueprint("sessions", __name__, url_prefix="/api/sessions")


@sessions_bp.route("", methods=["GET"])
@jwt_required()
def list_sessions():
    """
    List all sessions for the authenticated user, newest first.
    Query params: page=1, per_page=10
    """
    user_id  = str(get_jwt_identity())
    page     = request.args.get("page",     1,  type=int)
    per_page = request.args.get("per_page", 10, type=int)

    page = max(1, page)
    per_page = max(1, per_page)

    query = DrivingSession.objects(user_id=user_id).order_by("-start_time")
    total = query.count()
    pages = math.ceil(total / per_page) if total > 0 else 1

    offset = (page - 1) * per_page
    items = query.skip(offset).limit(per_page)

    return jsonify({
        "sessions":   [s.to_dict() for s in items],
        "total":      total,
        "page":       page,
        "per_page":   per_page,
        "pages":      pages,
    }), 200


@sessions_bp.route("/<string:session_id>", methods=["GET"])
@jwt_required()
def get_session(session_id: str):
    """Return a single session with its alert history."""
    user_id = str(get_jwt_identity())

    try:
        session_obj = DrivingSession.objects(id=session_id, user_id=user_id).first()
    except Exception:
        session_obj = None

    if not session_obj:
        return jsonify({"error": "Session not found."}), 404

    alerts = Alert.objects(session_id=str(session_id)).order_by("+timestamp")

    return jsonify({
        "session": session_obj.to_dict(),
        "alerts":  [a.to_dict() for a in alerts],
    }), 200


@sessions_bp.route("/<string:session_id>", methods=["DELETE"])
@jwt_required()
def delete_session(session_id: str):
    """Delete a session and all its associated alerts."""
    user_id = str(get_jwt_identity())

    try:
        session_obj = DrivingSession.objects(id=session_id, user_id=user_id).first()
    except Exception:
        session_obj = None

    if not session_obj:
        return jsonify({"error": "Session not found."}), 404

    Alert.objects(session_id=str(session_id)).delete()
    session_obj.delete()

    return jsonify({"message": f"Session {session_id} deleted."}), 200
