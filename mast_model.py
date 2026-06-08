# ============================================================
#  Emotion Classification (7 classes) - BiLSTM + Self-Attention
#  Final stable version (saves vocab + label encoder)
# ============================================================

import os, re, random, time, pickle
import numpy as np
import pandas as pd
from collections import Counter
from tqdm import tqdm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.utils.class_weight import compute_class_weight

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence, pad_packed_sequence

# ============================================================
# 🧩 Model Definition
# ============================================================

class SelfAttention(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.q = nn.Linear(dim, dim)
        self.k = nn.Linear(dim, dim)
        self.v = nn.Linear(dim, dim)
        self.scale = dim ** 0.5

    def forward(self, x):
        att = torch.softmax(torch.bmm(self.q(x), self.k(x).transpose(1, 2)) / self.scale, dim=-1)
        return torch.bmm(att, self.v(x))

class BiLSTMAttentionModel(nn.Module):
    def __init__(self, vocab_size, embed_dim, hidden_dim, num_layers, num_classes, dropout=0.4):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers=num_layers,
                            batch_first=True, bidirectional=True, dropout=dropout)
        self.att = SelfAttention(hidden_dim * 2)
        self.norm = nn.LayerNorm(hidden_dim * 2)
        self.dropout = nn.Dropout(dropout)
        self.fc1 = nn.Linear(hidden_dim * 2, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, num_classes)
        self.act = nn.ReLU()

    def forward(self, x, lengths):
        embeds = self.embedding(x)
        packed = pack_padded_sequence(embeds, lengths.cpu(), batch_first=True, enforce_sorted=False)
        packed_out, _ = self.lstm(packed)
        out, _ = pad_packed_sequence(packed_out, batch_first=True)
        att_out = self.att(out)
        out = self.norm(out + att_out)
        out = torch.mean(out, dim=1)
        out = self.act(self.fc1(self.dropout(out)))
        return self.fc2(out)

# ============================================================
# 🧹 Text Preprocessing
# ============================================================

def clean_text(text):
    text = str(text).lower()
    text = re.sub(r"[^a-z0-9\s']", " ", text)
    return re.sub(r"\s+", " ", text).strip()

def tokenize(text):
    return clean_text(text).split()

# ============================================================
# 🚀 Training
# ============================================================

