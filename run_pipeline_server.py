from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import torch
import torch.nn as nn
import numpy as np
import pickle
import re
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ Explicitly allow all origins


# ========= CONFIG =========
MODEL_PATH = r"D:\Data science\emotion_classifier\models_stable\best_model.pth"
VOCAB_PATH = r"D:\Data science\emotion_classifier\models_stable\vocab.pkl"
LABEL_ENCODER_PATH = r"D:\Data science\emotion_classifier\models_stable\label_encoder.pkl"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MAX_LEN = 100

# ========= MODEL =========
class SelfAttention(nn.Module):
    def __init__(self, hidden_dim):
        super(SelfAttention, self).__init__()
        self.q = nn.Linear(hidden_dim, hidden_dim)
        self.k = nn.Linear(hidden_dim, hidden_dim)
        self.v = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, x):
        Q, K, V = self.q(x), self.k(x), self.v(x)
        attn = torch.softmax(torch.bmm(Q, K.transpose(1, 2)) / (x.size(-1)**0.5), dim=-1)
        return torch.bmm(attn, V).mean(dim=1)

class EmotionClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, output_dim):
        super(EmotionClassifier, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=2,
                            bidirectional=True, batch_first=True)
        self.att = SelfAttention(hidden_dim * 2)
        self.norm = nn.LayerNorm(hidden_dim * 2)
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, output_dim)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        emb = self.embedding(x)
        lstm_out, _ = self.lstm(emb)
        attn_out = self.att(lstm_out)
        norm_out = self.norm(attn_out)
        out = torch.relu(self.fc1(norm_out))
        out = self.fc2(out)
        return self.softmax(out)

# ========= LOAD MODEL / VOCAB / LABELS =========
vocab_size, embed_dim, hidden_dim, output_dim = 23810, 300, 256, 7
model = EmotionClassifier(vocab_size, embed_dim, hidden_dim, output_dim)
state_dict = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
model.load_state_dict(state_dict)
model.to(DEVICE)
model.eval()

with open(VOCAB_PATH, "rb") as f:
    vocab = pickle.load(f)
tokenizer = Tokenizer(num_words=len(vocab), oov_token="<OOV>")
tokenizer.word_index = vocab

with open(LABEL_ENCODER_PATH, "rb") as f:
    label_encoder = pickle.load(f)

# ========= HELPERS =========
def clean_text(t):
    """Cleans raw tweet text safely for tokenization."""
    if not isinstance(t, str):
        return ""
    t = t.lower().strip()
    t = re.sub(r"http\S+|www\S+|@\S+|#\S+", "", t)  # remove URLs, tags, mentions
    t = re.sub(r"[^a-z\s]", "", t)  # keep only alphabets and spaces
    t = re.sub(r"\s+", " ", t).strip()
    return t


def text_to_sequence(text, tokenizer, max_len):
    """Converts clean text into numeric padded sequence."""
    text = clean_text(text)
    if not text:  # empty string
        return [0] * max_len

    seq = tokenizer.texts_to_sequences([text])
    if not seq or seq[0] is None or len(seq[0]) == 0:
        return [0] * max_len

    # Filter out None or invalid tokens
    cleaned = [int(tok) for tok in seq[0] if isinstance(tok, (int, np.integer))]
    if len(cleaned) == 0:
        return [0] * max_len

    padded = pad_sequences([cleaned], maxlen=max_len, padding='post', truncating='post')
    return padded[0].tolist()

# ========= API =========
@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json()
    texts = data.get("texts", [])
    texts = [t for t in texts if isinstance(t, str) and t.strip()]
    if not texts:
        return jsonify({"error": "No valid text received"}), 400

    if not texts: return jsonify({"error": "No text received"}), 400

    sequences = [text_to_sequence(t, tokenizer, MAX_LEN) for t in texts]
    inputs = torch.tensor(sequences, dtype=torch.long).to(DEVICE)

    predictions = []
    with torch.no_grad():
        for i in range(0, len(inputs), 32):
            batch = inputs[i:i+32]
            outputs = model(batch)
            _, labels = torch.max(outputs, dim=1)
            predictions.extend(labels.cpu().numpy())

    decoded = label_encoder.inverse_transform(predictions)
    counts = pd.Series(decoded).value_counts().to_dict()
    return jsonify({"counts": counts}), 200
@app.route("/label_texts", methods=["POST"])
def label_texts():
    """Return emotion label for each input text in the same order."""
    data = request.get_json(force=True)
    texts = data.get("texts", [])
    texts = [t for t in texts if isinstance(t, str) and t.strip()]
    if not texts:
        return jsonify({"error": "No valid text received"}), 400

    sequences = [text_to_sequence(t, tokenizer, MAX_LEN) for t in texts]
    inputs = torch.tensor(sequences, dtype=torch.long).to(DEVICE)

    predictions = []
    with torch.no_grad():
        for i in range(0, len(inputs), 32):
            batch = inputs[i:i+32]
            outputs = model(batch)
            _, labels = torch.max(outputs, dim=1)
            predictions.extend(labels.cpu().numpy())

    decoded = label_encoder.inverse_transform(predictions).tolist()
    return jsonify({"labels": decoded}), 200


if __name__ == "__main__":
    app.run(port=5001)
