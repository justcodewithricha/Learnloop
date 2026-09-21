import os

from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg import errors as pg_errors
from dotenv import load_dotenv

from db import get_connection

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/start")
def auth():
    return render_template("auth.html", active_tab="signup")


@app.route("/signup", methods=["POST"])
def signup():
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    confirm = request.form.get("confirm_password", "")

    if not name or not email or not password:
        flash("Please fill in every field.", "error")
        return render_template("auth.html", active_tab="signup")

    if password != confirm:
        flash("Passwords don't match.", "error")
        return render_template("auth.html", active_tab="signup")

    if len(password) < 8:
        flash("Password must be at least 8 characters.", "error")
        return render_template("auth.html", active_tab="signup")

    password_hash = generate_password_hash(password)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s) RETURNING id",
                (name, email, password_hash),
            )
            user_id = cur.fetchone()["id"]
        conn.commit()
    except pg_errors.UniqueViolation:
        conn.rollback()
        flash("An account with that email already exists.", "error")
        return render_template("auth.html", active_tab="login")
    finally:
        conn.close()

    session["user_id"] = user_id
    session["user_name"] = name
    return redirect(url_for("dashboard"))


@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name, password_hash FROM users WHERE email = %s",
                (email,),
            )
            user = cur.fetchone()
    finally:
        conn.close()

    if not user or not check_password_hash(user["password_hash"], password):
        flash("Incorrect email or password.", "error")
        return render_template("auth.html", active_tab="login")

    session["user_id"] = user["id"]
    session["user_name"] = user["name"]
    return redirect(url_for("dashboard"))


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("auth"))
    return render_template("dashboard.html", name=session.get("user_name"))


if __name__ == "__main__":
    app.run(debug=True)