if __name__ == "__main__":
    DATA_PATH = "D:\\Data science\\emotion_classifier\\data\\goemotions_7class_balanced.csv"
    MODEL_DIR = "D:\\Data science\\emotion_classifier\\models_stable"
    os.makedirs(MODEL_DIR, exist_ok=True)

    SEED = 42
    random.seed(SEED)
    np.random.seed(SEED)
    torch.manual_seed(SEED)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(SEED)

    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"✅ Device: {DEVICE}")
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    MAX_VOCAB = 30000
    MAX_LEN = 60
    BATCH_SIZE = 64
    EMBED_DIM = 300
    HIDDEN_DIM = 256
    N_LAYERS = 2
    DROPOUT = 0.4
    EPOCHS = 35
    LR = 1e-3

    print("📥 Loading data...")
    df = pd.read_csv(DATA_PATH).dropna(subset=["text", "emotion"])
    df["text"] = df["text"].apply(clean_text)

    le = LabelEncoder()
    df["label"] = le.fit_transform(df["emotion"])
    classes = le.classes_.tolist()
    num_classes = len(classes)
    print("Classes:", classes)

    train_df, val_df = train_test_split(df, test_size=0.1, stratify=df["label"], random_state=SEED)
    print(f"Train: {len(train_df)} | Val: {len(val_df)}")

    all_tokens = [t for txt in train_df["text"] for t in tokenize(txt)]
    vocab = {w: i + 2 for i, (w, _) in enumerate(Counter(all_tokens).most_common(MAX_VOCAB))}
    vocab["<PAD>"] = 0
    vocab["<UNK>"] = 1
    print("Vocab size:", len(vocab))

    def encode(text):
        tokens = tokenize(text)
        if len(tokens) == 0:
            tokens = ["<UNK>"]
        ids = [vocab.get(t, 1) for t in tokens[:MAX_LEN]]
        return torch.tensor(ids)

    class EmotionDataset(Dataset):
        def __init__(self, texts, labels):
            self.texts, self.labels = texts, labels
        def __len__(self): return len(self.texts)
        def __getitem__(self, i): return encode(self.texts[i]), int(self.labels[i])

    def collate_fn(batch):
        batch = [(x, y) for x, y in batch if len(x) > 0]
        if len(batch) == 0:
            return torch.zeros((1, 1), dtype=torch.long), torch.zeros(1, dtype=torch.long), torch.tensor([1])
        xs, ys = zip(*batch)
        lengths = [len(x) for x in xs]
        xs_padded = pad_sequence(xs, batch_first=True, padding_value=0)
        return xs_padded, torch.tensor(ys), torch.tensor(lengths)

    train_loader = DataLoader(EmotionDataset(train_df["text"].tolist(), train_df["label"].tolist()),
                              batch_size=BATCH_SIZE, shuffle=True, collate_fn=collate_fn)
    val_loader = DataLoader(EmotionDataset(val_df["text"].tolist(), val_df["label"].tolist()),
                            batch_size=BATCH_SIZE, shuffle=False, collate_fn=collate_fn)

    model = BiLSTMAttentionModel(len(vocab), EMBED_DIM, HIDDEN_DIM, N_LAYERS, num_classes, dropout=DROPOUT).to(DEVICE)
    print(model)

    class_weights = compute_class_weight("balanced", classes=np.arange(num_classes), y=train_df["label"])
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(class_weights, dtype=torch.float).to(DEVICE))
    optimizer = torch.optim.AdamW(model.parameters(), lr=LR, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode="max", factor=0.5, patience=3)

    best_val_acc, patience_counter = 0, 0
    patience = 6

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss, correct, total = 0, 0, 0

        for xb, yb, lengths in tqdm(train_loader, desc=f"Epoch {epoch}/{EPOCHS}"):
            xb, yb = xb.to(DEVICE), yb.to(DEVICE)
            optimizer.zero_grad()
            out = model(xb, lengths)
            loss = criterion(out, yb)
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()

            total_loss += loss.item() * xb.size(0)
            correct += (out.argmax(1) == yb).sum().item()
            total += yb.size(0)

        train_acc = correct / total
        train_loss = total_loss / total

        model.eval()
        val_correct, val_total, val_loss = 0, 0, 0
        with torch.no_grad():
            for xb, yb, lengths in val_loader:
                xb, yb = xb.to(DEVICE), yb.to(DEVICE)
                out = model(xb, lengths)
                loss = criterion(out, yb)
                val_loss += loss.item() * xb.size(0)
                val_correct += (out.argmax(1) == yb).sum().item()
                val_total += yb.size(0)

        val_acc = val_correct / val_total
        val_loss /= val_total
        scheduler.step(val_acc)

        print(f"Epoch {epoch:02d} | TrainAcc={train_acc:.4f} | ValAcc={val_acc:.4f} | TrainLoss={train_loss:.4f} | ValLoss={val_loss:.4f}")
        if val_acc > best_val_acc:
            best_val_acc = val_acc
            patience_counter = 0
            torch.save(model.state_dict(), f"{MODEL_DIR}/best_model.pth", _use_new_zipfile_serialization=True)
            with open(f"{MODEL_DIR}/vocab.pkl", "wb") as f:
                pickle.dump(vocab, f)
            with open(f"{MODEL_DIR}/label_encoder.pkl", "wb") as f:
                pickle.dump(le, f)
            print(f"✅ Saved best model & vocab: {best_val_acc:.4f}")
        else:
            patience_counter += 1
            if patience_counter >= patience:
                print("⏸ Early stopping.")
                break

    print(f"✅ Training complete. Best Validation Accuracy: {best_val_acc:.4f}")
