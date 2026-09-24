# Architecture

## Components

1. `intents.json` contains original fictional patterns and safety-oriented responses.
2. `IntentChatbot` validates the catalog, vectorizes patterns with TF-IDF bigrams, encodes labels, and trains a deterministic scikit-learn MLP.
3. `predict()` returns the highest-probability intent and confidence estimate.
4. `respond()` applies a threshold. Accepted predictions use a curated response; low-confidence inputs receive a fixed fallback.
5. Flask validates request bodies and exposes `/`, `/login`, `/chat`, `/logout`, and `/health`.
6. The browser interface renders dynamic text with `textContent` and displays intent/confidence metadata.

## Data flow

```text
fictional message -> TF-IDF transform -> MLP probabilities
                  -> best intent -> threshold
                  -> curated demo response or fixed fallback
                  -> Flask JSON -> browser text nodes
```

## Boundaries

- No LLM or generative model
- No external API
- No database or conversation persistence
- No order, bank, healthcare, payment, or live-agent integration
- No real credentials, identifiers, or personal data required
- No production deployment claim
