# Interview Briefing

## 30-second explanation

I built an intent-based support chatbot with Flask and scikit-learn. It converts a fictional message into TF-IDF features, uses a small MLP to classify one of 18 curated intents, and returns an original prewritten response. I added a confidence fallback, request validation, privacy-safe demo boundaries, safe browser rendering, and automated classifier and route tests. It is deliberately presented as a portfolio NLP demo, not an LLM or production support system.

## 2-minute explanation

The project started as a compact support-chatbot prototype. I reviewed the implementation and found that its real capability was supervised intent classification rather than generative AI. I separated the classifier into a reusable module, validated the intent schema, removed the runtime NLTK download requirement, and used TF-IDF unigrams and bigrams with a deterministic scikit-learn MLP. The Flask layer now validates aliases and messages, exposes a health route, and returns the intent and confidence with each response. Low-confidence input receives a fixed fallback instead of an unrelated intent response. I removed unnecessary email/phone collection and rewrote the response catalog so it never pretends to access orders, banks, hospitals, payments, or live agents. The frontend uses text nodes for dynamic content, reducing injection risk. Automated tests cover representative classifications, fallback behavior, catalog safety, and every route. The main limitation is the small hand-authored catalog, so I do not claim a general accuracy score or production readiness.

## How intents work

Each intent has a tag, example patterns, and curated responses. TF-IDF maps patterns and incoming text to sparse numeric features. The MLP learns a multiclass boundary over those features. At inference, the highest predicted class is decoded to the intent tag. If its confidence is below the threshold, the app returns a fixed fallback; otherwise it chooses one curated response for that intent.

## Limitations

- small, hand-authored training catalog;
- no independent representative test set;
- no conversation context or entity extraction;
- no calibrated out-of-domain detector;
- no external service integration or persistence;
- local Flask development server only.

## Modern LLM/API improvement path

A modern version could keep deterministic intent routing for high-risk actions and add retrieval or an LLM only for low-risk explanation. I would define an approved knowledge base, minimize/redact user data, use structured tool schemas, require server-side authorization for actions, add prompt-injection tests, log only sanitized telemetry, enforce latency/cost limits, evaluate factuality and refusal behavior, and keep a human escalation path. The LLM would never receive unrestricted system credentials or execute arbitrary commands.

## Likely interview questions

1. Why did you describe this as intent-based rather than generative AI?
2. Why use TF-IDF for this problem?
3. Why use an MLP instead of logistic regression or Naive Bayes?
4. How are intent labels encoded?
5. What does the confidence value represent?
6. Why is confidence not the same as accuracy?
7. How does the low-confidence fallback work?
8. How would you create a proper evaluation set?
9. How would you detect out-of-scope requests?
10. What risks existed in the original contact-data flow?
11. How did you reduce browser injection risk?
12. Why is the model trained at startup, and what would you change for production?
13. How would you add context across multiple messages?
14. How would you integrate an LLM safely?
15. What production controls are still missing?
