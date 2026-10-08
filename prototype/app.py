"""
Muster — MVP training log
A Flask web app for tracking PST/PFT training against selection standards.

Run locally:
    pip install -r requirements.txt
    python app.py
Then open http://127.0.0.1:5000
"""

from datetime import date, datetime
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from werkzeug.security import generate_password_hash, check_password_hash

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret-change-this-before-you-ever-deploy"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///muster.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message = "Log in to access your muster log."

# ---------------------------------------------------------------------------
# Standards — the physical standard lines each log entry is measured against.
# Reps-based events: higher is better (lower_better=False).
# Time-based events: stored in seconds, lower is better (lower_better=True).
# Swap these for the real standards of the pipeline you're targeting.
# ---------------------------------------------------------------------------

STANDARDS = {
    "pushups": {
        "label": "Push-ups (2 min)", "unit": "reps",
        "min": 50, "competitive": 80, "max": 100, "lower_better": False,
    },
    "situps": {
        "label": "Sit-ups (2 min)", "unit": "reps",
        "min": 60, "competitive": 85, "max": 100, "lower_better": False,
    },
    "pullups": {
        "label": "Pull-ups, dead hang", "unit": "reps",
        "min": 6, "competitive": 15, "max": 20, "lower_better": False,
    },
    "run_1_5mi": {
        "label": "1.5 mile run", "unit": "time",
        "min": 630, "competitive": 540, "max": 495, "lower_better": True,
    },
    "swim_500m": {
        "label": "500m swim", "unit": "time",
        "min": 750, "competitive": 570, "max": 480, "lower_better": True,
    },
}

EXERCISE_ORDER = ["pushups", "situps", "pullups", "run_1_5mi", "swim_500m"]


def format_seconds(total_seconds):
    """Convert seconds -> mm:ss for display."""
    total_seconds = int(round(total_seconds))
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}:{seconds:02d}"


def parse_time_to_seconds(raw):
    """Parse 'mm:ss' or 'm:ss' input into seconds. Raises ValueError on bad input."""
    raw = raw.strip()
    if ":" not in raw:
        raise ValueError("Time must be in mm:ss format, e.g. 9:45")
    minutes_str, seconds_str = raw.split(":", 1)
    minutes = int(minutes_str)
    seconds = int(seconds_str)
    if seconds < 0 or seconds > 59 or minutes < 0:
        raise ValueError("Invalid mm:ss value")
    return minutes * 60 + seconds


def progress_ratio(value, std):
    """
    Return 0-1 progress between min and max standard, for a progress bar,
    and the tier the value currently falls in (below_min / min / competitive / max).
    """
    lo, comp, hi = std["min"], std["competitive"], std["max"]
    if std["lower_better"]:
        # Smaller is better: flip the scale so 0 = worst (min), 1 = best (max)
        if value >= lo:
            ratio = 0.0
        elif value <= hi:
            ratio = 1.0
        else:
            ratio = (lo - value) / (lo - hi)
    else:
        if value <= lo:
            ratio = 0.0
        elif value >= hi:
            ratio = 1.0
        else:
            ratio = (value - lo) / (hi - lo)

    ratio = max(0.0, min(1.0, ratio))

    if std["lower_better"]:
        if value <= hi:
            tier = "max"
        elif value <= comp:
            tier = "competitive"
        elif value <= lo:
            tier = "min"
        else:
            tier = "below"
    else:
        if value >= hi:
            tier = "max"
        elif value >= comp:
            tier = "competitive"
        elif value >= lo:
            tier = "min"
        else:
            tier = "below"

    return ratio, tier


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entries = db.relationship("LogEntry", backref="user", lazy=True,
                               cascade="all, delete-orphan")

    def set_password(self, raw_password):
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password):
        return check_password_hash(self.password_hash, raw_password)


class LogEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    exercise = db.Column(db.String(40), nullable=False)   # key into STANDARDS
    value = db.Column(db.Float, nullable=False)           # reps, or seconds for time events
    entry_date = db.Column(db.Date, default=date.today, nullable=False)
    notes = db.Column(db.String(280))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# ---------------------------------------------------------------------------
