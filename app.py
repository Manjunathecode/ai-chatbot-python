import json
import nltk
import random
from flask import Flask, render_template, request, jsonify, session
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import LabelEncoder

# ── Download NLTK Data ──
nltk.download('punkt', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('omw-1.4', quiet=True)
nltk.download('punkt_tab', quiet=True)

app = Flask(__name__)
app.secret_key = "ai_support_secret_key"

# ── Load Intents ──
with open('intents.json', 'r') as f:
    intents = json.load(f)

# ── Prepare Training Data ──
lemmatizer = WordNetLemmatizer()
patterns = []
tags = []

for intent in intents['intents']:
    for pattern in intent['patterns']:
        words = nltk.word_tokenize(pattern.lower())
        words = [lemmatizer.lemmatize(w) for w in words]
        patterns.append(' '.join(words))
        tags.append(intent['tag'])

# ── Train Model ──
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(patterns)
encoder = LabelEncoder()
y = encoder.fit_transform(tags)

classifier = MLPClassifier(
    hidden_layer_sizes=(128, 64),
    activation='relu',
    max_iter=500,
    random_state=42
)
classifier.fit(X, y)

print("✅ Model trained successfully!")

# ── Predict Intent ──


def predict_intent(user_input):
    words = nltk.word_tokenize(user_input.lower())
    words = [lemmatizer.lemmatize(w) for w in words]
    X_input = vectorizer.transform([' '.join(words)])
    prediction = classifier.predict(X_input)[0]
    probability = max(classifier.predict_proba(X_input)[0])
    intent_tag = encoder.inverse_transform([prediction])[0]
    return intent_tag, probability

# ── Get Response ──


def get_response(intent_tag):
    for intent in intents['intents']:
        if intent['tag'] == intent_tag:
            return random.choice(intent['responses'])
    return "I'm sorry, I didn't understand that. Please try again!"

# ── Routes ──


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    name = data.get('name', '').strip()
    contact = data.get('contact', '').strip()

    if not name:
        return jsonify({'success': False, 'message': '⚠️ Please enter your name!'})
    if not contact:
        return jsonify({'success': False, 'message': '⚠️ Please enter email or phone!'})
    if '@' not in contact and not contact.isdigit():
        return jsonify({'success': False, 'message': '⚠️ Enter valid email or 10-digit phone!'})

    session['name'] = name
    session['contact'] = contact
    return jsonify({
        'success': True,
        'message': (
            f"👋 Welcome {name}! I'm your AI Support Assistant.\n\n"
            f"I can help you with:\n"
            f"🛍️ Orders & Delivery\n"
            f"💳 Payments & Refunds\n"
            f"🏦 Banking\n"
            f"🏥 Hospital Appointments\n"
            f"📱 Tech Support\n\n"
            f"How can I help you today?"
        )
    })


@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'response': ''})

    intent, confidence = predict_intent(user_message)
    response = get_response(intent)

    if confidence < 0.7:
        response = "I'm not sure I understood. Could you rephrase? " + response

    return jsonify({
        'response': response,
        'intent': intent,
        'confidence': round(confidence * 100, 2)
    })


@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True})


if __name__ == '__main__':
    app.run(debug=True)
