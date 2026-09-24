"""Flask application for the privacy-safe intent chatbot demonstration."""

from __future__ import annotations

import os
from pathlib import Path
import secrets

from flask import Flask, jsonify, render_template, request, session

from chatbot import IntentChatbot


BASE_DIR = Path(__file__).resolve().parent


def create_app(config: dict | None = None, chatbot: IntentChatbot | None = None) -> Flask:
    """Create the Flask app, optionally injecting test configuration or a chatbot."""

    app = Flask(__name__)
    app.config.update(
        SECRET_KEY=os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32),
        MAX_CONTENT_LENGTH=16 * 1024,
    )
    if config:
        app.config.update(config)

    bot = chatbot or IntentChatbot(BASE_DIR / "intents.json")
    app.extensions["intent_chatbot"] = bot

    @app.get("/")
    def home():
        return render_template("index.html")

    @app.post("/login")
    def login():
        data = request.get_json(silent=True) or {}
        display_name = str(data.get("display_name", "")).strip()
        if not display_name:
            return jsonify({"success": False, "message": "Enter a demo name or alias."}), 400
        if len(display_name) > 50:
            return jsonify({"success": False, "message": "Use 50 characters or fewer."}), 400

        session["display_name"] = display_name
        return jsonify(
            {
                "success": True,
                "message": (
                    f"Welcome, {display_name}. This portfolio demo classifies fictional "
                    "support questions into curated intents. Do not enter personal, payment, "
                    "medical, account, or order information."
                ),
            }
        )

    @app.post("/chat")
    def chat():
        data = request.get_json(silent=True) or {}
        message = str(data.get("message", "")).strip()
        if not message:
            return jsonify({"error": "Message must not be empty."}), 400
        if len(message) > 500:
            return jsonify({"error": "Message must be 500 characters or fewer."}), 400
        return jsonify(bot.respond(message))

    @app.post("/logout")
    def logout():
        session.clear()
        return jsonify({"success": True})

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "model": "tfidf-mlp-intent-classifier",
                "intent_count": bot.intent_count,
                "pattern_count": bot.pattern_count,
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1")
