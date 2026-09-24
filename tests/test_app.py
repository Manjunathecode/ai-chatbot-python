from pathlib import Path

import pytest

from app import create_app
from chatbot import IntentChatbot


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def client():
    bot = IntentChatbot(ROOT / "intents.json", random_seed=11)
    application = create_app(
        {"TESTING": True, "SECRET_KEY": "test-only-secret"}, chatbot=bot
    )
    return application.test_client()


def test_home_renders_privacy_boundary(client) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert b"Portfolio demonstration only" in response.data
    assert b"Demo name or alias" in response.data
    assert b"Email /" not in response.data


def test_login_accepts_alias_without_contact_data(client) -> None:
    response = client.post("/login", json={"display_name": "Demo User"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["success"] is True
    assert "Do not enter personal" in payload["message"]


def test_login_rejects_missing_or_long_alias(client) -> None:
    assert client.post("/login", json={}).status_code == 400
    assert client.post("/login", json={"display_name": "x" * 51}).status_code == 400


def test_chat_returns_intent_confidence_and_safe_response(client) -> None:
    response = client.post("/chat", json={"message": "Where is my order?"})
    assert response.status_code == 200
    payload = response.get_json()
    assert payload["intent"] == "order_status"
    assert payload["accepted"] is True
    assert 0.0 <= payload["confidence"] <= 100.0
    assert "real order identifiers" in payload["response"] or "production" in payload["response"]


def test_chat_rejects_empty_and_oversized_messages(client) -> None:
    assert client.post("/chat", json={"message": ""}).status_code == 400
    assert client.post("/chat", json={"message": "x" * 501}).status_code == 400


def test_health_reports_model_shape(client) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {
        "status": "ok",
        "model": "tfidf-mlp-intent-classifier",
        "intent_count": 18,
        "pattern_count": 198,
    }


def test_logout_clears_session(client) -> None:
    response = client.post("/logout")
    assert response.status_code == 200
    assert response.get_json() == {"success": True}
