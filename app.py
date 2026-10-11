import os
from datetime import datetime
from pathlib import Path
from functools import wraps
import secrets
from flask import Flask, jsonify, render_template, request, send_from_directory, abort, redirect, url_for, session
from werkzeug.utils import secure_filename

BASE_DIR = Path(__file__).resolve().parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024 * 1024
app.config["UPLOAD_FOLDER"] = str(UPLOAD_DIR)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 12
LOGIN_USERNAME = os.environ.get("UPLOADER_USERNAME", "admin")
LOGIN_PASSWORD = os.environ.get("UPLOADER_PASSWORD", "ChangeMe-Please-123!")


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("authenticated"):
            if request.path.startswith("/api/"):
                return jsonify({"error": "Authentication required. Please log in."}), 401
            return redirect(url_for("login"))
        return view(*args, **kwargs)
    return wrapped


def file_info(path):
    stat = path.stat()
    return {
        "name": path.name,
        "size": stat.st_size,
        "modified": datetime.fromtimestamp(stat.st_mtime).astimezone().isoformat(timespec="seconds")
    }


@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("authenticated"):
        return redirect(url_for("index"))
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if secrets.compare_digest(username, LOGIN_USERNAME) and secrets.compare_digest(password, LOGIN_PASSWORD):
            session.clear()
            session["authenticated"] = True
            session.permanent = True
            return redirect(url_for("index"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/api/files", methods=["GET"])
@login_required
def list_files():
    files = [file_info(p) for p in UPLOAD_DIR.iterdir() if p.is_file() and not p.name.startswith(".")]
    files.sort(key=lambda item: item["modified"], reverse=True)
    return jsonify(files)


@app.route("/api/upload", methods=["POST"])
@login_required
def upload_file():
    uploaded = request.files.get("file")
    if uploaded is None or not uploaded.filename:
        return jsonify({"error": "No file was provided."}), 400

    filename = secure_filename(uploaded.filename)
    if not filename:
        return jsonify({"error": "Invalid filename."}), 400

    destination = UPLOAD_DIR / filename
    if destination.exists():
        stem, suffix = destination.stem, destination.suffix
        index = 1
        while (UPLOAD_DIR / f"{stem}_{index}{suffix}").exists():
            index += 1
        filename = f"{stem}_{index}{suffix}"
        destination = UPLOAD_DIR / filename

    uploaded.save(destination)
    return jsonify({"message": "Uploaded successfully.", "file": file_info(destination)}), 201


@app.route("/api/download/<path:filename>", methods=["GET"])
@login_required
def download_file(filename):
    safe_name = secure_filename(filename)
    if not safe_name:
        abort(404)
    path = UPLOAD_DIR / safe_name
    if not path.is_file():
        abort(404)
    return send_from_directory(UPLOAD_DIR, safe_name, as_attachment=True)


@app.route("/api/delete/<path:filename>", methods=["DELETE"])
@login_required
def delete_file(filename):
    safe_name = secure_filename(filename)
    if not safe_name:
        abort(404)
    path = UPLOAD_DIR / safe_name
    if not path.is_file():
        return jsonify({"error": "File not found."}), 404
    path.unlink()
    return jsonify({"message": "Deleted successfully."})


@app.errorhandler(413)
def too_large(_error):
    return jsonify({"error": "File is too large. The maximum request size is 2 GB."}), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
