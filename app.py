
import os
import sqlite3
import uuid

from functools import wraps
from datetime import datetime

from flask import (
    Flask, render_template, request, jsonify,
    redirect, url_for, session, flash
)

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from dotenv import load_dotenv
from chatbot import Chatbot


load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "chat_history.db")

app = Flask(__name__)

app.secret_key = os.getenv("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError("Set FLASK_SECRET_KEY in your .env file.")

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=False  # Set True when deployed with HTTPS
)

bot = Chatbot()


# DATABASE
def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            conversation_id TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            conversation_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


init_db()


# AUTHENTICATION DECORATOR
def login_required(function):

    @wraps(function)
    def wrapper(*args, **kwargs):

        if "user_id" not in session:
            return redirect(url_for("login"))

        return function(*args, **kwargs)

    return wrapper


# LOGIN PAGE
@app.route("/login", methods=["GET", "POST"])
def login():

    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_db()

        user = connection.execute("""
            SELECT * FROM users
            WHERE username = ?
        """, (username,)).fetchone()

        connection.close()

        if user and check_password_hash(
            user["password_hash"], password
        ):

            session.clear()
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["conversation_id"] = user["conversation_id"]

            return redirect(url_for("index"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


# REGISTRATION PAGE
@app.route("/register", methods=["GET", "POST"])
def register():

    if "user_id" in session:
        return redirect(url_for("index"))

    if request.method == "POST":

        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if len(username) < 3 or len(username) > 30:
            flash("Username must be 3–30 characters.", "error")

        elif len(password) < 10:
            flash("Password must contain at least 10 characters.", "error")

        elif password != confirm_password:
            flash("Passwords do not match.", "error")

        else:

            connection = get_db()

            try:

                password_hash = generate_password_hash(password)
                conversation_id = str(uuid.uuid4())

                connection.execute("""
                    INSERT INTO users (
                        username, password_hash, conversation_id
                    )
                    VALUES (?, ?, ?)
                """, (
                    username,
                    password_hash,
                    conversation_id
                ))

                connection.commit()

                flash("Account created successfully. Please log in.", "success")

                connection.close()

                return redirect(url_for("login"))

            except sqlite3.IntegrityError:

                connection.close()
                flash("That username is already taken.", "error")

    return render_template("register.html")


# LOGOUT
@app.route("/logout")
@login_required
def logout():

    session.clear()

    return redirect(url_for("login"))


# GET CHAT HISTORY
def get_history(conversation_id, limit=20):

    connection = get_db()

    rows = connection.execute("""
        SELECT role, content
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id DESC
        LIMIT ?
    """, (conversation_id, limit)).fetchall()

    connection.close()

    return [
        {"role": row["role"], "content": row["content"]}
        for row in reversed(rows)
    ]


# SAVE MESSAGE
def save_message(conversation_id, role, content):

    connection = get_db()

    connection.execute("""
        INSERT INTO messages (
            conversation_id, role, content, created_at
        )
        VALUES (?, ?, ?, ?)
    """, (
        conversation_id,
        role,
        content,
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    connection.commit()
    connection.close()


# CHAT HOMEPAGE
@app.route("/")
@login_required
def index():

    conversation_id = session["conversation_id"]

    messages = get_history(conversation_id, limit=100)

    return render_template(
        "index.html",
        messages=messages,
        username=session["username"]
    )


# CHAT ENDPOINT
@app.route("/chat", methods=["POST"])
@login_required
def chat():

    data = request.get_json(silent=True) or {}
    user_message = data.get("message", "")

    if not isinstance(user_message, str):
        return jsonify({"error": "Invalid message."}), 400

    user_message = user_message.strip()

    if not user_message:
        return jsonify({"error": "Enter a message."}), 400

    if len(user_message) > 4000:
        return jsonify({"error": "Message is too long."}), 400

    conversation_id = session["conversation_id"]

    history = get_history(conversation_id)

    answer = bot.respond(user_message, history)

    save_message(conversation_id, "user", user_message)
    save_message(conversation_id, "assistant", answer)

    return jsonify({"reply": answer})


# CLEAR CHAT
@app.route("/clear", methods=["POST"])
@login_required
def clear_chat():

    conversation_id = session["conversation_id"]

    connection = get_db()

    connection.execute("""
        DELETE FROM messages
        WHERE conversation_id = ?
    """, (conversation_id,))

    connection.commit()
    connection.close()

    return jsonify({
        "success": True,
        "message": "Conversation cleared."
    })


# HEALTH CHECK
@app.route("/health")
def health():

    return jsonify({
        "status": "online",
        "assistant": "Masika AI"
    })


if __name__ == "__main__":

    print("=" * 45)
    print("       MASIKA AI")
    print("       AUTHENTICATION ENABLED")
    print("=" * 45)

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
