import logging
from pathlib import Path

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from utils.response import create_response
from utils.search import load_cache

BASE_DIR = Path(__file__).resolve().parent
FRONTEND_DIR = (BASE_DIR / "../frontend").resolve()

app = Flask(__name__, static_folder=str(FRONTEND_DIR), static_url_path="")
CORS(app)

limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    default_limits=["60 per minute"],
    storage_uri="memory://",
)

logging.basicConfig(level=logging.INFO)
file_handler = logging.FileHandler(BASE_DIR / "medical_backend.log", encoding="utf-8")
file_handler.setLevel(logging.INFO)
logging.getLogger().addHandler(file_handler)

load_cache()

@app.route("/")
def index():
    return send_from_directory(str(FRONTEND_DIR), "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(str(FRONTEND_DIR), path)


@app.route("/chat", methods=["POST"])
@limiter.limit("60 per minute")
def chat():
    data = request.get_json(silent=True) or {}
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"error": "Message is required."}), 400

    try:
        payload = create_response(message)
        return jsonify(payload)
    except Exception:
        logging.exception("Chat processing failed")
        return jsonify({
            "condition": "Health question",
            "description": "We were unable to process that request safely.",
            "medicines": [],
            "precautions": ["Please try again or rephrase your question."],
            "advice": ["If this is serious, seek medical help immediately."],
            "links": [],
            "learn_more": [],
            "disclaimer": "This is not a prescription. Consult a doctor.",
        }), 500


if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5001)
