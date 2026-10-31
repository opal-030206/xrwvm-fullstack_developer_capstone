"""Flask sentiment analysis microservice.

Runs independently of Django on port 5050.  Django calls ``POST /analyze``
whenever a review is submitted.

    python -m flask --app server.sentiment.app run --port 5050
"""

import os

from flask import Flask, jsonify, request
from flask_cors import CORS

try:  # importable both as a package module and as a standalone script
    from .analyzer import analyze
except ImportError:  # pragma: no cover - direct execution
    from analyzer import analyze

app = Flask(__name__)
CORS(app)


@app.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "service": "sentiment-analyzer"})


@app.post("/analyze")
def analyze_review():
    payload = request.get_json(silent=True) or request.form.to_dict() or {}
    text = payload.get("text") or payload.get("review") or ""

    if not isinstance(text, str) or not text.strip():
        return jsonify({"error": "Field 'text' is required."}), 400

    return jsonify(analyze(text))


@app.post("/sentiment")
def analyze_review_alias():
    """Alias kept for clients that post the review under 'review'."""
    return analyze_review()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5050"))
    app.run(host="0.0.0.0", port=port)
