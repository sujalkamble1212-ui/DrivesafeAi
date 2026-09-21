"""
DriveSafe AI — Screenshots Routes
=====================================
Serves alert screenshots stored in MongoDB GridFS.

Endpoints:
  GET /api/screenshots/<file_id>   — stream image from GridFS by its ID
"""

import io
import logging
import os

from flask              import Blueprint, send_file, jsonify, send_from_directory
from flask_jwt_extended import jwt_required

from storage.gridfs_storage import load_file as gridfs_load_file
from config import SCREENSHOTS_DIR

logger = logging.getLogger(__name__)

screenshots_bp = Blueprint("screenshots", __name__, url_prefix="/api/screenshots")


def _is_gridfs_id(value: str) -> bool:
    """True if value looks like a 24-char hex ObjectId."""
    return bool(value) and len(value) == 24 and all(c in "0123456789abcdefABCDEF" for c in value)


@screenshots_bp.route("/<string:file_ref>", methods=["GET"])
@jwt_required(optional=True)
def get_screenshot(file_ref: str):
    """
    Stream a screenshot image.

    file_ref can be:
      - A 24-char hex GridFS ObjectId  → load from MongoDB GridFS
      - A local filename               → serve from SCREENSHOTS_DIR (fallback)
    """
    if _is_gridfs_id(file_ref):
        # Load from GridFS
        try:
            data, filename, content_type = gridfs_load_file(file_ref)
            return send_file(
                io.BytesIO(data),
                mimetype=content_type or "image/jpeg",
                download_name=filename,
            )
        except FileNotFoundError:
            return jsonify({"error": "Screenshot not found."}), 404
        except Exception as exc:
            logger.error("GridFS screenshot load error: %s", exc)
            return jsonify({"error": "Could not load screenshot."}), 500
    else:
        # Legacy: serve from local disk
        filename = os.path.basename(file_ref)   # prevent directory traversal
        filepath = os.path.join(SCREENSHOTS_DIR, filename)
        if not os.path.isfile(filepath):
            return jsonify({"error": "Screenshot not found."}), 404
        return send_from_directory(SCREENSHOTS_DIR, filename)
