"""
DriveSafe AI — Authentication Routes
======================================
Endpoints:
  POST /api/auth/register   — create account
  POST /api/auth/login      — get JWT token
  POST /api/auth/logout     — invalidate token (client-side)
  GET  /api/auth/profile    — get current user profile
  PUT  /api/auth/profile    — update profile
"""

from flask              import Blueprint, request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity
)

from extensions          import db
from models.user         import User, UserSettings

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


# ─────────────────────────────────────────────
# Register
# ─────────────────────────────────────────────

@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user.
    Body: { username, email, password, full_name? }
    """
    data = request.get_json(silent=True) or {}

    username  = data.get("username",  "").strip()
    email     = data.get("email",     "").strip().lower()
    password  = data.get("password",  "")
    full_name = data.get("full_name", "").strip()

    # Validation
    if not username or not email or not password:
        return jsonify({"error": "username, email, and password are required."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already taken."}), 409

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already registered."}), 409

    # Create user
    user = User(username=username, email=email, full_name=full_name)
    user.set_password(password)
    db.session.add(user)
    db.session.flush()  # get user.id before commit

    # Create default settings
    settings = UserSettings(user_id=user.id)
    db.session.add(settings)
    db.session.commit()
    # Issue tokens
    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message":       "Registration successful.",
        "user":          user.to_dict(),
        "access_token":  access_token,
        "refresh_token": refresh_token,
    }), 201


# ─────────────────────────────────────────────
# Login
# ─────────────────────────────────────────────

@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login with username or email + password.
    Body: { username_or_email, password }
    """
    data     = request.get_json(silent=True) or {}
    identity = data.get("username_or_email", "").strip()
    password = data.get("password", "")

    if not identity or not password:
        return jsonify({"error": "username/email and password required."}), 400

    # Find user by username or email
    user = (User.query.filter_by(username=identity).first() or
            User.query.filter_by(email=identity.lower()).first())

    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid credentials."}), 401

    access_token  = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message":       "Login successful.",
        "user":          user.to_dict(),
        "access_token":  access_token,
        "refresh_token": refresh_token,
    }), 200


# ─────────────────────────────────────────────
# Logout (client-side token discard)
# ─────────────────────────────────────────────

@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    """
    Logout endpoint. Tokens are stateless (JWT), so the client
    simply discards the token. This endpoint provides a proper API
    contract and can be extended with a token blocklist if needed.
    """
    return jsonify({"message": "Logged out successfully."}), 200


# ─────────────────────────────────────────────
# Profile — GET
# ─────────────────────────────────────────────

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def get_profile():
    """Return current authenticated user's profile."""
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    return jsonify({"user": user.to_dict()}), 200


# ─────────────────────────────────────────────
# Profile — PUT
# ─────────────────────────────────────────────

@auth_bp.route("/profile", methods=["PUT"])
@jwt_required()
def update_profile():
    """
    Update user profile.
    Body: { full_name?, email?, current_password?, new_password? }
    """
    user_id = int(get_jwt_identity())
    user    = User.query.get_or_404(user_id)
    data    = request.get_json(silent=True) or {}

    # Update full_name
    if "full_name" in data:
        user.full_name = data["full_name"].strip()

    # Update email
    if "email" in data:
        new_email = data["email"].strip().lower()
        existing  = User.query.filter_by(email=new_email).first()
        if existing and existing.id != user.id:
            return jsonify({"error": "Email already in use."}), 409
        user.email = new_email

    # Update password
    if "new_password" in data:
        current = data.get("current_password", "")
        if not user.check_password(current):
            return jsonify({"error": "Current password is incorrect."}), 401
        if len(data["new_password"]) < 6:
            return jsonify({"error": "New password must be at least 6 characters."}), 400
        user.set_password(data["new_password"])

    db.session.commit()
    return jsonify({
        "message": "Profile updated.",
        "user":    user.to_dict(),
    }), 200
