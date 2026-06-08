# ========================================================
# Utility Functions for Twitter Scraper
# ========================================================

import os
import csv
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ========= TEXT CLEANING =========
def clean_text(text: str) -> str:
    """
    Clean tweet text: remove URLs, mentions, hashtags, extra spaces.
    
    Args:
        text: Raw tweet text
    
    Returns:
        Cleaned text
    """
    if not isinstance(text, str):
        return ""
    
    text = str(text).lower().strip()
    # Remove URLs
    import re
    text = re.sub(r"http\S+|www\S+", "", text)
    # Remove mentions and hashtags
    text = re.sub(r"@\S+|#\S+", "", text)
    # Remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()
    
    return text


def filter_empty_texts(texts: List[str]) -> List[str]:
    """Remove empty strings and texts with only whitespace."""
    return [t.strip() for t in texts if t.strip()]


def validate_url(url: str) -> bool:
    """Validate if URL is a valid Twitter/X post URL."""
    import re
    twitter_pattern = r"(https?://)?(www\.)?(twitter\.com|x\.com)/\w+/status/\d+"
    return bool(re.match(twitter_pattern, url))


# ========= API COMMUNICATION =========
def send_to_emotion_api(texts: List[str], endpoint: str, api_url: str) -> Dict:
    """
    Send texts to Flask emotion classifier API.
    
    Args:
        texts: List of text strings to classify
        endpoint: API endpoint ("/analyze" or "/label_texts")
        api_url: Base API URL (e.g., "http://127.0.0.1:5001")
    
    Returns:
        API response as dictionary
    """
    if not texts:
        logger.warning("No texts to send to API")
        return {}
    
    try:
        url = f"{api_url.rstrip('/')}{endpoint}"
        payload = {"texts": texts}
        
        logger.info(f"Sending {len(texts)} texts to {url}")
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        
        logger.info(f"✅ API response: {response.status_code}")
        return response.json()
    
    except requests.exceptions.ConnectionError:
        logger.error(f"❌ Failed to connect to API at {api_url}")
        logger.error("Make sure Flask server is running: python run_pipeline_server.py")
        return {}
    
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ API request error: {e}")
        return {}


def classify_emotions(texts: List[str], api_url: str) -> List[str]:
    """
    Classify emotions for a list of texts.
    
    Args:
        texts: List of text strings
        api_url: Base API URL
    
    Returns:
        List of emotion labels in same order as input
    """
    response = send_to_emotion_api(texts, "/label_texts", api_url)
    return response.get("labels", [])


def analyze_emotion_distribution(texts: List[str], api_url: str) -> Dict:
    """
    Get emotion distribution (counts) for a list of texts.
    
    Args:
        texts: List of text strings
        api_url: Base API URL
    
    Returns:
        Dictionary with emotion counts
    """
    response = send_to_emotion_api(texts, "/analyze", api_url)
    return response.get("counts", {})


# ========= CSV HANDLING =========
def save_to_csv(data: List[Dict], output_path: str, include_timestamp: bool = True) -> str:
    """
    Save scraped data to CSV file.
    
    Args:
        data: List of dictionaries with tweet data
        output_path: Output file path
        include_timestamp: Whether to include collection timestamp
    
    Returns:
        Path to saved file
    """
    if not data:
        logger.warning("No data to save")
        return ""
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_path)
    if output_dir:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        df = pd.DataFrame(data)
        
        if include_timestamp:
            df.insert(0, 'scraped_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        
        df.to_csv(output_path, index=False, encoding='utf-8')
        logger.info(f"✅ Saved {len(data)} records to {output_path}")
        
        return output_path
    
    except Exception as e:
        logger.error(f"❌ Error saving to CSV: {e}")
        return ""


def load_from_csv(csv_path: str) -> List[Dict]:
    """Load data from CSV file."""
    try:
        df = pd.read_csv(csv_path)
        logger.info(f"✅ Loaded {len(df)} records from {csv_path}")
        return df.to_dict('records')
    except Exception as e:
        logger.error(f"❌ Error loading CSV: {e}")
        return []


def merge_csvs(csv_paths: List[str], output_path: str) -> str:
    """Merge multiple CSV files into one."""
    dfs = []
    for path in csv_paths:
        try:
            df = pd.read_csv(path)
            dfs.append(df)
            logger.info(f"✅ Loaded {path}")
        except Exception as e:
            logger.error(f"❌ Error loading {path}: {e}")
    
    if not dfs:
        logger.error("No valid CSV files to merge")
        return ""
    
    merged = pd.concat(dfs, ignore_index=True)
    merged = merged.drop_duplicates(subset=['text'], keep='first')
    
    merged.to_csv(output_path, index=False, encoding='utf-8')
    logger.info(f"✅ Merged {len(dfs)} files into {output_path} ({len(merged)} unique records)")
    
    return output_path


# ========= STATS & REPORTING =========
def print_scraping_stats(data: List[Dict]):
    """Print statistics about scraped data."""
    if not data:
        logger.warning("No data to analyze")
        return
    
    df = pd.DataFrame(data)
    
    print("\n" + "="*60)
    print("📊 SCRAPING STATISTICS")
    print("="*60)
    print(f"Total records scraped: {len(df)}")
    
    if 'emotion' in df.columns:
        emotion_counts = df['emotion'].value_counts().to_dict()
        print(f"\n🎭 Emotion Distribution:")
        for emotion, count in sorted(emotion_counts.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / len(df)) * 100
            print(f"  {emotion:<12}: {count:>4} ({percentage:>5.1f}%)")
    
    if 'author' in df.columns:
        print(f"\nUnique authors: {df['author'].nunique()}")
    
    if 'text' in df.columns:
        avg_text_len = df['text'].str.len().mean()
        print(f"Average text length: {avg_text_len:.0f} characters")
    
    print("="*60 + "\n")


def generate_emotion_report(csv_path: str) -> str:
    """Generate emotion analysis report from CSV."""
    df = pd.read_csv(csv_path)
    
    if 'emotion' not in df.columns:
        logger.error("CSV doesn't have 'emotion' column")
        return ""
    
    report_lines = [
        "\n" + "="*60,
        "📊 EMOTION ANALYSIS REPORT",
        "="*60,
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Total texts: {len(df)}",
        "\n🎭 Emotion Distribution:"
    ]
    
    emotion_counts = df['emotion'].value_counts()
    for emotion, count in emotion_counts.items():
        percentage = (count / len(df)) * 100
        bar = "█" * int(percentage / 2)
        report_lines.append(f"  {emotion:<12}: {count:>4} ({percentage:>5.1f}%) {bar}")
    
    report_lines.append("="*60)
    
    report = "\n".join(report_lines)
    print(report)
    
    return report


# ========= DUPLICATE DETECTION =========
def remove_duplicates(data: List[Dict], key: str = 'text') -> Tuple[List[Dict], int]:
    """
    Remove duplicate records based on key field.
    
    Returns:
        Tuple of (cleaned_data, num_removed)
    """
    seen = set()
    unique_data = []
    removed_count = 0
    
    for record in data:
        value = record.get(key, "")
        if value not in seen:
            seen.add(value)
            unique_data.append(record)
        else:
            removed_count += 1
    
    logger.info(f"Removed {removed_count} duplicate records")
    return unique_data, removed_count


# ========= BATCH PROCESSING =========
def process_in_batches(items: List, batch_size: int = 32):
    """Generator to process items in batches."""
    for i in range(0, len(items), batch_size):
        yield items[i:i + batch_size]
