# ============================================================
#  Inference Script — Emotion Prediction (7 classes)
#  Loads trained model + vocab + label encoder
# ============================================================

import os, re, torch, pickle
import torch.nn.functional as F
from mast_model import BiLSTMAttentionModel, clean_text, tokenize

# ------------------ CONFIG ------------------
MODEL_DIR = "D:\\Data science\\emotion_classifier\\models_stable"
MODEL_PATH = f"{MODEL_DIR}\\best_model.pth"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"✅ Device: {DEVICE}")
if torch.cuda.is_available():
    print("GPU:", torch.cuda.get_device_name(0))

# ------------------ LOAD VOCAB + LABELS ------------------
with open(f"{MODEL_DIR}\\vocab.pkl", "rb") as f:
    vocab = pickle.load(f)
with open(f"{MODEL_DIR}\\label_encoder.pkl", "rb") as f:
    le = pickle.load(f)
classes = le.classes_.tolist()

# ------------------ MODEL INIT ------------------
model = BiLSTMAttentionModel(len(vocab), 300, 256, 2, len(classes), dropout=0.4).to(DEVICE)

# Safe load (weights_only=True silences warning)
weights = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
model.load_state_dict(weights)
model.eval()

# ------------------ TEXT ENCODING ------------------
MAX_LEN = 60

def encode(text):
    tokens = tokenize(text)
    if len(tokens) == 0:
        tokens = ["<UNK>"]
    ids = [vocab.get(t, 1) for t in tokens[:MAX_LEN]]
    return torch.tensor(ids)

# ------------------ PREDICTION FUNCTION ------------------
def predict_emotion(text):
    text = clean_text(text)
    x = encode(text).unsqueeze(0).to(DEVICE)
    lengths = torch.tensor([x.size(1)])
    with torch.no_grad():
        logits = model(x, lengths)
        probs = F.softmax(logits, dim=1).cpu().numpy().flatten()
    pred_idx = probs.argmax()
    return classes[pred_idx], probs

# ------------------ USER INTERFACE ------------------
if __name__ == "__main__":
    while True:
        text = input("\nEnter text (or 'quit' to exit): ").strip()
        if text.lower() in ["quit", "exit"]:
            break
        label, probs = predict_emotion(text)
        print(f"\n🧠 Predicted Emotion: {label.upper()}")
        print("📊 Confidence Breakdown:")
        for c, p in zip(classes, probs):
            print(f"  {c:<10} → {p*100:.2f}%")
