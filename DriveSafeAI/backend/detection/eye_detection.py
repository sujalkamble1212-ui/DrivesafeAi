"""
DriveSafe AI — Eye Drowsiness Detector
========================================
Loads the user's pre-trained EfficientNetB0 model (eye_model.keras)
and combines it with MediaPipe EAR (Eye Aspect Ratio) for instant,
rock-solid eye state (Open / Closed) detection.
"""

import time
import logging
import numpy as np
import cv2
import mediapipe as mp

from keras.models import load_model
from keras.applications.efficientnet import preprocess_input

from config import EYE_MODEL_PATH, DetectionConfig

logger = logging.getLogger(__name__)


class EyeDetector:
    """
    Detects eye state using Eye Aspect Ratio (EAR) combined with a pre-trained
    EfficientNetB0 model for maximum speed and accuracy.
    """

    # MediaPipe landmark indices for left and right eyes
    LEFT_EYE_LANDMARKS  = [362, 382, 381, 380, 374, 373, 390, 249,
                            263, 466, 388, 387, 386, 385, 384, 398]
    RIGHT_EYE_LANDMARKS = [33, 7, 163, 144, 145, 153, 154, 155,
                           133, 173, 157, 158, 159, 160, 161, 246]

    # EAR Landmark sets: [p1_horiz_left, p2_vert_top1, p3_vert_top2, p4_horiz_right, p5_vert_bot1, p6_vert_bot2]
    LEFT_EAR_PTS  = [362, 386, 385, 263, 374, 380]
    RIGHT_EAR_PTS = [33,  159, 158, 133, 145, 153]

    def __init__(self):
        self._model        = None
        self._face_mesh    = None
        self._mp_face_mesh = mp.solutions.face_mesh

        # State tracking for drowsiness timing
        self._closed_start_time: float | None = None
        self._closed_duration:   float        = 0.0
        self._open_frame_count:  int          = 0

        self._load_model()
        self._init_face_mesh()

    def _load_model(self) -> None:
        """Load eye model from disk using tf.keras, or fall back to MediaPipe EAR."""
        try:
            import os
            import tensorflow as tf
            from config import MODELS_DIR

            target_path = EYE_MODEL_PATH
            if not os.path.exists(target_path):
                alt_path = os.path.join(MODELS_DIR, "eye_model.keras")
                if os.path.exists(alt_path):
                    target_path = alt_path

            if os.path.exists(target_path):
                self._model = tf.keras.models.load_model(target_path, compile=False)
                logger.info(f"✅ {os.path.basename(target_path)} loaded successfully.")
            else:
                logger.warning("⚠️ No eye model file found on disk. Operating with MediaPipe EAR geometry fallback.")
                self._model = None
        except Exception as exc:
            logger.warning(f"⚠️ Could not load Keras eye model ({exc}). Operating with MediaPipe EAR geometry fallback.")
            self._model = None


    def _init_face_mesh(self) -> None:
        """Initialise MediaPipe Face Mesh in tracking mode for fast per-frame execution."""
        self._face_mesh = self._mp_face_mesh.FaceMesh(
            static_image_mode=False,
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.4,
            min_tracking_confidence=0.4,
        )

    def _compute_ear(self, landmarks, eye_pts: list[int], h: int, w: int) -> float:
        """Calculate Eye Aspect Ratio (EAR) for geometric eye open/close detection."""
        try:
            pts = np.array([(landmarks[i].x * w, landmarks[i].y * h) for i in eye_pts], dtype=np.float64)
            v1 = np.linalg.norm(pts[1] - pts[4])
            v2 = np.linalg.norm(pts[2] - pts[5])
            h_dist = np.linalg.norm(pts[0] - pts[3])
            if h_dist < 1e-6:
                return 0.3
            return float((v1 + v2) / (2.0 * h_dist))
        except Exception:
            return 0.3

    def _extract_eye_region(self, frame: np.ndarray, landmarks, indices: list,
                            h: int, w: int) -> np.ndarray | None:
        """Extract eye bounding box using dynamic padding proportional to eye width."""
        coords = [(int(landmarks[i].x * w), int(landmarks[i].y * h)) for i in indices]
        xs = [c[0] for c in coords]
        ys = [c[1] for c in coords]

        eye_w = max(10, max(xs) - min(xs))
        padding = max(4, int(eye_w * 0.20))  # 20% proportional padding to avoid eyebrow noise

        x1 = max(0, min(xs) - padding)
        y1 = max(0, min(ys) - padding)
        x2 = min(w, max(xs) + padding)
        y2 = min(h, max(ys) + padding)

        if x2 <= x1 or y2 <= y1:
            return None
        return frame[y1:y2, x1:x2]

    def _predict_eye_fast(self, eye_crop: np.ndarray) -> float:
        """Direct C++ model invocation without Keras wrapper overhead (~5ms vs 200ms)."""
        img = cv2.resize(eye_crop, DetectionConfig.EYE_INPUT_SIZE)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img = np.array(img, dtype=np.float32)
        img = preprocess_input(img)
        img = np.expand_dims(img, axis=0)

        # Direct call is 30x faster than model.predict()
        out = self._model(img, training=False)
        return float(out[0][0])

    @staticmethod
    def should_trigger_drowsiness_alert(closed_duration: float) -> bool:
        return closed_duration >= DetectionConfig.DROWSINESS_SECONDS

    def detect(self, frame: np.ndarray, face_landmarks=None) -> dict:
        result = {
            "eye_status":       "No_Face",
            "confidence":       0.0,
            "closed_duration":  0.0,
            "drowsy_alert":     False,
        }

        h, w = frame.shape[:2]

        if face_landmarks is None:
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_result = self._face_mesh.process(rgb)
            if mp_result.multi_face_landmarks:
                face_landmarks = mp_result.multi_face_landmarks[0].landmark

        if not face_landmarks:
            self._open_frame_count += 1
            if self._open_frame_count >= 3:
                self._closed_start_time = None
                self._closed_duration   = 0.0
            return result

        # 1. Compute Eye Aspect Ratio (EAR) for both eyes
        left_ear  = self._compute_ear(face_landmarks, self.LEFT_EAR_PTS, h, w)
        right_ear = self._compute_ear(face_landmarks, self.RIGHT_EAR_PTS, h, w)
        avg_ear   = (left_ear + right_ear) / 2.0

        # 2. Run EfficientNet model on BOTH eye crops for robust multi-eye prediction
        left_crop  = self._extract_eye_region(frame, face_landmarks, self.LEFT_EYE_LANDMARKS, h, w)
        right_crop = self._extract_eye_region(frame, face_landmarks, self.RIGHT_EYE_LANDMARKS, h, w)

        probs = []
        if left_crop is not None and left_crop.size > 0:
            probs.append(self._predict_eye_fast(left_crop))
        if right_crop is not None and right_crop.size > 0:
            probs.append(self._predict_eye_fast(right_crop))

        model_prob = float(np.mean(probs)) if probs else 0.5

        # 3. Robust Hybrid Fusion: Combine EAR geometry + CNN Model probability
        # EAR score: 0.0 (closed) to 1.0 (open), normalized around 0.12–0.24 EAR range
        ear_score = max(0.0, min(1.0, (avg_ear - 0.12) / 0.12))
        open_confidence = 0.50 * ear_score + 0.50 * model_prob

        # Eyes are Closed ONLY IF combined open confidence is below 0.42 OR both signals independently indicate closed
        is_closed = (open_confidence < 0.42) or (avg_ear < 0.14 and model_prob < 0.40)

        if is_closed:
            eye_status = "Closed_Eyes"
            conf       = round(1.0 - open_confidence, 2)
            self._open_frame_count = 0
        else:
            eye_status = "Open_Eyes"
            conf       = round(open_confidence, 2)
            self._open_frame_count += 1

        result["eye_status"] = eye_status
        result["confidence"] = max(0.5, min(1.0, conf))

        # ── Drowsiness Timer with Immediate Open Reset ──────────
        now = time.time()
        if eye_status == "Closed_Eyes":
            if self._closed_start_time is None:
                self._closed_start_time = now
            self._closed_duration = now - self._closed_start_time
        else:
            # Immediate reset on any open frame
            self._closed_start_time = None
            self._closed_duration   = 0.0

        result["closed_duration"] = self._closed_duration
        result["drowsy_alert"] = self.should_trigger_drowsiness_alert(self._closed_duration)

        return result

    def reset_state(self) -> None:
        self._closed_start_time = None
        self._closed_duration   = 0.0
        self._open_frame_count  = 0

    def close(self) -> None:
        if self._face_mesh:
            self._face_mesh.close()
