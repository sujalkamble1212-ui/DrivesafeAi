"""
DriveSafe AI — GridFS Storage Helper
======================================
Provides helpers to store and retrieve binary files (screenshots, PDFs)
in MongoDB GridFS so they persist across Hugging Face container restarts.

Usage:
    from storage.gridfs_storage import save_file, load_file, delete_file
"""

import io
import os
import logging
from gridfs import GridFS
from pymongo import MongoClient
from bson import ObjectId

logger = logging.getLogger(__name__)

_gridfs: GridFS | None = None
_client: MongoClient | None = None


def _get_gridfs() -> GridFS:
    """
    Lazily create a GridFS handle using MONGODB_URI from environment.
    Re-uses the same connection across calls (module-level singleton).
    """
    global _gridfs, _client
    if _gridfs is None:
        uri    = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/drivesafe_ai")
        db_name = os.environ.get("MONGODB_DB", "drivesafe_ai")
        _client = MongoClient(uri)
        db      = _client[db_name]
        _gridfs = GridFS(db)
        logger.info("GridFS initialised on database '%s'", db_name)
    return _gridfs


def save_file(data: bytes, filename: str, content_type: str = "application/octet-stream") -> str:
    """
    Save bytes to GridFS.

    Args:
        data         : Raw bytes of the file.
        filename     : Human-readable filename stored in GridFS metadata.
        content_type : MIME type (e.g. 'image/jpeg', 'application/pdf').

    Returns:
        str — the GridFS file_id as a hex string, to be stored in MongoDB.
    """
    try:
        fs = _get_gridfs()
        file_id = fs.put(
            io.BytesIO(data),
            filename=filename,
            content_type=content_type,
        )
        logger.debug("Saved %s to GridFS as %s", filename, str(file_id))
        return str(file_id)
    except Exception as exc:
        logger.error("GridFS save error for %s: %s", filename, exc)
        raise exc


def load_file(file_id: str) -> tuple[bytes, str, str]:
    """
    Load a file from GridFS by its ID.

    Returns:
        (data_bytes, filename, content_type)

    Raises:
        FileNotFoundError if the file doesn't exist.
    """
    try:
        fs = _get_gridfs()
        grid_out = fs.get(ObjectId(file_id))
        data = grid_out.read()
        return data, grid_out.filename, grid_out.content_type
    except Exception as exc:
        logger.error("GridFS load error for id=%s: %s", file_id, exc)
        raise FileNotFoundError(f"File {file_id} not found in GridFS") from exc


def delete_file(file_id: str) -> None:
    """Delete a file from GridFS by its ID (best-effort)."""
    try:
        fs = _get_gridfs()
        fs.delete(ObjectId(file_id))
        logger.debug("Deleted GridFS file %s", file_id)
    except Exception as exc:
        logger.warning("GridFS delete warning for id=%s: %s", file_id, exc)
