import logging
import os
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import (
    LoginManager,
    current_user,
    login_user,
    logout_user,
)
from flask_wtf.csrf import CSRFProtect

from .forms import LoginForm, RegisterForm
from .models import User, db

logger = logging.getLogger(__name__)

csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=[])


def _normalize_database_url(database_url: str) -> str:
    if database_url.startswith("postgres://"):
        return database_url.replace("postgres://", "postgresql://", 1)
    return database_url


def create_app(test_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=True)

    instance_path = Path(app.instance_path)
    instance_path.mkdir(parents=True, exist_ok=True)

    default_database = f"sqlite:///{(instance_path / 'fullstack.db').as_posix()}"
    database_url = os.getenv("DATABASE_URL", default_database)
    secret_key = os.getenv("SECRET_KEY") or "dev-only-secret-key"

    app.config.update(
        SECRET_KEY=secret_key,
        SQLALCHEMY_DATABASE_URI=_normalize_database_url(database_url),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
        WTF_CSRF_ENABLED=True,
        RATELIMIT_STORAGE_URI="memory://",
        RATELIMIT_ENABLED=True,
    )

    if test_config:
        app.config.update(test_config)

    # Structured logging
    log_level = logging.DEBUG if app.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # Extensions
    db.init_app(app)
    csrf.init_app(app)

    login_manager.login_view = "login"
    login_manager.login_message = "Please log in to access that page."
    login_manager.login_message_category = "error"
    login_manager.init_app(app)

    limiter.storage_uri = app.config["RATELIMIT_STORAGE_URI"]
    limiter.init_app(app)

    @login_manager.user_loader
    def load_user(user_id: str) -> User | None:
        return db.session.get(User, int(user_id))

    with app.app_context():
        db.create_all()

    # ---------------------------------------------------------------------------
    # Security headers
    # ---------------------------------------------------------------------------

    @app.after_request
    def set_security_headers(response):
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

    # ---------------------------------------------------------------------------
    # Error handlers
    # ---------------------------------------------------------------------------

    @app.errorhandler(404)
    def not_found(e):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def internal_error(e):
        db.session.rollback()
        logger.exception("Unhandled server error: %s", e)
        return render_template("errors/500.html"), 500

    # ---------------------------------------------------------------------------
    # Routes
    # ---------------------------------------------------------------------------

    @app.route("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    @app.route("/")
    def home():
        projects = [
            {
                "title": "Jinja Student List",
                "description": "Simple templating example rendered from Flask.",
                "endpoint": "students",
                "cta": "Open student list",
            },
            {
                "title": "Validated Form",
                "description": "Server-side validation for name, mobile, and password.",
                "endpoint": "form_demo",
                "cta": "Open validation form",
            },
            {
                "title": "Auth Demo",
                "description": "Registration and login backed by SQLAlchemy.",
                "endpoint": "register",
                "cta": "Open auth flow",
            },
        ]
        return render_template("home.html", projects=projects)

    @app.route("/students")
    def students():
        student_list = ["student1", "student2", "student3"]
        return render_template("students.html", students=student_list)

    @app.route("/form-demo", methods=["GET", "POST"])
    def form_demo():
        errors = []
        submitted_name = None

        if request.method == "POST":
            submitted_name = request.form.get("name", "").strip()
            mobile = request.form.get("mobile", "").strip()
            password = request.form.get("password", "")

            if len(submitted_name) < 5:
                errors.append("Username must be at least 5 characters long.")

            if not mobile.isdigit() or len(mobile) < 10:
                errors.append("Mobile number must be at least 10 digits long.")

            if len(password) < 8:
                errors.append("Password must be at least 8 characters long.")

            if not errors:
                return render_template("form_success.html", name=submitted_name)

        return render_template("form_demo.html", errors=errors, submitted_name=submitted_name)

    @app.route("/auth/register", methods=["GET", "POST"])
    @limiter.limit("10 per minute")
    def register():
        if current_user.is_authenticated:
            return redirect(url_for("home"))

        form = RegisterForm()

        if form.validate_on_submit():
            existing_user = User.query.filter(
                (User.username == form.username.data) | (User.email == form.email.data)
            ).first()

            if existing_user is not None:
                flash("A user with that username or email already exists.", "error")
            else:
                try:
                    user = User(username=form.username.data, email=form.email.data)
                    user.set_password(form.password.data)
                    db.session.add(user)
                    db.session.commit()
                    logger.info("New user registered: %s", form.username.data)
                    flash("Registration successful. You can log in now.", "success")
                    return redirect(url_for("login"))
                except Exception:
                    db.session.rollback()
                    logger.exception("Failed to register user %s", form.username.data)
                    flash("An error occurred during registration. Please try again.", "error")

        return render_template("register.html", form=form)

    @app.route("/auth/login", methods=["GET", "POST"])
    @limiter.limit("10 per minute")
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("home"))

        form = LoginForm()

        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                logger.warning("Failed login attempt for username=%r", form.username.data)
                flash("Invalid username or password.", "error")
            else:
                login_user(user)
                logger.info("User logged in: %s", user.username)
                flash(f"Welcome back, {user.username}.", "success")
                next_page = request.args.get("next", "")
                if next_page and urlsplit(next_page).netloc == "":
                    return redirect(next_page)
                return redirect(url_for("home"))

        return render_template("login.html", form=form)

    @app.route("/auth/logout", methods=["POST"])
    def logout():
        logout_user()
        flash("You have been signed out.", "success")
        return redirect(url_for("home"))

    return app