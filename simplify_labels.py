import pandas as pd

# Load merged dataset
df = pd.read_csv("data/merged_dataset.csv")

# Define mapping
emotion_map = {
    'joy': 'joy',
    'amusement': 'joy',
    'excitement': 'joy',
    'love': 'joy',
    'gratitude': 'joy',
    'optimism': 'joy',
    'caring': 'joy',

    'sadness': 'sadness',
    'grief': 'sadness',
    'remorse': 'sadness',
    'disappointment': 'sadness',
    'embarrassment': 'sadness',

    'anger': 'anger',
    'annoyance': 'anger',
    'disapproval': 'anger',

    'fear': 'fear',
    'nervousness': 'fear',

    'surprise': 'surprise',
    'realization': 'surprise',

    'disgust': 'disgust',

    # everything else goes to neutral
    'neutral': 'neutral',
    'approval': 'neutral',
    'admiration': 'neutral',
    'curiosity': 'neutral',
    'pride': 'neutral',
    'desire': 'neutral',
    'relief': 'neutral',
}

# Apply mapping
df['emotion'] = df['emotion'].map(lambda x: emotion_map.get(str(x).lower(), 'neutral'))

# Show result
print("Unique emotions after mapping:", df['emotion'].unique())
print("Counts:\n", df['emotion'].value_counts())

# Save new version
df.to_csv("data/merged_simplified.csv", index=False)
print("✅ Saved simplified dataset as data/merged_simplified.csv")
