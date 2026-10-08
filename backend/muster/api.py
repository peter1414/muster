from datetime import datetime, date

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from .extensions import db
from .models import LogEntry, User
from .standards import (
    EXERCISE_ORDER,
    STANDARDS,
    display_value,
    parse_time_to_seconds,
    progress_ratio,
    serialize_standards,
)

api_bp = Blueprint("api", __name__)


def _current_user():
    return db.session.get(User, int(get_jwt_identity()))


def _serialize_entry(entry):
    std = STANDARDS[entry.exercise]
    return {
        "id": entry.id,
        "exercise": entry.exercise,
        "label": std["label"],
        "value": entry.value,
        "display_value": display_value(entry.value, std),
        "entry_date": entry.entry_date.isoformat(),
        "notes": entry.notes or "",
        "created_at": entry.created_at.isoformat() if entry.created_at else None,
    }


def _parse_and_validate_entry(data):
    """Shared by create + update. Returns (fields_dict, error_response_or_None)."""
    exercise = data.get("exercise")
    if exercise not in STANDARDS:
        return None, ("Choose a valid exercise.", 400)

    std = STANDARDS[exercise]
    raw_value = data.get("value")

    try:
        if std["unit"] == "time":
            # Accept either "mm:ss" strings or a raw seconds number, since a
            # native client may send either depending on its input widget.
            if isinstance(raw_value, str):
                value = parse_time_to_seconds(raw_value)
            else:
                value = float(raw_value)
        else:
            value = float(raw_value)
        if value < 0:
            raise ValueError("Value cannot be negative.")
    except (TypeError, ValueError) as exc:
        return None, (str(exc) or "Invalid value entered.", 400)

    entry_date_raw = data.get("entry_date")
    if entry_date_raw:
        try:
            entry_date = datetime.strptime(entry_date_raw, "%Y-%m-%d").date()
        except ValueError:
            return None, ("entry_date must be YYYY-MM-DD.", 400)
    else:
        entry_date = date.today()

    notes = (data.get("notes") or "").strip()[:280]

    return {
        "exercise": exercise,
        "value": value,
        "entry_date": entry_date,
        "notes": notes,
    }, None


@api_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user = _current_user()
    if user is None:
        return jsonify({"error": "Account not found."}), 404
    return jsonify(user.to_public_dict()), 200


@api_bp.route("/standards", methods=["GET"])
def standards():
    # Public/no-auth: this is static reference data, not user data, and the
    # mobile app needs it before login to render the register/log forms.
    return jsonify(serialize_standards()), 200


@api_bp.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    user_id = int(get_jwt_identity())
    cards = []
    for key in EXERCISE_ORDER:
        std = STANDARDS[key]
        latest = (
            LogEntry.query.filter_by(user_id=user_id, exercise=key)
            .order_by(LogEntry.entry_date.desc(), LogEntry.created_at.desc())
            .first()
        )
        card = {
            "key": key,
            "label": std["label"],
            "unit": std["unit"],
            "lower_better": std["lower_better"],
            "min_display": display_value(std["min"], std),
            "competitive_display": display_value(std["competitive"], std),
            "max_display": display_value(std["max"], std),
            "entry": None,
        }
        if latest:
            ratio, tier = progress_ratio(latest.value, std)
            card["entry"] = _serialize_entry(latest)
            card["ratio"] = round(ratio * 100)
            card["tier"] = tier
        cards.append(card)

    total_entries = LogEntry.query.filter_by(user_id=user_id).count()
    return jsonify({"cards": cards, "total_entries": total_entries}), 200


@api_bp.route("/entries", methods=["GET"])
@jwt_required()
def list_entries():
    user_id = int(get_jwt_identity())

    try:
        page = max(1, int(request.args.get("page", 1)))
        per_page = min(100, max(1, int(request.args.get("per_page", 20))))
    except ValueError:
        return jsonify({"error": "page and per_page must be integers."}), 400

    exercise = request.args.get("exercise")
    query = LogEntry.query.filter_by(user_id=user_id)
    if exercise:
        if exercise not in STANDARDS:
            return jsonify({"error": "Unknown exercise filter."}), 400
        query = query.filter_by(exercise=exercise)

    query = query.order_by(LogEntry.entry_date.desc(), LogEntry.created_at.desc())
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    return jsonify({
        "entries": [_serialize_entry(e) for e in pagination.items],
        "page": pagination.page,
        "per_page": per_page,
        "total": pagination.total,
        "total_pages": pagination.pages,
        "has_next": pagination.has_next,
    }), 200


@api_bp.route("/entries", methods=["POST"])
@jwt_required()
def create_entry():
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True) or {}

    fields, error = _parse_and_validate_entry(data)
    if error:
        message, status = error
        return jsonify({"error": message}), status

    entry = LogEntry(user_id=user_id, **fields)
    db.session.add(entry)
    db.session.commit()

    return jsonify(_serialize_entry(entry)), 201


def _get_owned_entry(entry_id, user_id):
    entry = db.session.get(LogEntry, entry_id)
    if entry is None or entry.user_id != user_id:
        return None
    return entry


@api_bp.route("/entries/<int:entry_id>", methods=["PUT"])
@jwt_required()
def update_entry(entry_id):
    user_id = int(get_jwt_identity())
    entry = _get_owned_entry(entry_id, user_id)
    if entry is None:
        return jsonify({"error": "Entry not found."}), 404

    data = request.get_json(silent=True) or {}
    # Allow partial updates: fall back to the entry's existing values for
    # any field the client didn't send.
    merged = {
        "exercise": data.get("exercise", entry.exercise),
        "value": data.get("value", entry.value),
        "entry_date": data.get("entry_date", entry.entry_date.isoformat()),
        "notes": data.get("notes", entry.notes),
    }

    fields, error = _parse_and_validate_entry(merged)
    if error:
        message, status = error
        return jsonify({"error": message}), status

    for k, v in fields.items():
        setattr(entry, k, v)
    db.session.commit()

    return jsonify(_serialize_entry(entry)), 200


@api_bp.route("/entries/<int:entry_id>", methods=["DELETE"])
@jwt_required()
def delete_entry(entry_id):
    user_id = int(get_jwt_identity())
    entry = _get_owned_entry(entry_id, user_id)
    if entry is None:
        return jsonify({"error": "Entry not found."}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Entry deleted."}), 200
