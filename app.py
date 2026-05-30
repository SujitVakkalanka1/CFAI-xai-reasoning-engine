"""
Flask app for the CFAI Finance Reasoning Model with a simple login page.
"""

from __future__ import annotations

import os
from functools import wraps
from pathlib import Path
from typing import Any, Dict

from flask import Flask, jsonify, redirect, render_template, request, session, url_for

from finance_engine import FinanceInputError, FinanceReasoningModel


BASE_DIR = Path(__file__).resolve().parent
CHECKS_PATH = BASE_DIR / "finance_checks.json"

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-secret-key")

LOGIN_USERNAME = os.getenv("APP_USERNAME", "admin")
LOGIN_PASSWORD = os.getenv("APP_PASSWORD", "finance123")


def get_model() -> FinanceReasoningModel:
    return FinanceReasoningModel.from_json(CHECKS_PATH)


def login_required(view_function):
    @wraps(view_function)
    def wrapper(*args, **kwargs):
        if session.get("logged_in"):
            return view_function(*args, **kwargs)

        if request.path.startswith("/api/"):
            return jsonify({"message": "Please login first."}), 401

        return redirect(url_for("login"))

    return wrapper


@app.route("/login", methods=["GET", "POST"])
def login():
    error_message = ""

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == LOGIN_USERNAME and password == LOGIN_PASSWORD:
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("home"))

        error_message = "Wrong username or password."

    return render_template("login.html", error_message=error_message)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def home():
    return render_template("index.html", username=session.get("username", "User"))


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/evaluate", methods=["POST"])
@login_required
def evaluate():
    try:
        entered_values: Dict[str, Any] = request.get_json(force=True)
        result = get_model().evaluate(entered_values)
        return jsonify(result), 200

    except FinanceInputError as error:
        return jsonify({"message": str(error)}), 400

    except Exception:
        return jsonify({"message": "Something went wrong. Please check the entered values."}), 500


if __name__ == "__main__":
    app.run(debug=True)