# Routes — auth
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        error = None
        if not username or not email or not password:
            error = "All fields are required."
        elif len(password) < 6:
            error = "Password must be at least 6 characters."
        elif User.query.filter_by(username=username).first():
            error = "That username is already taken."
        elif User.query.filter_by(email=email).first():
            error = "An account with that email already exists."

        if error:
            flash(error, "error")
            return render_template("register.html")

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash("Account created. Welcome to Muster.", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()

        if user is None or not user.check_password(password):
            flash("Incorrect username or password.", "error")
            return render_template("login.html")

        login_user(user)
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Routes — app
# ---------------------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    cards = []
    for key in EXERCISE_ORDER:
        std = STANDARDS[key]
        latest = (
            LogEntry.query
            .filter_by(user_id=current_user.id, exercise=key)
            .order_by(LogEntry.entry_date.desc(), LogEntry.created_at.desc())
            .first()
        )
        def fmt(n):
            return format_seconds(n) if std["unit"] == "time" else int(n)

        card = {
            "key": key,
            "label": std["label"],
            "std": std,
            "entry": None,
            "min_display": fmt(std["min"]),
            "competitive_display": fmt(std["competitive"]),
            "max_display": fmt(std["max"]),
            "unit_suffix": "reps" if std["unit"] == "reps" else "",
        }
        if latest:
            ratio, tier = progress_ratio(latest.value, std)
            card["entry"] = latest
            card["display_value"] = fmt(latest.value)
            card["ratio"] = round(ratio * 100)
            card["tier"] = tier
        cards.append(card)

    total_entries = LogEntry.query.filter_by(user_id=current_user.id).count()
    return render_template("dashboard.html", cards=cards, total_entries=total_entries)


@app.route("/log", methods=["GET", "POST"])
@login_required
def log_entry():
    if request.method == "POST":
        exercise = request.form.get("exercise")
        raw_value = request.form.get("value", "").strip()
        entry_date_raw = request.form.get("entry_date") or date.today().isoformat()
        notes = request.form.get("notes", "").strip()[:280]

        if exercise not in STANDARDS:
            flash("Choose a valid exercise.", "error")
            return render_template("log_entry.html", standards=STANDARDS,
                                    exercise_order=EXERCISE_ORDER)

        std = STANDARDS[exercise]
        try:
            if std["unit"] == "time":
                value = parse_time_to_seconds(raw_value)
            else:
                value = float(raw_value)
                if value < 0:
                    raise ValueError("Value cannot be negative.")
        except ValueError as exc:
            flash(str(exc) or "Invalid value entered.", "error")
            return render_template("log_entry.html", standards=STANDARDS,
                                    exercise_order=EXERCISE_ORDER)

        try:
            entry_date = datetime.strptime(entry_date_raw, "%Y-%m-%d").date()
        except ValueError:
            entry_date = date.today()

        entry = LogEntry(
            user_id=current_user.id,
            exercise=exercise,
            value=value,
            entry_date=entry_date,
            notes=notes,
        )
        db.session.add(entry)
        db.session.commit()
        flash(f"Logged {std['label']}.", "success")
        return redirect(url_for("dashboard"))

    return render_template("log_entry.html", standards=STANDARDS,
                            exercise_order=EXERCISE_ORDER, today=date.today().isoformat())


@app.route("/history")
@login_required
def history():
    entries = (
        LogEntry.query
        .filter_by(user_id=current_user.id)
        .order_by(LogEntry.entry_date.desc(), LogEntry.created_at.desc())
        .all()
    )
    rows = []
    for e in entries:
        std = STANDARDS[e.exercise]
        display_value = format_seconds(e.value) if std["unit"] == "time" else int(e.value)
        rows.append({"entry": e, "label": std["label"], "display_value": display_value})
    return render_template("history.html", rows=rows)


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
