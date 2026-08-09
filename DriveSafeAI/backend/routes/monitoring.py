"""
DriveSafe AI — Monitoring Routes
===================================
Endpoints:
  POST /api/monitor/session/start  — start a new session
  POST /api/monitor/session/end    — end session, compute final scores
  POST /api/monitor/frame          — process a base64 frame → detections
  POST /api/monitor/alert          — save an alert to the database
"""

import base64
import logging
import numpy as np
import cv2
from datetime import datetime

from flask              import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from extensions          import db
from models.session      import DrivingSession
from models.alert        import Alert
from models.user         import User, UserSettings

logger = logging.getLogger(__name__)

monitor_bp = Blueprint("monitor", __name__, url_prefix="/api/monitor")

# ─────────────────────────────────────────────
# Helper: decode base64 frame → numpy BGR
# ─────────────────────────────────────────────

def _decode_frame(b64_data: str) -> np.ndarray | None:
    """Decode a base64-encoded JPEG/PNG string to a BGR numpy array."""
    try:
        # Strip optional data-url prefix
        if "," in b64_data:
            b64_data = b64_data.split(",", 1)[1]
        raw  = base64.b64decode(b64_data)
        arr  = np.frombuffer(raw, dtype=np.uint8)
        frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        return frame
    except Exception as exc:
        logger.error(f"Frame decode error: {exc}")
        return None



# ─────────────────────────────────────────────
# Preview (face detection without a session)
# ─────────────────────────────────────────────

@monitor_bp.route("/preview", methods=["POST"])
@jwt_required()
def preview_frame():
    """Run face/eye/head detection on a frame WITHOUT starting a session.
    Fires no alerts, saves nothing to the database.
    Returns live detection status so the UI can show a 'camera ready' indicator.
    """
    data     = request.get_json(silent=True) or {}
    frame_b64 = data.get("frame_data", "")
    if not frame_b64:
        return jsonify({"error": "No frame data"}), 400

    frame = _decode_frame(frame_b64)
    if frame is None:
        return jsonify({"error": "Invalid frame"}), 400

    managers = current_app.detection_managers
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_result = managers["eye"]._face_mesh.process(rgb)
    face_landmarks = (
        mp_result.multi_face_landmarks[0].landmark
        if mp_result.multi_face_landmarks else None
    )

    face_detected = face_landmarks is not None
    eye_res  = managers["eye"].detect(frame, face_landmarks=face_landmarks)
    head_res = managers["head"].detect(frame, face_landmarks=face_landmarks)

    return jsonify({
        "face_detected": face_detected,
        "eye_status":    eye_res.get("eye_status", "No_Face"),
        "direction":     head_res.get("direction", "No_Face"),
        "ready":         face_detected,
    }), 200


# ─────────────────────────────────────────────
# Start Session
# ─────────────────────────────────────────────

@monitor_bp.route("/session/start", methods=["POST"])
@jwt_required()
def start_session():
    """
    Start a new driving session for the authenticated user.
    Returns the new session ID.
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}
    frame_b64 = data.get("frame_data", "")

    # Mark any previously active sessions as ended
    active = DrivingSession.query.filter_by(user_id=user_id, is_active=True).all()
    for s in active:
        s.is_active = False
        s.end_time  = datetime.utcnow()

    session_obj = DrivingSession(user_id=user_id)
    db.session.add(session_obj)
    db.session.commit()

    # Reset all detection state
    managers = current_app.detection_managers
    managers["eye"].reset_state()
    managers["head"].reset_state()
    managers["yawn"].reset_state()
    managers["phone"].reset_state()
    managers["alert"].reset_session()

    # Apply voice alert setting from user preferences
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    if settings:
        managers["alert"].set_voice_enabled(settings.voice_alerts_enabled)

    if frame_b64:
        frame = _decode_frame(frame_b64)
        if frame is not None:
            managers["alert"].check_session_start_screenshot(frame, session_obj.id)
        else:
            logger.warning("Session start screenshot skipped because frame data was invalid.")

    return jsonify({
        "message":    "Session started.",
        "session_id": session_obj.id,
    }), 201


# ─────────────────────────────────────────────
# End Session
# ─────────────────────────────────────────────

@monitor_bp.route("/session/end", methods=["POST"])
@jwt_required()
def end_session():
    """
    End the active session, compute final scores.
    Body: { session_id }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}
    sid     = data.get("session_id")

    session_obj = DrivingSession.query.filter_by(id=sid, user_id=user_id).first()
    if not session_obj:
        return jsonify({"error": "Session not found."}), 404

    managers = current_app.detection_managers

    # Compute final scores from the alert manager's rolling history
    alert_count = managers["alert"].get_alert_count()

    session_obj.end_time  = datetime.utcnow()
    session_obj.is_active = False
    session_obj.duration_seconds = (
        session_obj.end_time - session_obj.start_time
    ).total_seconds()
    session_obj.total_alerts = alert_count

    # Count events from saved alerts
    session_alerts = Alert.query.filter_by(session_id=sid).all()
    session_obj.eye_closure_count  = sum(1 for a in session_alerts if a.alert_type == "drowsiness")
    session_obj.yawn_count         = sum(1 for a in session_alerts if a.alert_type == "yawn_detected")
    session_obj.phone_usage_count  = sum(1 for a in session_alerts if a.alert_type == "phone_detected")

    db.session.commit()

    return jsonify({
        "message": "Session ended.",
        "session": session_obj.to_dict(),
    }), 200


