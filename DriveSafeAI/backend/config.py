"""
DriveSafe AI — Configuration Module
====================================
Central configuration file for Flask application settings,
database, file paths, AI model thresholds, and security.
"""

import os
from datetime import timedelta

# ─────────────────────────────────────────────
# Base Paths
# ─────────────────────────────────────────────

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SCREENSHOTS_DIR = os.path.join(BASE_DIR, "screenshots")
REPORTS_DIR     = os.path.join(BASE_DIR, "reports")
MODELS_DIR      = BASE_DIR  # eye_model.keras lives at backend root

# Ensure directories exist
os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR,     exist_ok=True)


# ─────────────────────────────────────────────
# Flask Configuration
# ─────────────────────────────────────────────

class Config:
    # Security
    SECRET_KEY          = os.environ.get("SECRET_KEY", "drivesafe-ai-super-secret-key-2024")
    JWT_SECRET_KEY      = os.environ.get("JWT_SECRET_KEY", "drivesafe-jwt-secret-2024")
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(hours=24)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Database
    MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/drivesafe_ai")
    MONGODB_DB  = os.environ.get("MONGODB_DB", "drivesafe_ai")

    # CORS
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")

    # Upload / static
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024   # 16 MB max upload

    # Debug
    DEBUG = os.environ.get("FLASK_DEBUG", "True") == "True"



# ─────────────────────────────────────────────
# AI Model Paths
# ─────────────────────────────────────────────

EYE_MODEL_PATH  = os.path.join(MODELS_DIR, "best_eye_model.keras")
LABELS_PATH     = os.path.join(MODELS_DIR, "labels.txt")
YOLO_MODEL_NAME = "yolov8n.pt"           # downloaded automatically by ultralytics

# ─────────────────────────────────────────────
# Detection Thresholds
# ─────────────────────────────────────────────

class DetectionConfig:
    # Eye detection
    EYE_INPUT_SIZE          = (224, 224)
    EYE_CLOSED_THRESHOLD    = 0.45         # sigmoid < 0.45 → closed
    DROWSINESS_SECONDS      = 2.5          # eyes closed > 2.5 sec → alert (blinks are <0.4s, ignored)

    # Head pose (in degrees)
    HEAD_YAW_THRESHOLD      = 35           # left/right look threshold (degrees)
    HEAD_PITCH_THRESHOLD    = 30           # up/down look threshold (degrees)
    HEAD_DISTRACTION_SECONDS = 1.5         # distracted > 1.5 sec → alert

    # Yawn detection (Mouth Aspect Ratio)
    MAR_THRESHOLD           = 0.6          # above this = yawning
    YAWN_MIN_FRAMES         = 10           # consecutive frames to confirm yawn

    # Phone detection
    PHONE_CONFIDENCE        = 0.35         # YOLO confidence threshold
    PHONE_CLASS_ID          = 67           # COCO class index for "cell phone"
    PHONE_ALERT_SECONDS     = 1.0          # detected > 1.0 sec → alert

    # Sensitivity multipliers (1.0 = default)
    SENSITIVITY_MULTIPLIERS = {
        "low":    1.5,
        "medium": 1.0,
        "high":   0.7,
    }

    # Scoring weights
    SAFETY_WEIGHT_EYE   = 0.40
    SAFETY_WEIGHT_HEAD  = 0.30
    SAFETY_WEIGHT_PHONE = 0.20
    SAFETY_WEIGHT_YAWN  = 0.10

    # Screenshot
    SCREENSHOT_QUALITY = 85   # JPEG quality
