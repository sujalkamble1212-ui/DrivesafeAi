"""
DriveSafe AI — Alerts Routes
================================
Endpoints:
  GET  /api/alerts          — paginated alert history for user
  GET  /api/alerts/<id>     — single alert detail
  DELETE /api/alerts/<id>   — delete alert
"""

from flask              import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions   import db
from models.alert import Alert

alerts_bp = Blueprint("alerts", __name__, url_prefix="/api/alerts")


@alerts_bp.route("", methods=["GET"])
@jwt_required()
def list_alerts():
    """
    List alerts for the authenticated user.
    Query params:
      page        : int (default 1)
      per_page    : int (default 20)
      session_id  : int (filter by session)
      alert_type  : str (filter by type)
    """
    user_id    = int(get_jwt_identity())
    page       = request.args.get("page",       1,  type=int)
    per_page   = request.args.get("per_page",   20, type=int)
    session_id = request.args.get("session_id", None, type=int)
    alert_type = request.args.get("alert_type", None)

    query = Alert.query.filter_by(user_id=user_id)

    if session_id:
        query = query.filter_by(session_id=session_id)
    if alert_type:
        query = query.filter_by(alert_type=alert_type)

    pagination = (
        query
        .order_by(Alert.timestamp.desc())
        .paginate(page=page, per_page=per_page, error_out=False)
    )

    return jsonify({
        "alerts":   [a.to_dict() for a in pagination.items],
        "total":    pagination.total,
        "page":     page,
        "per_page": per_page,
        "pages":    pagination.pages,
    }), 200


@alerts_bp.route("/<int:alert_id>", methods=["GET"])
@jwt_required()
def get_alert(alert_id: int):
    """Return a single alert record."""
    user_id = int(get_jwt_identity())
    alert   = Alert.query.filter_by(id=alert_id, user_id=user_id).first_or_404()
    return jsonify({"alert": alert.to_dict()}), 200


@alerts_bp.route("/<int:alert_id>", methods=["DELETE"])
@jwt_required()
def delete_alert(alert_id: int):
    """Delete a single alert."""
    user_id = int(get_jwt_identity())
    alert   = Alert.query.filter_by(id=alert_id, user_id=user_id).first_or_404()
    db.session.delete(alert)
    db.session.commit()
    return jsonify({"message": f"Alert {alert_id} deleted."}), 200
