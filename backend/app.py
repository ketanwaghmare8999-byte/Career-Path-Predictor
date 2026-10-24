# app.py
# Main backend server (Flask, as listed in synopsis "Technologies Used").
# Exposes a REST API that the frontend (HTML/CSS/JS) calls with fetch().
#
# Endpoints:
#   POST /api/signup        -> create account
#   POST /api/login         -> login, returns JWT token
#   GET  /api/skills        -> list of all skills/interests (to build the form)
#   POST /api/predict       -> ML prediction + skill-gap analysis (auth optional)
#   POST /api/feedback      -> save relevant/irrelevant feedback (feedback loop)
#   GET  /api/stats         -> aggregate feedback stats (admin-style view)

import os
import sys
import jwt
import joblib
import datetime
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, jsonify
from flask_cors import CORS

sys.path.append(os.path.join(os.path.dirname(__file__), "data"))
from career_skill_map import CAREER_SKILL_MAP, ALL_SKILLS, ALL_INTERESTS

import database as db

BASE = os.path.dirname(__file__)
MODEL_PATH = os.path.join(BASE, "models", "career_model.pkl")
SECRET_KEY = "career-path-predictor-dev-secret"  # for a real deployment, load from env var

app = Flask(__name__)
CORS(app)

db.init_db()

if not os.path.exists(MODEL_PATH):
    print("No trained model found. Run train_model.py first.")
    bundle = None
else:
    bundle = joblib.load(MODEL_PATH)

MODEL = bundle["model"] if bundle else None
SKILL_COLUMNS = bundle["skill_columns"] if bundle else ALL_SKILLS


# ---------------------------------------------------------------
# Auth helpers
# ---------------------------------------------------------------
def generate_token(user_id, email):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def get_user_from_token():
    """Returns user_id if a valid token was sent, else None (predictions
    still work without login, but won't be saved to a user's history)."""
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return payload.get("user_id")
    except jwt.PyJWTError:
        return None


def read_json():
    """Return the JSON body as a dict, or an empty dict if it is missing or is not a JSON object."""
    data = request.get_json(force=True, silent=True)
    return data if isinstance(data, dict) else {}


def text_value(data, key, strip=True):
    """Return a text value from the request body ('' if it is missing or not text)."""
    value = data.get(key)
    if not isinstance(value, str):
        return ""
    return value.strip() if strip else value


# ---------------------------------------------------------------
# Auth routes
# ---------------------------------------------------------------
@app.route("/api/signup", methods=["POST"])
def signup():
    data = read_json()
    name = text_value(data, "name")
    email = text_value(data, "email").lower()
    password = text_value(data, "password", strip=False)

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are all required."}), 400

    if " " in email or "@" not in email or "." not in email.rsplit("@", 1)[-1]:
        return jsonify({"error": "Please enter a valid email address."}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters."}), 400

    if db.get_user_by_email(email):
        return jsonify({"error": "An account with this email already exists."}), 400

    password_hash = generate_password_hash(password)
    user_id = db.create_user(name, email, password_hash)
    token = generate_token(user_id, email)
    return jsonify({"token": token, "name": name, "email": email})


@app.route("/api/login", methods=["POST"])
def login():
    data = read_json()
    email = text_value(data, "email").lower()
    password = text_value(data, "password", strip=False)

    if not email or not password:
        return jsonify({"error": "Email and password are required."}), 400

    user = db.get_user_by_email(email)
    if not user or not check_password_hash(user["password_hash"], password):
        return jsonify({"error": "Incorrect email or password."}), 401

    token = generate_token(user["id"], user["email"])
    return jsonify({"token": token, "name": user["name"], "email": user["email"]})


# ---------------------------------------------------------------
# Data routes (used to build the frontend form)
# ---------------------------------------------------------------
@app.route("/api/skills", methods=["GET"])
def get_skills():
    return jsonify({"skills": ALL_SKILLS, "interests": ALL_INTERESTS})


# ---------------------------------------------------------------
# Prediction route (the core ML feature)
# ---------------------------------------------------------------
@app.route("/api/predict", methods=["POST"])
def predict():
    if MODEL is None:
        return jsonify({"error": "Model is not trained yet. Run train_model.py first."}), 500

    data = read_json()
    skills = data.get("skills") if isinstance(data.get("skills"), list) else []
    interests = data.get("interests") if isinstance(data.get("interests"), list) else []

    # Keep only known skills/interests (anything else is ignored)
    selected_skills = {s for s in skills if isinstance(s, str) and s in ALL_SKILLS}
    selected_interests = {i for i in interests if isinstance(i, str) and i in ALL_INTERESTS}

    # The model predicts from skills, so at least one skill is needed
    if not selected_skills:
        return jsonify({"error": "Please select at least one skill."}), 400

    # Build the feature vector the model expects (1 = has skill, 0 = doesn't)
    feature_row = [[1 if s in selected_skills else 0 for s in SKILL_COLUMNS]]

    # predict_proba gives a confidence score per career (this is the
    # "classification model ... with a confidence score" from the synopsis)
    probabilities = MODEL.predict_proba(feature_row)[0]
    classes = MODEL.classes_

    ranked = sorted(zip(classes, probabilities), key=lambda x: x[1], reverse=True)
    top_results = ranked[:5]

    results = []
    for career_name, prob in top_results:
        info = CAREER_SKILL_MAP.get(career_name, {})
        required_skills = set(info.get("skills", []))

        have = sorted(required_skills & selected_skills)
        missing = sorted(required_skills - selected_skills)

        # Blend the model's probability with a simple interest-overlap boost,
        # then normalize into a friendlier 0-100 "match %" for the UI.
        interest_overlap = 0
        if info.get("interests"):
            interest_overlap = len(set(info["interests"]) & selected_interests) / len(info["interests"])

        match_pct = round(min(97, max(5, (prob * 100 * 0.8) + (interest_overlap * 20))))

        results.append({
            "career": career_name,
            "confidence": match_pct,
            "description": info.get("desc", ""),
            "have_skills": have,
            "missing_skills": missing,
            "resources": info.get("resources", ""),
        })

    # Re-sort after blending interest boost, in case ordering shifted
    results.sort(key=lambda r: r["confidence"], reverse=True)

    user_id = get_user_from_token()
    prediction_id = db.save_prediction(
        user_id, list(selected_skills), list(selected_interests),
        results[0]["career"], results[0]["confidence"]
    )

    return jsonify({"results": results, "prediction_id": prediction_id})


# ---------------------------------------------------------------
# Feedback loop route
# ---------------------------------------------------------------
@app.route("/api/feedback", methods=["POST"])
def feedback():
    data = read_json()
    prediction_id = data.get("prediction_id")
    career = data.get("career")
    is_relevant = data.get("is_relevant")

    if not isinstance(career, str) or career not in CAREER_SKILL_MAP:
        return jsonify({"error": "Unknown career."}), 400
    if isinstance(prediction_id, bool) or not isinstance(prediction_id, int) or not db.prediction_exists(prediction_id):
        return jsonify({"error": "Unknown prediction."}), 400
    if not isinstance(is_relevant, bool):
        return jsonify({"error": "Feedback must be true or false."}), 400

    db.save_feedback(prediction_id, career, is_relevant)
    return jsonify({"status": "saved"})


@app.route("/api/stats", methods=["GET"])
def stats():
    return jsonify({"feedback_stats": db.get_feedback_stats()})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "model_loaded": MODEL is not None})


if __name__ == "__main__":
    app.run(debug=False, port=5000)
