"""
Muster backend — application factory.

This is the JSON API that the native/React Native client talks to. It
replaces the original single-file Flask app's server-rendered HTML routes;
the original file is kept at backend/app_original.py for reference.
"""
import os

from flask import Flask, jsonify

from .config import CONFIG_BY_NAME
from .extensions import cors, db, jwt, limiter, migrate


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_ENV", "development")
    config_cls = CONFIG_BY_NAME.get(config_name, CONFIG_BY_NAME["development"])

    app = Flask(__name__)
    app.config.from_object(config_cls)

    if config_name == "production" and not app.config.get("SECRET_KEY"):
        raise RuntimeError(
            "SECRET_KEY environment variable must be set in production. "
            "Refusing to start with no key / a guessable default."
        )

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)
    cors.init_app(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    from . import models  # noqa: F401  (registers models with SQLAlchemy metadata)
    from .auth import auth_bp
    from .api import api_bp

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(api_bp, url_prefix="/api")

    @app.route("/healthz")
    def healthz():
        return jsonify({"status": "ok"}), 200

    @app.errorhandler(404)
    def not_found(_e):
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(405)
    def method_not_allowed(_e):
        return jsonify({"error": "Method not allowed."}), 405

    @app.errorhandler(500)
    def server_error(_e):
        app.logger.exception("Unhandled server error")
        return jsonify({"error": "Internal server error."}), 500

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "same-origin"
        return response

    return app
