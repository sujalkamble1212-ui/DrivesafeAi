"""
DriveSafe AI — Main Flask Application Entry Point
==================================================
Initializes Flask app, SQLAlchemy, JWT, CORS, blueprints,
and AI detection managers.
"""

import os
import logging
from flask import Flask, send_from_directory
from flask_cors import CORS

from config import Config, SCREENSHOTS_DIR
from extensions import init_db, jwt
from routes.auth import auth_bp
from routes.monitoring import monitor_bp
from routes.sessions import sessions_bp
from routes.alerts import alerts_bp
from routes.reports import reports_bp
from routes.settings import settings_bp

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


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Extensions
    init_db(app)
    jwt.init_app(app)
    CORS(app, origins=Config.CORS_ORIGINS, supports_credentials=True)

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(monitor_bp)
    app.register_blueprint(sessions_bp)
    app.register_blueprint(alerts_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(settings_bp)

    # Serve static screenshots route
    @app.route("/screenshots/<path:filename>")
    def serve_screenshot(filename):
        return send_from_directory(SCREENSHOTS_DIR, filename)

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
