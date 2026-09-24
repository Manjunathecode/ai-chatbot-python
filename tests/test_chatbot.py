import json
from pathlib import Path

import pytest

from chatbot import FALLBACK_RESPONSE, IntentChatbot


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def bot() -> IntentChatbot:
    return IntentChatbot(ROOT / "intents.json", random_seed=7)


def test_intent_catalog_loads(bot: IntentChatbot) -> None:
    assert bot.intent_count == 18
    assert bot.pattern_count == 198


@pytest.mark.parametrize(
    ("message", "expected_intent"),
    [
        ("Hello there", "greeting"),
        ("Where is my order?", "order_status"),
        ("My payment failed", "payment_issue"),
        ("Reset my password", "reset_password"),
        ("App is not working", "app_issue"),
        ("Block my debit card", "block_card"),
        ("Book a doctor appointment", "book_appointment"),
        ("I need to speak to a human", "contact_agent"),
    ],
)
def test_representative_training_phrases(
    bot: IntentChatbot, message: str, expected_intent: str
) -> None:
    prediction = bot.predict(message)
    assert prediction.intent == expected_intent
    assert 0.0 <= prediction.confidence <= 1.0


def test_low_confidence_message_uses_fixed_fallback(bot: IntentChatbot) -> None:
    result = bot.respond("banana spaceship quantum")
    assert result["accepted"] is False
    assert result["response"] == FALLBACK_RESPONSE


def test_empty_message_is_rejected(bot: IntentChatbot) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        bot.predict("   ")


def test_invalid_catalog_is_rejected(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text(json.dumps({"intents": []}), encoding="utf-8")
    with pytest.raises(ValueError, match="non-empty"):
        IntentChatbot(invalid)


def test_responses_do_not_request_demo_contact_or_account_data() -> None:
    payload = json.loads((ROOT / "intents.json").read_text(encoding="utf-8"))
    all_responses = " ".join(
        response
        for intent in payload["intents"]
        for response in intent["responses"]
    ).lower()
    assert "support@" not in all_responses
    assert "1800-" not in all_responses
    assert "share your order id" not in all_responses
    assert "i have raised" not in all_responses
    assert "connecting you" not in all_responses
