"""Intent classification and curated response selection for the demo chatbot."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import random
from typing import Any

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder


FALLBACK_RESPONSE = (
    "I am not confident that I understood that message. Try a short fictional "
    "support question such as 'Where is my order?' or 'How do I reset my password?'"
)


@dataclass(frozen=True)
class IntentPrediction:
    """One predicted intent and its classifier confidence."""

    intent: str
    confidence: float


class IntentChatbot:
    """Small TF-IDF + MLP intent classifier backed by curated demo responses."""

    def __init__(
        self,
        intents_path: str | Path,
        *,
        confidence_threshold: float = 0.55,
        random_seed: int = 42,
    ) -> None:
        self.intents_path = Path(intents_path)
        self.confidence_threshold = confidence_threshold
        self._random = random.Random(random_seed)
        self._intents = self._load_intents(self.intents_path)
        self._responses = {
            intent["tag"]: tuple(intent["responses"]) for intent in self._intents
        }

        patterns: list[str] = []
        tags: list[str] = []
        for intent in self._intents:
            patterns.extend(intent["patterns"])
            tags.extend([intent["tag"]] * len(intent["patterns"]))

        self.vectorizer = TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            sublinear_tf=True,
            token_pattern=r"(?u)\b\w+\b",
        )
        features = self.vectorizer.fit_transform(patterns)
        self.encoder = LabelEncoder()
        labels = self.encoder.fit_transform(tags)
        self.classifier = MLPClassifier(
            hidden_layer_sizes=(64,),
            activation="relu",
            solver="lbfgs",
            max_iter=1_000,
            random_state=random_seed,
        )
        self.classifier.fit(features, labels)

    @staticmethod
    def _load_intents(path: Path) -> list[dict[str, Any]]:
        with path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)

        intents = payload.get("intents")
        if not isinstance(intents, list) or not intents:
            raise ValueError("intents.json must contain a non-empty 'intents' list")

        seen_tags: set[str] = set()
        for index, intent in enumerate(intents):
            if not isinstance(intent, dict):
                raise ValueError(f"Intent at index {index} must be an object")
            tag = intent.get("tag")
            patterns = intent.get("patterns")
            responses = intent.get("responses")
            if not isinstance(tag, str) or not tag.strip():
                raise ValueError(f"Intent at index {index} has no valid tag")
            if tag in seen_tags:
                raise ValueError(f"Duplicate intent tag: {tag}")
            if not isinstance(patterns, list) or not patterns or not all(
                isinstance(item, str) and item.strip() for item in patterns
            ):
                raise ValueError(f"Intent '{tag}' must have non-empty text patterns")
            if not isinstance(responses, list) or not responses or not all(
                isinstance(item, str) and item.strip() for item in responses
            ):
                raise ValueError(f"Intent '{tag}' must have non-empty text responses")
            seen_tags.add(tag)

        return intents

    @property
    def intent_count(self) -> int:
        return len(self._intents)

    @property
    def pattern_count(self) -> int:
        return sum(len(intent["patterns"]) for intent in self._intents)

    def predict(self, message: str) -> IntentPrediction:
        cleaned = message.strip()
        if not cleaned:
            raise ValueError("Message must not be empty")

        features = self.vectorizer.transform([cleaned])
        probabilities = self.classifier.predict_proba(features)[0]
        best_index = int(probabilities.argmax())
        encoded_label = self.classifier.classes_[best_index]
        intent = str(self.encoder.inverse_transform([encoded_label])[0])
        return IntentPrediction(intent=intent, confidence=float(probabilities[best_index]))

    def respond(self, message: str) -> dict[str, str | float | bool]:
        prediction = self.predict(message)
        accepted = prediction.confidence >= self.confidence_threshold
        response = (
            self._random.choice(self._responses[prediction.intent])
            if accepted
            else FALLBACK_RESPONSE
        )
        return {
            "response": response,
            "intent": prediction.intent,
            "confidence": round(prediction.confidence * 100, 2),
            "accepted": accepted,
        }
