import torch
import torch.nn as nn
import pandas as pd
from tqdm import tqdm
import numpy as np
import pickle
import re
import warnings
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

warnings.filterwarnings("ignore", category=FutureWarning)

# ========= CONFIG =========
MODEL_PATH = r"D:\Data science\emotion_classifier\models_stable\best_model.pth"
VOCAB_PATH = r"D:\Data science\emotion_classifier\models_stable\vocab.pkl"
LABEL_ENCODER_PATH = r"D:\Data science\emotion_classifier\models_stable\label_encoder.pkl"
INPUT_CSV = r"D:\Data science\Tweet_scaper\cleaned_tweet_replies.csv"
OUTPUT_CSV = "predicted_sentiments.csv"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MAX_LEN = 100

# ========= MODEL ARCHITECTURE =========
class SelfAttention(nn.Module):
    def __init__(self, hidden_dim):
        super(SelfAttention, self).__init__()
        self.q = nn.Linear(hidden_dim, hidden_dim)
        self.k = nn.Linear(hidden_dim, hidden_dim)
        self.v = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, x):
        Q, K, V = self.q(x), self.k(x), self.v(x)
        attn = torch.softmax(torch.bmm(Q, K.transpose(1, 2)) / (x.size(-1) ** 0.5), dim=-1)
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

# ========= LOAD MODEL =========
vocab_size = 23810
embed_dim = 300
hidden_dim = 256
output_dim = 7  # 7 emotion classes

print("📦 Loading model...")
model = EmotionClassifier(vocab_size, embed_dim, hidden_dim, output_dim)
state_dict = torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True)
model.load_state_dict(state_dict)
model.to(DEVICE)
model.eval()
print("✅ Model loaded successfully.")

# ========= LOAD VOCAB =========
print("📘 Loading vocabulary from vocab.pkl ...")
with open(VOCAB_PATH, "rb") as f:
    vocab = pickle.load(f)

tokenizer = Tokenizer(num_words=len(vocab), oov_token="<OOV>")
tokenizer.word_index = vocab
print(f"✅ Loaded vocab with {len(vocab)} tokens")

# ========= LOAD LABEL ENCODER =========
print("🎯 Loading label encoder...")
with open(LABEL_ENCODER_PATH, "rb") as f:
    label_encoder = pickle.load(f)
print(f"✅ Label encoder loaded with {len(label_encoder.classes_)} classes.")

# ========= CLEAN TEXT & TOKENIZE =========
def clean_text_for_tokenizer(text):
    if not isinstance(text, str):
        return ""
    text = text.lower().strip()
    text = re.sub(r"http\S+|www\S+|@\S+|#\S+", "", text)
    text = re.sub(r"[^a-z\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def text_to_sequence(text, tokenizer, max_len):
    text = clean_text_for_tokenizer(text)
    if text == "":
        return [0] * max_len
    seq = tokenizer.texts_to_sequences([text])
    if not seq or seq[0] is None or len(seq[0]) == 0:
        return [0] * max_len
    cleaned_seq = [tok for tok in seq[0] if isinstance(tok, (int, np.integer))]
    if len(cleaned_seq) == 0:
        return [0] * max_len
    padded = pad_sequences([cleaned_seq], maxlen=max_len, padding='post', truncating='post')
    return padded[0].tolist()

# ========= LOAD DATA =========
df = pd.read_csv(INPUT_CSV)
texts = df["text"].astype(str).tolist()
print(f"📄 Loaded {len(texts)} texts from CSV.")

# ========= CONVERT TO TENSORS =========
sequences = [text_to_sequence(t, tokenizer, MAX_LEN) for t in texts]
inputs = torch.tensor(sequences, dtype=torch.long).to(DEVICE)

# ========= PREDICT =========
predictions = []
confidences = []

print("⚙️ Running predictions...")
with torch.no_grad():
    for i in tqdm(range(0, len(inputs), 32)):
        batch = inputs[i:i+32]
        outputs = model(batch)
        probs, labels = torch.max(outputs, dim=1)
        predictions.extend(labels.cpu().numpy())
        confidences.extend(probs.cpu().numpy())

# ========= DECODE LABELS =========
predicted_labels = label_encoder.inverse_transform(predictions)

# ========= SAVE RESULTS =========
output_df = pd.DataFrame({
    "text": texts,
    "predicted_label": predicted_labels,
    "confidence": np.round(confidences, 4)
})
output_df.to_csv(OUTPUT_CSV, index=False)

# ========= SUMMARY =========
summary = output_df["predicted_label"].value_counts().to_dict()
print("\n🧾 Prediction Summary:")
for label, count in summary.items():
    print(f"  {label:<10}: {count}")

print(f"\n✅ Predictions saved to: {OUTPUT_CSV}")
