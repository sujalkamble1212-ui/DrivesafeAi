"""
DriveSafe AI — Main Flask Application Entry Point
==================================================
Initializes Flask app, MongoDB, JWT, CORS, blueprints,
and AI detection managers. In production (Hugging Face Spaces)
Flask also serves the pre-built React frontend.
"""

import os
import logging
from flask import Flask, send_from_directory, send_file
from flask_cors import CORS

from config import Config, SCREENSHOTS_DIR
from extensions import init_db, jwt
from routes.auth import auth_bp
from routes.monitoring import monitor_bp
from routes.sessions import sessions_bp
from routes.alerts import alerts_bp
from routes.reports import reports_bp
from routes.settings import settings_bp
from routes.screenshots import screenshots_bp

from detection.eye_detection import EyeDetector
from detection.head_pose import HeadPoseDetector
from detection.yawn_detection import YawnDetector
from detection.phone_detection import PhoneDetector
from detection.alert_manager import AlertManager

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Path to the pre-built React frontend
# (populated by Dockerfile COPY step)
# ─────────────────────────────────────────────
BASE_DIR         = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR     = os.path.join(BASE_DIR, "static_frontend")
SERVE_FRONTEND   = os.path.isdir(FRONTEND_DIR)   # True inside Docker container


def create_app():
    app = Flask(
        __name__,
        static_folder=FRONTEND_DIR if SERVE_FRONTEND else None,
        static_url_path=""
    )
    app.config.from_object(Config)

    # Initialize Extensions
    init_db(app)
    jwt.init_app(app)
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

    # Register API Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)
    app.register_blueprint(screenshots_bp)

    # Serve screenshots
    @app.route("/screenshots/<path:filename>")
    def serve_screenshot(filename):
        return send_from_directory(SCREENSHOTS_DIR, filename)

    # ── Serve React SPA (production / Hugging Face only) ──────────────────
    if SERVE_FRONTEND:
        @app.route("/", defaults={"path": ""})
        @app.route("/<path:path>")
        def serve_react(path):
            """
            Catch-all: serve React SPA files.
            API routes are registered before this catch-all so they take priority.
            """
            target = os.path.join(FRONTEND_DIR, path)
            if path and os.path.isfile(target):
                return send_from_directory(FRONTEND_DIR, path)
            # Fallback to index.html for client-side routing
            return send_file(os.path.join(FRONTEND_DIR, "index.html"))
        logger.info("📦 Serving React frontend from %s", FRONTEND_DIR)

    logger.info("Initializing AI Detection Models...")
    eye_detector   = EyeDetector()
    head_detector  = HeadPoseDetector()
    yawn_detector  = YawnDetector()
    phone_detector = PhoneDetector()
    alert_manager  = AlertManager()

    app.detection_managers = {
        "eye":   eye_detector,
        "head":  head_detector,
        "yawn":  yawn_detector,
        "phone": phone_detector,
        "alert": alert_manager,
    }
    logger.info("✅ All AI Detection Models initialized.")

    return app


app = create_app()

if __name__ == "__main__":
    logger.info("🚀 Starting DriveSafe AI Flask Server on port 5000...")
    app.run(host="0.0.0.0", port=5000, debug=Config.DEBUG)
