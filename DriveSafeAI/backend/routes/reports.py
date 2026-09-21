"""
DriveSafe AI — Reports Routes
================================
Endpoints:
  GET  /api/reports/<session_id>         — generate/download PDF
  GET  /api/reports/<session_id>/status  — check if report exists

Reports are stored in MongoDB GridFS so they persist across deployments.
The session.report_path field holds either:
  - A GridFS file_id string (e.g. "67f3a1b2c8d4e5f600112233")
  - A local file path (fallback, e.g. "/app/reports/report_xxx.pdf")
"""

import os
import io
import logging

from flask              import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity

from models.session      import DrivingSession
from models.alert        import Alert
from models.user         import User
from detection.report_generator import ReportGenerator
from storage.gridfs_storage     import load_file as gridfs_load_file

logger = logging.getLogger(__name__)

reports_bp = Blueprint("reports", __name__, url_prefix="/api/reports")

_generator = ReportGenerator()


def _is_gridfs_id(value: str) -> bool:
    """Return True if value looks like a MongoDB ObjectId hex string (24 hex chars)."""
    return bool(value) and len(value) == 24 and all(c in "0123456789abcdefABCDEF" for c in value)


@reports_bp.route("/<string:session_id>", methods=["GET"])
@jwt_required()
def get_report(session_id: str):
    """
    Generate (if not cached) and stream the PDF report for a session.
    Prefers GridFS-stored PDFs; falls back to local disk for legacy reports.
    """
    user_id = str(get_jwt_identity())

    try:
        session_obj = DrivingSession.objects(id=session_id, user_id=user_id).first()
    except Exception:
        session_obj = None

    if not session_obj:
        return jsonify({"error": "Session not found."}), 404

    try:
        user = User.objects(id=user_id).first()
    except Exception:
        user = None

    if not user:
        return jsonify({"error": "User not found."}), 404

    download_name = f"DriveSafeAI_Report_Session_{session_id}.pdf"

    # ── Return cached report if it still exists ──────────────────────────────
    if session_obj.report_path:
        cached = session_obj.report_path

        # Case 1: stored in GridFS
        if _is_gridfs_id(cached):
            try:
                data, filename, content_type = gridfs_load_file(cached)
                return send_file(
                    io.BytesIO(data),
                    mimetype="application/pdf",
                    as_attachment=True,
                    download_name=download_name,
                )
            except FileNotFoundError:
                logger.warning("GridFS report %s not found; regenerating.", cached)
                # Fall through to regenerate

        # Case 2: stored locally (legacy / fallback)
        elif os.path.exists(cached):
            return send_file(
                cached,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=download_name,
            )

    # ── Generate a fresh PDF ─────────────────────────────────────────────────
    alerts = Alert.objects(session_id=str(session_id)).order_by("+timestamp")

    try:
        report_ref = _generator.generate(
            session=session_obj.to_dict(),
            user=user.to_dict(),
            alerts=[a.to_dict() for a in alerts],
        )
    except Exception as exc:
        logger.error("PDF generation error: %s", exc)
        return jsonify({"error": f"Report generation failed: {exc}"}), 500

    # Cache the GridFS id (or local path fallback) in the session document
    session_obj.report_path = report_ref
    session_obj.save()

    # Serve the newly generated PDF
    if _is_gridfs_id(report_ref):
        try:
            data, filename, content_type = gridfs_load_file(report_ref)
            return send_file(
                io.BytesIO(data),
                mimetype="application/pdf",
                as_attachment=True,
                download_name=download_name,
            )
        except Exception as exc:
            logger.error("Failed to load newly generated GridFS report: %s", exc)
            return jsonify({"error": "Report saved but could not be served."}), 500
    else:
        # Local fallback path
        return send_file(
            report_ref,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=download_name,
        )


@reports_bp.route("/<string:session_id>/status", methods=["GET"])
@jwt_required()
def report_status(session_id: str):
    """Check whether a PDF report has been generated for a session."""
    user_id = str(get_jwt_identity())

    try:
        session_obj = DrivingSession.objects(id=session_id, user_id=user_id).first()
    except Exception:
        session_obj = None

    if not session_obj:
        return jsonify({"error": "Session not found."}), 404

    cached = session_obj.report_path or ""
    if _is_gridfs_id(cached):
        has_report = True   # GridFS id — assume it exists (generated by us)
    else:
        has_report = bool(cached and os.path.exists(cached))

    return jsonify({
        "session_id": session_id,
        "has_report": has_report,
    }), 200
