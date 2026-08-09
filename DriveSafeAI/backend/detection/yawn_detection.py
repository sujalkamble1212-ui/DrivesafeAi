"""
DriveSafe AI — Yawn Detector
==============================
Uses MediaPipe Face Mesh to compute the Mouth Aspect Ratio (MAR)
and detect yawning.

MAR = vertical_mouth_opening / horizontal_mouth_width
If MAR > threshold for N consecutive frames → yawn detected.
"""

import logging
import numpy as np
import cv2
import mediapipe as mp

from config import DetectionConfig

logger = logging.getLogger(__name__)


class YawnDetector:
    """
    Detects yawning using Mouth Aspect Ratio (MAR) computed
    from MediaPipe Face Mesh lip landmarks.
    """

    # Outer lip landmark indices (MediaPipe Face Mesh 468 points)
    # Top lip:    13 (center upper)
    # Bottom lip: 14 (center lower)
    # Left corner:  61
    # Right corner: 291
    # Upper outer:  82, 87
    # Lower outer: 312, 317

    UPPER_LIP = [82, 13, 312]
    LOWER_LIP = [87, 14, 317]
    LEFT_LIP  = 61
    RIGHT_LIP  = 291

    def __init__(self):
        self._mp_face_mesh = mp.solutions.face_mesh
        self._face_mesh    = self._mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4,
        )
        self._yawn_frames: int  = 0
        self._total_yawns: int  = 0
        self._currently_yawning: bool = False
        self._yawn_alert_fired: bool  = False   # prevent re-firing same yawn episode

    # ──────────────────────────────────────────────
    # MAR Computation
    # ──────────────────────────────────────────────

    def _compute_mar(self, landmarks, h: int, w: int) -> float:
        """
        Compute Mouth Aspect Ratio from Face Mesh landmarks.

        MAR = mean(|upper_i − lower_i|) / |left_corner − right_corner|
        """
        def pt(idx):
            lm = landmarks[idx]
            return np.array([lm.x * w, lm.y * h], dtype=np.float64)

        # Vertical distances
        v1 = np.linalg.norm(pt(self.UPPER_LIP[0]) - pt(self.LOWER_LIP[0]))
        v2 = np.linalg.norm(pt(self.UPPER_LIP[1]) - pt(self.LOWER_LIP[1]))
        v3 = np.linalg.norm(pt(self.UPPER_LIP[2]) - pt(self.LOWER_LIP[2]))

        # Horizontal distance
        h_dist = np.linalg.norm(pt(self.LEFT_LIP) - pt(self.RIGHT_LIP))

        if h_dist < 1e-6:
            return 0.0

        mar = (v1 + v2 + v3) / (3.0 * h_dist)
        return float(mar)

    # ──────────────────────────────────────────────
    # Main Detection
    # ──────────────────────────────────────────────

    def detect(self, frame: np.ndarray, face_landmarks=None) -> dict:
        """
        Process a BGR frame and return yawn detection results.

        Returns dict:
            mar            : float  (mouth aspect ratio)
            is_yawning     : bool
            yawn_alert     : bool   (confirmed yawn event)
            total_yawns    : int
        """
        result = {
            "mar":          0.0,
            "is_yawning":   False,
            "yawn_alert":   False,
            "total_yawns":  self._total_yawns,
        }

        h, w = frame.shape[:2]

        if not face_landmarks:
            self._yawn_frames       = 0
            self._currently_yawning = False
            return result

        mar = self._compute_mar(face_landmarks, h, w)

        result["mar"] = round(mar, 4)

        if mar > DetectionConfig.MAR_THRESHOLD:
            self._yawn_frames   += 1
            result["is_yawning"] = True
        else:
            # Transition from yawning → not yawning → count the yawn
            if self._currently_yawning and self._yawn_frames >= DetectionConfig.YAWN_MIN_FRAMES:
                self._total_yawns += 1
            self._yawn_frames       = 0
            self._currently_yawning = False
            self._yawn_alert_fired  = False   # reset so next yawn episode can fire

        # Confirm yawn is in progress once enough frames have passed
        if self._yawn_frames >= DetectionConfig.YAWN_MIN_FRAMES:
            self._currently_yawning = True
            # Fire alert ONCE per confirmed yawn episode (while mouth is still open)
            if not self._yawn_alert_fired:
                result["yawn_alert"]    = True
                result["is_yawning"]    = True
                self._yawn_alert_fired  = True

        result["total_yawns"] = self._total_yawns
        return result

    def reset_state(self) -> None:
        """Reset yawn counters."""
        self._yawn_frames       = 0
        self._total_yawns       = 0
        self._currently_yawning = False
        self._yawn_alert_fired  = False

    def close(self) -> None:
        """Release MediaPipe resources."""
        if self._face_mesh:
            self._face_mesh.close()