# ─────────────────────────────────────────────
# Process Frame
# ─────────────────────────────────────────────

@monitor_bp.route("/frame", methods=["POST"])
@jwt_required()
def process_frame():
    """
    Process a single webcam frame for all detections.

    Body: {
        frame_data: str,       # base64-encoded JPEG
        session_id: int
    }

    Returns:
        {
          eye:    { eye_status, confidence, closed_duration, drowsy_alert }
          head:   { direction, yaw, pitch, distraction_duration, distraction_alert }
          yawn:   { mar, is_yawning, yawn_alert, total_yawns }
          phone:  { phone_detected, phone_count, detections, phone_alert }
          safety_score:    float
          attention_score: float
          alerts_fired:    list[str]
        }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}

    frame_b64  = data.get("frame_data", "")
    session_id = data.get("session_id")

    if not frame_b64:
        return jsonify({"error": "frame_data is required."}), 400

    if not session_id:
        return jsonify({"error": "Active session is required."}), 400

    session_obj = DrivingSession.query.filter_by(id=session_id, user_id=user_id, is_active=True).first()
    if not session_obj:
        return jsonify({"error": "No active session found."}), 400

    frame = _decode_frame(frame_b64)
    if frame is None:
        return jsonify({"error": "Invalid frame data."}), 400

    managers = current_app.detection_managers

    # ── Capture session start baseline screenshot if first frame ──
    managers["alert"].check_session_start_screenshot(frame, session_id or 0)

    # ── Single-pass Face Mesh extraction ──────────
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_result = managers["eye"]._face_mesh.process(rgb)
    face_landmarks = (
        mp_result.multi_face_landmarks[0].landmark
        if mp_result.multi_face_landmarks else None
    )

    # ── Run all detectors ──────────────────────
    eye_res   = managers["eye"].detect(frame, face_landmarks=face_landmarks)
    head_res  = managers["head"].detect(frame, face_landmarks=face_landmarks)
    yawn_res  = managers["yawn"].detect(frame, face_landmarks=face_landmarks)
    phone_res = managers["phone"].detect(frame)

    # ── Compute scores ─────────────────────────
    safety, attention = managers["alert"].compute_scores(
        eye_res, head_res, yawn_res, phone_res
    )

    # ── Fire alerts if needed ──────────────────
    alerts_fired = []

    # 1. Drowsiness / Eyes Closed Alert
    is_drowsy = bool(eye_res.get("drowsy_alert"))
    if is_drowsy:
        managers["alert"].mark_still_active("drowsiness")
        alert_data = managers["alert"].fire_alert(
            "drowsiness", frame, session_id or 0,
            extra={"eye_status": eye_res.get("eye_status"),
                   "confidence": eye_res.get("confidence", 0)}
        )
        if alert_data:
            alerts_fired.append(alert_data)
            if user_id and session_id:
                _save_alert(user_id, session_id, alert_data, eye_res, head_res)
    else:
        managers["alert"].clear_active_alert("drowsiness")

    # 2. Head Distraction Alert
    # The head pose detector uses a smart 3-second sustained threshold:
    # brief glances (mirror checks, shoulder checks, turns) are normal driving
    # and do NOT trigger this alert. Only sustained non-forward gaze does.
    is_distracted = head_res.get("distraction_alert", False)
    if is_distracted:
        managers["alert"].mark_still_active("distraction")
        alert_data = managers["alert"].fire_alert(
            "distraction", frame, session_id or 0,
            extra={"head_pose": head_res.get("direction")}
        )
        if alert_data:
            alerts_fired.append(alert_data)
            if user_id and session_id:
                _save_alert(user_id, session_id, alert_data, eye_res, head_res)
    else:
        managers["alert"].clear_active_alert("distraction")

    # 3. Mobile Phone Detection Alert
    is_phone = phone_res.get("phone_alert") or (
        phone_res.get("phone_detected") and phone_res.get("phone_duration", 0) >= 1.0
    )
    if is_phone:
        managers["alert"].mark_still_active("phone_detected")
        alert_data = managers["alert"].fire_alert(
            "phone_detected", frame, session_id or 0,
        )
        if alert_data:
            alerts_fired.append(alert_data)
            if user_id and session_id:
                _save_alert(user_id, session_id, alert_data, eye_res, head_res)
    else:
        managers["alert"].clear_active_alert("phone_detected")

    # 4. Yawn Alert
    is_yawn = yawn_res.get("yawn_alert")
    if is_yawn:
        managers["alert"].mark_still_active("yawn_detected")
        alert_data = managers["alert"].fire_alert(
            "yawn_detected", frame, session_id or 0,
        )
        if alert_data:
            alerts_fired.append(alert_data)
            if user_id and session_id:
                _save_alert(user_id, session_id, alert_data, eye_res, head_res)
    else:
        managers["alert"].clear_active_alert("yawn_detected")

    # ── Update session scores live ─────────────
    if session_id:
        session_obj = DrivingSession.query.get(session_id)
        if session_obj and session_obj.is_active:
            session_obj.safety_score    = safety
            session_obj.attention_score = attention
            db.session.commit()

    # ── Calculate face bounding box from landmarks or Haar Cascade ──────
    face_bbox = None
    if face_landmarks:
        xs = [lm.x for lm in face_landmarks]
        ys = [lm.y for lm in face_landmarks]
        xmin, xmax = min(xs), max(xs)
        ymin, ymax = min(ys), max(ys)
        pad_x = (xmax - xmin) * 0.10
        pad_y = (ymax - ymin) * 0.15
        face_bbox = {
            "x": max(0.0, round(xmin - pad_x, 4)),
            "y": max(0.0, round(ymin - pad_y, 4)),
            "width": min(1.0, round((xmax - xmin) + 2 * pad_x, 4)),
            "height": min(1.0, round((ymax - ymin) + 2 * pad_y, 4))
        }
    else:
        # Fallback to OpenCV Haar Cascade if MediaPipe landmarks unavailable
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            face_cascade = cv2.CascadeClassifier(cascade_path)
            if not face_cascade.empty():
                faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(30, 30))
                if len(faces) > 0:
                    h_img, w_img = frame.shape[:2]
                    fx, fy, fw, fh = faces[0]
                    face_bbox = {
                        "x": round(float(fx) / w_img, 4),
                        "y": round(float(fy) / h_img, 4),
                        "width": round(float(fw) / w_img, 4),
                        "height": round(float(fh) / h_img, 4)
                    }
        except Exception:
            face_bbox = None

    return jsonify({
        "eye":                  eye_res,
        "head":                 head_res,
        "yawn":                 yawn_res,
        "phone":                phone_res,
        "eye_status":           eye_res,
        "head_pose":            head_res,
        "yawn_status":          yawn_res,
        "phone_status":         phone_res,
        "face_bbox":            face_bbox,
        "safety_score":         safety,
        "attention_score":      attention,
        "alerts_fired":         alerts_fired,
    }), 200


# ─────────────────────────────────────────────
# Save Alert (internal helper)
# ─────────────────────────────────────────────

def _save_alert(user_id: int, session_id: int, alert_data: dict,
                eye_res: dict, head_res: dict) -> None:
    """Persist an alert record to the database."""
    try:
        alert = Alert(
            session_id      = session_id,
            user_id         = user_id,
            alert_type      = alert_data["alert_type"],
            severity        = alert_data["severity"],
            message         = alert_data["message"],
            screenshot_path = alert_data.get("screenshot_path"),
            eye_status      = eye_res.get("eye_status"),
            head_pose       = head_res.get("direction"),
            confidence      = alert_data.get("confidence"),
        )
        db.session.add(alert)
        db.session.commit()
    except Exception as exc:
        logger.error(f"Alert save error: {exc}")
        db.session.rollback()


# ─────────────────────────────────────────────
# Manual Alert (POST /api/monitor/alert)
# ─────────────────────────────────────────────

@monitor_bp.route("/alert", methods=["POST"])
@jwt_required()
def save_alert():
    """
    Manually save an alert (e.g., client-side detected event).
    Body: { session_id, alert_type, message?, severity? }
    """
    user_id = int(get_jwt_identity())
    data    = request.get_json(silent=True) or {}

    session_id = data.get("session_id")
    alert_type = data.get("alert_type", "unknown")
    message    = data.get("message", "")
    severity   = data.get("severity", "warning")

    alert = Alert(
        session_id = session_id,
        user_id    = user_id,
        alert_type = alert_type,
        message    = message,
        severity   = severity,
    )
    db.session.add(alert)
    db.session.commit()

    return jsonify({
        "message": "Alert saved.",
        "alert":   alert.to_dict(),
    }), 201
