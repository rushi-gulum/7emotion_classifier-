# ========================================================
# Usage Examples for Twitter Emotion Scraper
# ========================================================

"""
This file demonstrates various ways to use the scraper.
Run each function to see examples in action.
"""

from app import ScraperApp
from twitter_scraper import TwitterScraper
from utils import (
    classify_emotions, analyze_emotion_distribution,
    save_to_csv, load_from_csv, print_scraping_stats,
    merge_csvs, remove_duplicates
)
from config import FLASK_API_URL, OUTPUT_DIR


# ========= EXAMPLE 1: Simple Scrape & Analyze ==========
def example_1_basic_scrape():
    """Scrape a single tweet with emotion analysis."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Scrape with Emotion Analysis")
    print("="*60)
    
    app = ScraperApp()
    
    tweet_url = "https://x.com/user/status/1234567890"  # Replace with real URL
    
    result = app.scrape_and_analyze(
        tweet_urls=[tweet_url],
        output_file="example1_replies.csv",
        analyze_emotions=True,
        headless=True
    )
    
    print(f"✅ Results saved to: {result}")


# ========= EXAMPLE 2: Scrape Multiple Tweets ==========
def example_2_multiple_tweets():
    """Scrape multiple tweets at once."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Scrape Multiple Tweets")
    print("="*60)
    
    app = ScraperApp()
    
    tweet_urls = [
        "https://x.com/user1/status/111",
        "https://x.com/user2/status/222",
        "https://x.com/user3/status/333",
    ]
    
    result = app.scrape_and_analyze(
        tweet_urls=tweet_urls,
        output_file="example2_multi_tweets.csv",
        analyze_emotions=True,
        headless=True
    )
    
    print(f"✅ Results saved to: {result}")


# ========= EXAMPLE 3: Scrape Without Emotions ==========
def example_3_scrape_no_emotions():
    """Scrape tweets without emotion classification."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Scrape Without Emotion Analysis")
    print("="*60)
    
    app = ScraperApp()
    
    tweet_url = "https://x.com/user/status/1234567890"  # Replace with real URL
    
    result = app.scrape_and_analyze(
        tweet_urls=[tweet_url],
        output_file="example3_no_emotions.csv",
        analyze_emotions=False,  # Skip emotion analysis
        headless=True
    )
    
    print(f"✅ Results saved to: {result}")


# ========= EXAMPLE 4: Add Emotions to Existing CSV ==========
def example_4_add_emotions():
    """Add emotion classifications to existing CSV."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Add Emotions to Existing CSV")
    print("="*60)
    
    app = ScraperApp()
    
    csv_path = "scraped_data/example1_replies.csv"  # Must exist
    
    result = app.process_csv_with_emotions(
        csv_path=csv_path,
        output_path="scraped_data/example4_with_emotions.csv"
    )
    
    print(f"✅ Results saved to: {result}")


