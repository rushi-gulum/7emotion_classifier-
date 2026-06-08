import torch
from main_train import TextCNN, encode, vocab, le, DEVICE

# Load model
model = TextCNN(len(vocab), 128, len(le.classes_))
model.load_state_dict(torch.load("models/textcnn_emotion.pth", map_location=DEVICE))
model.to(DEVICE)
model.eval()

def predict_emotion(text):
    ids = torch.tensor([encode(text)], dtype=torch.long).to(DEVICE)
    with torch.no_grad():
        out = model(ids)
        pred = out.argmax(1).item()
    return le.classes_[pred]

print("✅ Model loaded successfully!")

while True:
    txt = input("\nEnter a comment (or type 'exit'): ")
    if txt.lower() == "exit":
        break
    print("Predicted Emotion:", predict_emotion(txt))
