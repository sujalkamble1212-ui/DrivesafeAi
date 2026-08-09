"""
DriveSafe AI — Sessions Routes
=================================
Endpoints:
  GET  /api/sessions          — list user's sessions (paginated)
  GET  /api/sessions/<id>     — single session with alerts
  DELETE /api/sessions/<id>   — delete a session
"""

from flask              import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions     import db
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
    user_id  = int(get_jwt_identity())
    page     = request.args.get("page",     1,  type=int)
    per_page = request.args.get("per_page", 10, type=int)

    pagination = (
        DrivingSession.query
        .filter_by(user_id=user_id)
        .order_by(DrivingSession.start_time.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "sessions":   [s.to_dict() for s in pagination.items],
        "total":      pagination.total,
        "page":       page,
        "per_page":   per_page,
        "pages":      pagination.pages,
    }), 200


@sessions_bp.route("/<int:session_id>", methods=["GET"])
@jwt_required()
def get_session(session_id: int):
    """Return a single session with its alert history."""
    user_id = int(get_jwt_identity())

    session_obj = DrivingSession.query.filter_by(
        id=session_id, user_id=user_id
    ).first_or_404()

    alerts = (
        Alert.query
        .filter_by(session_id=session_id)
        .order_by(Alert.timestamp.asc())
        .all()
    )

    return jsonify({
        "session": session_obj.to_dict(),
        "alerts":  [a.to_dict() for a in alerts],
    }), 200


@sessions_bp.route("/<int:session_id>", methods=["DELETE"])
@jwt_required()
def delete_session(session_id: int):
    """Delete a session and all its associated alerts."""
    user_id = int(get_jwt_identity())

    session_obj = DrivingSession.query.filter_by(
        id=session_id, user_id=user_id
    ).first_or_404()

    db.session.delete(session_obj)
    db.session.commit()

    return jsonify({"message": f"Session {session_id} deleted."}), 200
