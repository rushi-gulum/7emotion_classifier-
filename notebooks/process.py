import pandas as pd
import os

# ==============================
# CONFIGURATION
# ==============================
INPUT_FILE = "data/sample.csv"   # Path to your input dataset
OUTPUT_FILE = "data/goemotions_7class.csv"

# ==============================
# LABEL MAPPING
# ==============================
EMOTION_MAP = {
    # Joy-related
    "admiration": "joy", "amusement": "joy", "approval": "joy", "excitement": "joy",
    "gratitude": "joy", "love": "joy", "optimism": "joy", "pride": "joy", 
    "relief": "joy", "desire": "joy", "caring": "joy",

    # Anger-related
    "anger": "anger", "annoyance": "anger", "disapproval": "anger", "remorse": "anger",

    # Sadness-related
    "sadness": "sadness", "disappointment": "sadness", "grief": "sadness", "embarrassment": "sadness",

    # Fear-related
    "fear": "fear", "nervousness": "fear",

    # Surprise-related
    "surprise": "surprise", "realization": "surprise",

    # Disgust-related
    "disgust": "disgust",

    # Neutral
    "neutral": "neutral",
}

TARGET_CLASSES = ["joy", "anger", "sadness", "fear", "surprise", "disgust", "neutral"]

# ==============================
# CONVERSION FUNCTION
# ==============================
def convert_to_7class(input_path, output_path):
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"❌ Input file not found: {input_path}")

    print(f"📥 Loading dataset from: {input_path}")
    df = pd.read_csv(input_path)
    print(f"Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns")

    # Ensure the necessary columns exist
    text_col = "text" if "text" in df.columns else "comment_text"
    if text_col not in df.columns:
        raise ValueError("❌ No text column found (expected 'text' or 'comment_text').")

    # Map original emotion columns to 7 classes
    available_cols = [c for c in EMOTION_MAP.keys() if c in df.columns]
    print(f"✅ Found {len(available_cols)} label columns in dataset.")

    def map_emotion(row):
        for col, mapped in EMOTION_MAP.items():
            if col in df.columns and row[col] == 1:
                return mapped
        return None

    df["emotion"] = df.apply(map_emotion, axis=1)

    # Keep only useful rows and columns
    df_clean = df[[text_col, "emotion"]].dropna().rename(columns={text_col: "text"})
    df_clean = df_clean[df_clean["emotion"].isin(TARGET_CLASSES)]

    print(f"✅ Filtered dataset: {df_clean.shape[0]} valid rows with target emotions.")
    print("Class distribution:")
    print(df_clean["emotion"].value_counts())

    # Save the cleaned dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df_clean.to_csv(output_path, index=False)
    print(f"💾 Saved converted dataset to: {output_path}")

# ==============================
# RUN CONVERSION
# ==============================
if __name__ == "__main__":
    convert_to_7class(INPUT_FILE, OUTPUT_FILE)
