"""
DriveSafe AI — Mobile Phone Detector
======================================
Uses YOLOv8n (pretrained on COCO) to detect mobile phones in a frame.
Only the "cell phone" class (COCO class ID = 67) is reported.
"""

import time
import logging
import numpy as np
import cv2

from config import DetectionConfig

logger = logging.getLogger(__name__)


class PhoneDetector:
    """
    Detects mobile phones in video frames using YOLOv8n.
    The YOLO model is loaded lazily on first call to avoid slowing
    Flask startup (the model file may need to be downloaded).
    """

    PHONE_CLASS_ID   = DetectionConfig.PHONE_CLASS_ID    # 67 in COCO
    PHONE_CLASS_NAME = "cell phone"

    def __init__(self):
        self._model             = None
        self._phone_start: float | None = None
        self._phone_duration: float     = 0.0
        self._total_phone_detections: int = 0

    # ──────────────────────────────────────────────
    # Lazy Model Loading
    # ──────────────────────────────────────────────

    def _load_model(self) -> None:
        """Load YOLOv8n model (downloads yolov8n.pt on first run)."""
        if self._model is not None:
            return
        try:
            from ultralytics import YOLO
            self._model = YOLO("yolov8n.pt")
            logger.info("✅ YOLOv8n loaded successfully.")
        except Exception as exc:
            logger.error(f"❌ Failed to load YOLO model: {exc}")
            raise

    # ──────────────────────────────────────────────
    # Detection
    # ──────────────────────────────────────────────

    def detect(self, frame: np.ndarray) -> dict:
        """
        Run phone detection on a BGR frame.

        Returns dict:
            phone_detected       : bool
            phone_count          : int  (phones in frame)
            detections           : list[dict] with bbox, confidence
            phone_duration       : float (seconds phone has been visible)
            phone_alert          : bool (visible > PHONE_ALERT_SECONDS)
            total_phone_detections: int (lifetime count)
        """
        self._load_model()

        result = {
            "phone_detected":        False,
            "phone_count":           0,
            "detections":            [],
            "phone_duration":        0.0,
            "phone_alert":           False,
            "total_phone_detections": self._total_phone_detections,
        }

        try:
            # Run YOLO inference with 320x320 input size for ultra-fast performance (~15ms)
            yolo_results = self._model(
                frame,
                imgsz=320,
                conf=0.30,
                classes=[self.PHONE_CLASS_ID],
                verbose=False,
            )
        except Exception as exc:
            logger.warning(f"YOLO inference error: {exc}")
            return result

        phones_found = []
        for r in yolo_results:
            if r.boxes is None:
                continue
            for box in r.boxes:
                cls_id = int(box.cls[0])
                if cls_id != self.PHONE_CLASS_ID:
                    continue
                conf = float(box.conf[0])
                xyxy = box.xyxy[0].tolist()   # [x1, y1, x2, y2]
                phones_found.append({
                    "confidence": round(conf, 3),
                    "bbox":       [round(v) for v in xyxy],
                    "class_name": self.PHONE_CLASS_NAME,
                })

        phone_detected = len(phones_found) > 0
        result["phone_detected"] = phone_detected
        result["phone_count"]    = len(phones_found)
        result["detections"]     = phones_found

        # ── Duration Timer ────────────────────────
        now = time.time()
        if phone_detected:
            if self._phone_start is None:
                self._phone_start = now
                self._total_phone_detections += 1
            self._phone_duration = now - self._phone_start
        else:
            self._phone_start    = None
            self._phone_duration = 0.0

        result["phone_duration"] = self._phone_duration
        result["total_phone_detections"] = self._total_phone_detections

        if self._phone_duration >= DetectionConfig.PHONE_ALERT_SECONDS:
            result["phone_alert"] = True

        return result

    def reset_state(self) -> None:
        """Reset phone detection counters."""
        self._phone_start             = None
        self._phone_duration          = 0.0
        self._total_phone_detections  = 0

    def get_total_detections(self) -> int:
        return self._total_phone_detections
