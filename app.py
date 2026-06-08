from flask import Flask, request, jsonify, render_template
import torch
import torch.nn as nn
import pickle
import os

# ======================
# CONFIG
# ======================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_TYPE = "lstm"  # switch to "lstm" for BiLSTM
MODEL_DIR = "models"

# Paths
CNN_PATH = os.path.join(MODEL_DIR, "textcnn_emotion.pth")
LSTM_PATH = os.path.join(MODEL_DIR, "bilstm_emotion.pth")
VOCAB_PATH = os.path.join(MODEL_DIR, "vocab.pkl")
LE_PATH = os.path.join(MODEL_DIR, "label_encoder.pkl")

# ======================
# LOAD VOCAB + LABEL ENCODER
# ======================
with open(VOCAB_PATH, "rb") as f:
    vocab = pickle.load(f)

with open(LE_PATH, "rb") as f:
    le = pickle.load(f)

MAX_LEN = 50

def tokenize(text: str):
    return str(text).lower().split()

def encode(text: str):
    tokens = tokenize(text)
    ids = [vocab.get(t, vocab.get("<UNK>", 1)) for t in tokens[:MAX_LEN]]
    if len(ids) < MAX_LEN:
        ids += [vocab.get("<PAD>", 0)] * (MAX_LEN - len(ids))
    return ids

# ======================
# DEFINE MODELS
# ======================
class TextCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim, num_classes, kernel_sizes=[3,4,5], num_filters=128, dropout=0.5):
        super(TextCNN, self).__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.convs = nn.ModuleList([nn.Conv2d(1, num_filters, (k, embed_dim)) for k in kernel_sizes])
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(len(kernel_sizes) * num_filters, num_classes)
    def forward(self, x):
        x = self.embedding(x)
        x = x.unsqueeze(1)
        conv_outs = [torch.relu(conv(x)).squeeze(3) for conv in self.convs]
        pools = [torch.max(out, dim=2)[0] for out in conv_outs]
        cat = torch.cat(pools, dim=1)
        cat = self.dropout(cat)
        return self.fc(cat)

class BiLSTMClassifier(nn.Module):
    def __init__(self, vocab_size, embed_dim=200, hidden_dim=128, num_classes=7):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(
            embed_dim,
            hidden_dim,
            num_layers=2,
            bidirectional=True,
            batch_first=True,
            dropout=0.3
        )
        self.fc = nn.Linear(hidden_dim * 2, num_classes)
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):
        x = self.embedding(x)
        lstm_out, _ = self.lstm(x)
        # Take the last hidden states from both directions
        out = torch.cat((lstm_out[:, -1, :128], lstm_out[:, 0, 128:]), dim=1)
        out = self.dropout(out)
        return self.fc(out)

# ======================
# LOAD MODEL
# ======================
num_classes = len(le.classes_)
vocab_size = max(vocab.values()) + 1
num_classes = len(le.classes_)

model = BiLSTMClassifier(vocab_size, embed_dim=200, hidden_dim=128, num_classes=num_classes)
model.load_state_dict(torch.load(LSTM_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()
print(f"✅ Loaded LSTM model on {DEVICE}")



model.to(DEVICE)
model.eval()

# ======================
# FLASK APP
# ======================
app = Flask(__name__, template_folder="templates")

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(force=True)
    text = data.get("text", "")
    if not text:
        return jsonify({"error": "No text provided"}), 400

    ids = torch.tensor([encode(text)], dtype=torch.long).to(DEVICE)
    with torch.no_grad():
        output = model(ids)
        pred_idx = output.argmax(1).item()
        # FIXED mapping to match your trained model order
        label_order = ['anger', 'disgust', 'fear', 'joy', 'neutral', 'sadness', 'surprise']
        emotion = label_order[pred_idx]


    return jsonify({
        "input_text": text,
        "predicted_emotion": emotion
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