# ========= EXAMPLE 5: Direct Scraper Usage ==========
def example_5_direct_scraper():
    """Use TwitterScraper class directly for more control."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Direct TwitterScraper Usage")
    print("="*60)
    
    tweet_url = "https://x.com/user/status/1234567890"  # Replace with real URL
    
    try:
        with TwitterScraper(headless=True) as scraper:
            # Scrape the tweet
            result = scraper.scrape_tweet_with_replies(tweet_url)
            
            print(f"\nTweet: {result['tweet_text']}")
            print(f"Replies collected: {result['reply_count']}")
            
            # Flatten results
            flattened = scraper.flatten_results([result])
            
            # Optionally classify emotions
            texts = [r['text'] for r in flattened]
            emotions = classify_emotions(texts, FLASK_API_URL)
            
            print(f"\nEmotion classifications:")
            for text, emotion in zip(texts[:3], emotions[:3]):
                print(f"  '{text[:50]}...' → {emotion}")
    
    except Exception as e:
        print(f"Error: {e}")


# ========= EXAMPLE 6: Batch Processing ==========
def example_6_batch_processing():
    """Process results in batches for memory efficiency."""
    print("\n" + "="*60)
    print("EXAMPLE 6: Batch Processing Large Results")
    print("="*60)
    
    from utils import process_in_batches
    
    # Simulate large result set
    sample_data = [
        {"text": f"Sample tweet {i}", "author": "N/A", "emotion": None}
        for i in range(100)
    ]
    
    texts = [r['text'] for r in sample_data]
    
    # Process in batches
    all_emotions = []
    for batch in process_in_batches(texts, batch_size=32):
        print(f"Processing batch of {len(batch)} texts...")
        emotions = classify_emotions(batch, FLASK_API_URL)
        all_emotions.extend(emotions)
    
    print(f"✅ Processed {len(all_emotions)} texts in batches")


# ========= EXAMPLE 7: Merge Multiple CSVs ==========
def example_7_merge_csvs():
    """Merge multiple CSV files and deduplicate."""
    print("\n" + "="*60)
    print("EXAMPLE 7: Merge Multiple CSVs")
    print("="*60)
    
    app = ScraperApp()
    
    csv_files = [
        "scraped_data/batch1.csv",
        "scraped_data/batch2.csv",
        "scraped_data/batch3.csv",
    ]
    
    result = app.merge_and_analyze(
        csv_files=csv_files,
        output_file="scraped_data/merged_all.csv"
    )
    
    print(f"✅ Merged results saved to: {result}")


# ========= EXAMPLE 8: Remove Duplicates ==========
def example_8_remove_duplicates():
    """Load CSV and remove duplicate texts."""
    print("\n" + "="*60)
    print("EXAMPLE 8: Remove Duplicates from CSV")
    print("="*60)
    
    csv_path = "scraped_data/example1_replies.csv"
    
    # Load
    data = load_from_csv(csv_path)
    print(f"Original records: {len(data)}")
    
    # Remove duplicates
    unique_data, removed = remove_duplicates(data, key='text')
    print(f"After deduplication: {len(unique_data)} unique records")
    print(f"Duplicates removed: {removed}")
    
    # Save
    save_to_csv(unique_data, "scraped_data/example8_deduplicated.csv")


# ========= EXAMPLE 9: Emotion Distribution Analysis ==========
def example_9_emotion_analysis():
    """Analyze emotion distribution from CSV."""
    print("\n" + "="*60)
    print("EXAMPLE 9: Emotion Distribution Analysis")
    print("="*60)
    
    csv_path = "scraped_data/example1_replies.csv"
    
    # Load
    data = load_from_csv(csv_path)
    print_scraping_stats(data)
    
    # Get emotion distribution
    texts = [r['text'] for r in data if r.get('text')]
    dist = analyze_emotion_distribution(texts, FLASK_API_URL)
    
    print(f"\n🎭 Emotion Distribution:")
    for emotion, count in sorted(dist.items(), key=lambda x: x[1], reverse=True):
        print(f"  {emotion:<12}: {count:>3}")


# ========= EXAMPLE 10: Custom Workflow ==========
def example_10_custom_workflow():
    """Implement a custom workflow combining multiple operations."""
    print("\n" + "="*60)
    print("EXAMPLE 10: Custom Workflow")
    print("="*60)
    
    app = ScraperApp()
    
    # 1. Scrape tweets
    print("\n1️⃣  Scraping tweets...")
    csv1 = app.scrape_and_analyze(
        tweet_urls=["https://x.com/user/status/123"],
        output_file="workflow_batch1.csv",
        analyze_emotions=False  # Skip for now
    )
    
    # 2. Load and analyze emotions
    print("\n2️⃣  Adding emotion analysis...")
    csv2 = app.process_csv_with_emotions(
        csv_path=csv1,
        output_path="workflow_batch1_emotions.csv"
    )
    
    # 3. Load results
    data = load_from_csv(csv2)
    
    # 4. Print statistics
    print("\n3️⃣  Final statistics...")
    print_scraping_stats(data)
    
    print(f"\n✅ Workflow completed! Results: {csv2}")


# ========= EXAMPLE 11: Emotion API Direct Usage ==========
def example_11_emotion_api():
    """Use emotion classification API directly."""
    print("\n" + "="*60)
    print("EXAMPLE 11: Direct Emotion API Usage")
    print("="*60)
    
    sample_texts = [
        "I absolutely love this!",
        "This is terrible and I hate it.",
        "I'm not sure about this.",
        "I'm so afraid of what might happen.",
        "That's disgusting!",
        "Wow, what a surprise!",
    ]
    
    print(f"Classifying {len(sample_texts)} texts...")
    emotions = classify_emotions(sample_texts, FLASK_API_URL)
    
    print(f"\n🎭 Results:")
    for text, emotion in zip(sample_texts, emotions):
        print(f"  '{text}' → {emotion}")


# ========= EXAMPLE 12: Headless vs Non-Headless ==========
def example_12_headless_comparison():
    """Compare headless vs non-headless modes."""
    print("\n" + "="*60)
    print("EXAMPLE 12: Headless vs Non-Headless")
    print("="*60)
    
    print("\nHeadless Mode (Recommended - Faster):")
    print("  - No browser window shown")
    print("  - ~2-3x faster")
    print("  - Better for servers/automation")
    print("  - Usage: python app.py --scrape <URL> --analyze")
    
    print("\nNon-Headless Mode (Debugging):")
    print("  - Shows browser window")
    print("  - Slower but visible")
    print("  - Good for troubleshooting")
    print("  - Usage: python app.py --scrape <URL> --analyze --no-headless")


# ========= MAIN ==========
if __name__ == "__main__":
    print("\n" + "="*60)
    print("🕷️  Twitter Emotion Scraper - Usage Examples")
    print("="*60)
    
    print("\nAvailable examples:")
    print("  1. example_1_basic_scrape() - Basic scrape + analysis")
    print("  2. example_2_multiple_tweets() - Scrape multiple tweets")
    print("  3. example_3_scrape_no_emotions() - Scrape without emotions")
    print("  4. example_4_add_emotions() - Add emotions to CSV")
    print("  5. example_5_direct_scraper() - Direct scraper usage")
    print("  6. example_6_batch_processing() - Batch processing")
    print("  7. example_7_merge_csvs() - Merge multiple CSVs")
    print("  8. example_8_remove_duplicates() - Remove duplicates")
    print("  9. example_9_emotion_analysis() - Emotion analysis")
    print("  10. example_10_custom_workflow() - Custom workflow")
    print("  11. example_11_emotion_api() - Direct API usage")
    print("  12. example_12_headless_comparison() - Mode comparison")
    
    print("\nUsage:")
    print("  from examples import example_1_basic_scrape")
    print("  example_1_basic_scrape()")
    
    print("\n" + "="*60)
