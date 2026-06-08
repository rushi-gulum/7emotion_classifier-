import pandas as pd
from sklearn.model_selection import train_test_split
from utils.preprocessing import clean_text

def load_and_prepare_data(path: str, test_size: float = 0.1, random_state: int = 42):
    """
    Loads dataset, cleans text, drops NaN rows, and splits into train/test.
    """
    print(f"🔹 Loading dataset from: {path}")
    df = pd.read_csv(path)

    # Ensure required columns exist
    if "tweet" not in df.columns or "emotion" not in df.columns:
        raise ValueError("Dataset must contain 'tweet' and 'emotion' columns.")

    # Clean text
    df["tweet"] = df["tweet"].astype(str).apply(clean_text)
    df.dropna(subset=["tweet", "emotion"], inplace=True)

    # Split
    train_df, test_df = train_test_split(
        df, test_size=test_size, stratify=df["emotion"], random_state=random_state
    )

    print(f"✅ Data loaded successfully: {len(train_df)} train, {len(test_df)} test samples")
    return train_df, test_df
