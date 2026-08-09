"""
DriveSafe AI — Reports Routes
================================
Endpoints:
  GET  /api/reports/<session_id>         — generate/download PDF
  GET  /api/reports/<session_id>/status  — check if report exists
"""

import os
import logging

from flask              import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions          import db
from models.session      import DrivingSession
from models.alert        import Alert
from models.user         import User
from detection.report_generator import ReportGenerator

logger = logging.getLogger(__name__)

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

_generator = ReportGenerator()


@reports_bp.route("/<int:session_id>", methods=["GET"])
@jwt_required()
def get_report(session_id: int):
    """
    Generate (if not cached) and stream the PDF report for a session.
    """
    user_id = int(get_jwt_identity())

    session_obj = DrivingSession.query.filter_by(
        id=session_id, user_id=user_id
    ).first_or_404()

    user = User.query.get_or_404(user_id)

    # Return cached report if it exists and file is on disk
    if session_obj.report_path and os.path.exists(session_obj.report_path):
        return send_file(
            session_obj.report_path,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=f"DriveSafeAI_Report_Session_{session_id}.pdf",
        )

    # Gather alerts for this session
    alerts = (
        Alert.query
        .filter_by(session_id=session_id)
        .order_by(Alert.timestamp.asc())
        .all()
    )

    # Generate PDF
    try:
        pdf_path = _generator.generate(
            session=session_obj.to_dict(),
            user=user.to_dict(),
            alerts=[a.to_dict() for a in alerts],
        )
    except Exception as exc:
        logger.error(f"PDF generation error: {exc}")
        return jsonify({"error": f"Report generation failed: {exc}"}), 500

    # Cache path in DB
    session_obj.report_path = pdf_path
    db.session.commit()

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"DriveSafeAI_Report_Session_{session_id}.pdf",
    )


@reports_bp.route("/<int:session_id>/status", methods=["GET"])
@jwt_required()
def report_status(session_id: int):
    """Check whether a PDF report has been generated for a session."""
    user_id = int(get_jwt_identity())

    session_obj = DrivingSession.query.filter_by(
        id=session_id, user_id=user_id
    ).first_or_404()

    has_report = bool(
        session_obj.report_path and
        os.path.exists(session_obj.report_path)
    )

    return jsonify({
        "session_id": session_id,
        "has_report": has_report,
        "report_path": session_obj.report_path,
    }), 200
