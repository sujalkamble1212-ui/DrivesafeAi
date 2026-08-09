"""
DriveSafe AI — Head Pose Estimator
=====================================
Uses MediaPipe Face Mesh + solvePnP to estimate 3D head pose
(yaw, pitch, roll) and classify the driver's gaze direction.

Directions:
  Looking Left / Right / Up / Down / Forward
"""

import time
import logging
import numpy as np
import cv2
import mediapipe as mp

from config import DetectionConfig

logger = logging.getLogger(__name__)


class HeadPoseDetector:
    """
    Estimates head pose from face landmarks using a 3D face model
    and OpenCV's solvePnP solver.
    """

    # 3D model points for a generic face (in mm)
    MODEL_POINTS = np.array([
        (  0.0,    0.0,    0.0),   # Nose tip        — landmark 1
        (  0.0, -330.0,  -65.0),   # Chin            — landmark 8
        (-225.0,  170.0, -135.0),  # Left eye corner — landmark 36
        ( 225.0,  170.0, -135.0),  # Right eye corner— landmark 45
        (-150.0, -150.0, -125.0),  # Left mouth      — landmark 48
        ( 150.0, -150.0, -125.0),  # Right mouth     — landmark 54
    ], dtype=np.float64)

    # Corresponding MediaPipe Face Mesh landmark indices
    LANDMARK_INDICES = [1, 152, 33, 263, 61, 291]

    def __init__(self):
        self._mp_face_mesh = mp.solutions.face_mesh
        self._face_mesh    = self._mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4,
        )

        # State tracking for distraction timing
        self._distracted_start:    float | None = None
        self._forward_return_time: float | None = None   # tracks when driver returns to forward gaze
        self._distraction_duration: float       = 0.0

    # ──────────────────────────────────────────────
    # Pose Estimation
    # ──────────────────────────────────────────────

    def _get_image_points(self, landmarks, h: int, w: int) -> np.ndarray:
        """Extract 2D pixel coordinates for the 6 landmark points."""
        pts = []
        for idx in self.LANDMARK_INDICES:
            lm = landmarks[idx]
            pts.append((lm.x * w, lm.y * h))
        return np.array(pts, dtype=np.float64)

    def _build_camera_matrix(self, h: int, w: int) -> np.ndarray:
        """Build a simple camera intrinsic matrix from image size."""
        focal_length = w
        cx, cy       = w / 2.0, h / 2.0
        return np.array([
            [focal_length, 0,            cx],
            [0,            focal_length, cy],
            [0,            0,            1 ],
        ], dtype=np.float64)

    def _classify_direction(self, yaw: float, pitch: float) -> str:
        """Map yaw/pitch angles (degrees) to human-readable direction."""
        y_thresh = DetectionConfig.HEAD_YAW_THRESHOLD
        p_thresh = DetectionConfig.HEAD_PITCH_THRESHOLD

        if yaw < -y_thresh:
            return "Looking_Left"
        elif yaw > y_thresh:
            return "Looking_Right"
        elif pitch < -p_thresh:
            return "Looking_Down"
        elif pitch > p_thresh:
            return "Looking_Up"
        else:
            return "Looking_Forward"

    # ──────────────────────────────────────────────
    # Main Detection
    # ──────────────────────────────────────────────

    def detect(self, frame: np.ndarray, face_landmarks=None) -> dict:
        """
        Process a BGR frame and return head pose information.

        Real-world driving involves frequent brief head movements for mirror
        checks, shoulder checks, and intersection turns. This detector uses
        a 3-second sustained threshold to distinguish genuine distraction
        from normal driving glances.

        Returns dict:
            direction           : str  (e.g. "Looking_Left")
            yaw                 : float (degrees)
            pitch               : float (degrees)
            roll                : float (degrees)
            distraction_duration: float (seconds of current sustained look-away)
            distraction_alert   : bool  (True only after 3s continuous non-forward)
            is_glancing         : bool  (True during brief normal glance < 3s)
        """
        result = {
            "direction":             "Unknown",
            "yaw":                   0.0,
            "pitch":                 0.0,
            "roll":                  0.0,
            "distraction_duration":  0.0,
            "distraction_alert":     False,
            "is_glancing":           False,
        }

        h, w = frame.shape[:2]

        if face_landmarks is None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_result = self._face_mesh.process(rgb)
            if mp_result.multi_face_landmarks:
                face_landmarks = mp_result.multi_face_landmarks[0].landmark

        if not face_landmarks:
            self._distracted_start    = None
            self._forward_return_time = None
            self._distraction_duration = 0.0
            result["direction"] = "No_Face"
            return result

        image_points = self._get_image_points(face_landmarks, h, w)
        camera_mat   = self._build_camera_matrix(h, w)
        dist_coeffs  = np.zeros((4, 1))

        success, rot_vec, _ = cv2.solvePnP(
            self.MODEL_POINTS,
            image_points,
            camera_mat,
            dist_coeffs,
            flags=cv2.SOLVEPNP_SQPNP,
        )

        if not success:
            return result

        # Convert rotation vector → Euler angles (degrees)
        rot_mat, _ = cv2.Rodrigues(rot_vec)
        proj_mat   = np.hstack([rot_mat, np.zeros((3, 1))])
        _, _, _, _, _, _, euler = cv2.decomposeProjectionMatrix(proj_mat)

        pitch = float(euler[0])
        yaw   = float(euler[1])
        roll  = float(euler[2])

        direction = self._classify_direction(yaw, pitch)

        result.update({
            "direction": direction,
            "yaw":       round(yaw,   2),
            "pitch":     round(pitch, 2),
            "roll":      round(roll,  2),
        })

        # ── Smart Distraction Timer ───────────────────────────────────────
        # Real driving requires frequent brief head turns (mirrors, turns).
        # We only fire an alert when the driver looks away CONTINUOUSLY for
        # HEAD_DISTRACTION_SECONDS (3s). A brief return to forward gaze of
        # less than HEAD_GLANCE_FORGIVENESS (1s) does NOT reset the timer —
        # this handles natural scanning patterns at intersections.
        now           = time.time()
        is_distracted = (direction != "Looking_Forward")

        if is_distracted:
            # Cancel any pending forgiveness window
            self._forward_return_time = None

            if self._distracted_start is None:
                self._distracted_start = now
            self._distraction_duration = now - self._distracted_start

        else:
            # Driver is looking forward — start a forgiveness window.
            # Only reset the distraction timer once they stay forward
            # for longer than HEAD_GLANCE_FORGIVENESS.
            if self._forward_return_time is None:
                self._forward_return_time = now

            forward_for = now - self._forward_return_time
            if forward_for >= DetectionConfig.HEAD_GLANCE_FORGIVENESS:
                # Truly back to forward — reset timer
                self._distracted_start    = None
                self._distraction_duration = 0.0
            # If still within forgiveness window, keep accumulated duration

        result["distraction_duration"] = round(self._distraction_duration, 2)

        # Brief glances under the alert threshold are normal driving
        if is_distracted and self._distraction_duration < DetectionConfig.HEAD_DISTRACTION_SECONDS:
            result["is_glancing"] = True

        if self._distraction_duration >= DetectionConfig.HEAD_DISTRACTION_SECONDS:
            result["distraction_alert"] = True

        return result

    def reset_state(self) -> None:
        """Reset distraction timer."""
        self._distracted_start     = None
        self._forward_return_time  = None
        self._distraction_duration = 0.0

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self._face_mesh:
            self._face_mesh.close()
