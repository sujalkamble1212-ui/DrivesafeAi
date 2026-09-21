"""
DriveSafe AI — Alerts Routes
================================
Endpoints:
  GET  /api/alerts            — paginated alert history for user
  GET  /api/alerts/<alert_id> — single alert detail
  DELETE /api/alerts/<alert_id> — delete alert
"""

import math
from flask              import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

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
      session_id  : str (filter by session)
      alert_type  : str (filter by type)
    """
    user_id    = str(get_jwt_identity())
    page       = request.args.get("page",       1,  type=int)
    per_page   = request.args.get("per_page",   20, type=int)
    session_id = request.args.get("session_id", None)
    alert_type = request.args.get("alert_type", None)

    page = max(1, page)
    per_page = max(1, per_page)

    filters = {"user_id": user_id}
    if session_id:
        filters["session_id"] = str(session_id)
    if alert_type:
        filters["alert_type"] = alert_type

    query = Alert.objects(**filters).order_by("-timestamp")
    total = query.count()
    pages = math.ceil(total / per_page) if total > 0 else 1

    offset = (page - 1) * per_page
    items = query.skip(offset).limit(per_page)

    return jsonify({
        "alerts":   [a.to_dict() for a in items],
        "total":    total,
        "page":     page,
        "per_page": per_page,
        "pages":    pages,
    }), 200


@alerts_bp.route("/<string:alert_id>", methods=["GET"])
@jwt_required()
def get_alert(alert_id: str):
    """Return a single alert record."""
    user_id = str(get_jwt_identity())
    try:
        alert = Alert.objects(id=alert_id, user_id=user_id).first()
    except Exception:
        alert = None

    if not alert:
        return jsonify({"error": "Alert not found."}), 404

    return jsonify({"alert": alert.to_dict()}), 200


@alerts_bp.route("/<string:alert_id>", methods=["DELETE"])
@jwt_required()
def delete_alert(alert_id: str):
    """Delete a single alert."""
    user_id = str(get_jwt_identity())
    try:
        alert = Alert.objects(id=alert_id, user_id=user_id).first()
    except Exception:
        alert = None

    if not alert:
        return jsonify({"error": "Alert not found."}), 404

    alert.delete()
    return jsonify({"message": f"Alert {alert_id} deleted."}), 200
