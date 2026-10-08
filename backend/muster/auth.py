"""
Auth blueprint: register, login, token refresh, password reset, account
deletion.

Auth is stateless JWT (access + refresh tokens) instead of the original
app's session cookies, since a native/React Native client can't rely on
browser cookies. Password reset tokens are separate, short-lived,
itsdangerous-signed tokens (not JWTs) so they can't be reused as auth.
"""
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required,
)
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

from .extensions import db, limiter
from .models import User
from .validators import validate_email, validate_password, validate_username

auth_bp = Blueprint("auth", __name__)


def _reset_serializer():
    return URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"], salt="password-reset"
    )


def _issue_tokens(user):
    identity = str(user.id)
    return {
        "access_token": create_access_token(identity=identity),
        "refresh_token": create_refresh_token(identity=identity),
        "user": user.to_public_dict(),
    }


@auth_bp.route("/register", methods=["POST"])
@limiter.limit("10 per minute")
def register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    for error in (
        validate_username(username),
        validate_email(email),
        validate_password(password),
    ):
        if error:
            return jsonify({"error": error}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "That username is already taken."}), 409
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "An account with that email already exists."}), 409

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify(_issue_tokens(user)), 201


@auth_bp.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""

    user = User.query.filter_by(username=username).first()
    if user is None or not user.check_password(password):
        # Deliberately identical message/status for "no such user" and
        # "wrong password" so login can't be used to enumerate usernames.
        return jsonify({"error": "Incorrect username or password."}), 401

    return jsonify(_issue_tokens(user)), 200


@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    return jsonify({"access_token": create_access_token(identity=identity)}), 200


@auth_bp.route("/forgot-password", methods=["POST"])
@limiter.limit("5 per minute")
def forgot_password():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    user = User.query.filter_by(email=email).first()

    # Always return 200 with the same message whether or not the email
    # exists, so this endpoint can't be used to enumerate accounts.
    response = {"message": "If that email has an account, a reset link has been sent."}

    if user:
        token = _reset_serializer().dumps({"uid": user.id})
        if current_app.config["EMAIL_SENDING_CONFIGURED"]:
            # TODO: wire up a real transactional email provider (SES,
            # SendGrid, Postmark, ...) here and send a deep link containing
            # `token` instead of returning/logging it.
            current_app.logger.info("Password reset requested for user %s", user.id)
        else:
            # No email provider configured yet — surface the token directly
            # so the reset flow is usable in dev/staging. Do NOT ship this
            # branch to production; set EMAIL_BACKEND and remove it first.
            current_app.logger.warning(
                "EMAIL_BACKEND not configured; returning reset token in API "
                "response for user %s instead of emailing it.", user.id
            )
            response["dev_reset_token"] = token

    return jsonify(response), 200


@auth_bp.route("/reset-password", methods=["POST"])
@limiter.limit("10 per minute")
def reset_password():
    data = request.get_json(silent=True) or {}
    token = data.get("token") or ""
    new_password = data.get("password") or ""

    error = validate_password(new_password)
    if error:
        return jsonify({"error": error}), 400

    try:
        payload = _reset_serializer().loads(
            token, max_age=current_app.config["PASSWORD_RESET_MAX_AGE"]
        )
    except SignatureExpired:
        return jsonify({"error": "This reset link has expired. Request a new one."}), 400
    except BadSignature:
        return jsonify({"error": "This reset link is invalid."}), 400

    user = db.session.get(User, payload.get("uid"))
    if user is None:
        return jsonify({"error": "This reset link is invalid."}), 400

    user.set_password(new_password)
    db.session.commit()
    return jsonify({"message": "Password updated. You can now log in."}), 200


@auth_bp.route("/account", methods=["DELETE"])
@jwt_required()
def delete_account():
    """
    Required for App Store review (Guideline 5.1.1v): any app that lets a
    user create an account must let them delete it, in-app, without having
    to go through a website or contact support.
    """
    user_id = int(get_jwt_identity())
    user = db.session.get(User, user_id)
    if user is None:
        return jsonify({"error": "Account not found."}), 404

    db.session.delete(user)  # cascades to LogEntry rows
    db.session.commit()
    return jsonify({"message": "Account deleted."}), 200
