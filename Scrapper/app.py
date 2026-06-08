# ========================================================
# Main Scraper Application - Integration Layer
# ========================================================

import os
import sys
import argparse
import logging
from typing import List
from pathlib import Path

from twitter_scraper import TwitterScraper
from utils import (
    save_to_csv, load_from_csv, classify_emotions, remove_duplicates,
    print_scraping_stats, generate_emotion_report, process_in_batches,
    merge_csvs
)
from config import OUTPUT_DIR, CSV_FILENAME, BATCH_SIZE, FLASK_API_URL

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ScraperApp:
    """Main application for scraping and analyzing tweets."""
    
    def __init__(self, api_url: str = FLASK_API_URL, output_dir: str = OUTPUT_DIR):
        """
        Initialize scraper app.
        
        Args:
            api_url: Flask emotion classifier API URL
            output_dir: Directory for output files
        """
        self.api_url = api_url
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    def scrape_and_analyze(self, tweet_urls: List[str], output_file: str = None,
                           analyze_emotions: bool = True, headless: bool = True) -> str:
        """
        Scrape tweets and optionally analyze emotions.
        
        Args:
            tweet_urls: List of tweet URLs to scrape
            output_file: Output CSV filename (default: tweet_replies.csv)
            analyze_emotions: Whether to classify emotions
            headless: Run browser in headless mode
        
        Returns:
            Path to output CSV file
        """
        if not output_file:
            output_file = CSV_FILENAME
        
        output_path = os.path.join(self.output_dir, output_file)
        
        try:
            # Step 1: Scrape tweets
            logger.info(f"\n{'='*60}")
            logger.info("STEP 1: SCRAPING TWEETS")
            logger.info('='*60)
            
            with TwitterScraper(headless=headless) as scraper:
                results = scraper.scrape_multiple_tweets(tweet_urls)
                flattened = scraper.flatten_results(results)
            
            if not flattened:
                logger.error("No data scraped")
                return ""
            
            logger.info(f"✅ Scraped {len(flattened)} replies")
            
            # Step 2: Remove duplicates
            logger.info(f"\n{'='*60}")
            logger.info("STEP 2: REMOVING DUPLICATES")
            logger.info('='*60)
            
            unique_data, removed = remove_duplicates(flattened)
            logger.info(f"✅ {removed} duplicates removed, {len(unique_data)} unique records")
            
            # Step 3: Classify emotions (optional)
            if analyze_emotions:
                logger.info(f"\n{'='*60}")
                logger.info("STEP 3: ANALYZING EMOTIONS")
                logger.info('='*60)
                
                texts = [record['text'] for record in unique_data]
                emotions = classify_emotions(texts, self.api_url)
                
                if emotions and len(emotions) == len(unique_data):
                    for record, emotion in zip(unique_data, emotions):
                        record['emotion'] = emotion
                    logger.info(f"✅ Classified {len(emotions)} texts")
                else:
                    logger.warning("⚠️  Could not classify emotions, saving without emotion labels")
            
            # Step 4: Save to CSV
            logger.info(f"\n{'='*60}")
            logger.info("STEP 4: SAVING RESULTS")
            logger.info('='*60)
            
            save_to_csv(unique_data, output_path, include_timestamp=True)
            
            # Step 5: Print statistics
            logger.info(f"\n{'='*60}")
            logger.info("STEP 5: STATISTICS")
            logger.info('='*60)
            
            print_scraping_stats(unique_data)
            
            if analyze_emotions and 'emotion' in unique_data[0]:
                generate_emotion_report(output_path)
            
            return output_path
        
        except Exception as e:
            logger.error(f"❌ Error during scraping: {e}")
            return ""
    
    def process_csv_with_emotions(self, csv_path: str, output_path: str = None) -> str:
        """
        Load CSV and add emotion classifications.
        
        Args:
            csv_path: Path to input CSV
            output_path: Path to output CSV (default: same dir, _emotions suffix)
        
        Returns:
            Path to output CSV
        """
        if not output_path:
            base_path = csv_path.replace('.csv', '')
            output_path = f"{base_path}_emotions.csv"
        
        try:
            logger.info(f"Loading CSV: {csv_path}")
            data = load_from_csv(csv_path)
            
            if not data:
                logger.error("No data loaded from CSV")
                return ""
            
            logger.info(f"✅ Loaded {len(data)} records")
            
            # Extract texts and classify
            texts = [record.get('text', '') for record in data if record.get('text')]
            
            logger.info(f"\nClassifying emotions for {len(texts)} texts...")
            emotions = classify_emotions(texts, self.api_url)
            
            if emotions and len(emotions) == len(data):
                for record, emotion in zip(data, emotions):
                    record['emotion'] = emotion
                
                logger.info(f"✅ Classified {len(emotions)} texts")
            else:
                logger.warning("⚠️  Could not classify all texts")
            
            # Save
            save_to_csv(data, output_path, include_timestamp=False)
            generate_emotion_report(output_path)
            
            return output_path
        
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            return ""
    
    def merge_and_analyze(self, csv_files: List[str], output_file: str = "merged_replies.csv") -> str:
        """
        Merge multiple CSV files and generate emotion report.
        
        Args:
            csv_files: List of CSV file paths
            output_file: Output filename
        
        Returns:
            Path to merged CSV
        """
        output_path = os.path.join(self.output_dir, output_file)
        
        try:
            merged_path = merge_csvs(csv_files, output_path)
            
            if merged_path:
                generate_emotion_report(merged_path)
            
            return merged_path
        
        except Exception as e:
            logger.error(f"❌ Error merging files: {e}")
            return ""


def main():
    """Command-line interface for scraper."""
    parser = argparse.ArgumentParser(
        description="🧠 Tweet Emotion Scraper & Analyzer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape a single tweet with emotion analysis
  python app.py --scrape https://x.com/user/status/123 --analyze

  # Scrape multiple tweets
  python app.py --scrape https://x.com/user1/status/123 https://x.com/user2/status/456

  # Add emotions to existing CSV
  python app.py --csv scraped_data/replies.csv --analyze

  # Merge multiple CSVs
  python app.py --merge file1.csv file2.csv file3.csv --output merged.csv

  # Run headless (no browser window)
  python app.py --scrape <URL> --headless
        """
    )
    
    parser.add_argument('--scrape', nargs='+',
                        help='Tweet URL(s) to scrape')
    parser.add_argument('--csv', type=str,
                        help='Path to CSV file for emotion analysis')
    parser.add_argument('--merge', nargs='+',
                        help='CSV files to merge')
    parser.add_argument('--analyze', action='store_true',
                        help='Classify emotions using Flask API')
    parser.add_argument('--output', '-o', type=str,
                        help='Output filename')
    parser.add_argument('--api-url', type=str, default=FLASK_API_URL,
                        help=f'Flask API URL (default: {FLASK_API_URL})')
    parser.add_argument('--output-dir', type=str, default=OUTPUT_DIR,
                        help=f'Output directory (default: {OUTPUT_DIR})')
    parser.add_argument('--no-headless', action='store_true',
                        help='Show browser window (for debugging)')
    
    args = parser.parse_args()
    
    app = ScraperApp(api_url=args.api_url, output_dir=args.output_dir)
    headless = not args.no_headless
    
    # Scrape tweets
    if args.scrape:
        logger.info(f"Scraping {len(args.scrape)} tweet(s)...")
        output_file = args.output or CSV_FILENAME
        result = app.scrape_and_analyze(
            args.scrape,
            output_file=output_file,
            analyze_emotions=args.analyze,
            headless=headless
        )
        
        if result:
            print(f"\n✅ Results saved to: {result}")
    
    # Analyze existing CSV
    elif args.csv:
        if not os.path.exists(args.csv):
            logger.error(f"CSV file not found: {args.csv}")
            return
        
        output_file = args.output or f"{os.path.basename(args.csv).replace('.csv', '')}_emotions.csv"
        result = app.process_csv_with_emotions(args.csv, output_file)
        
        if result:
            print(f"\n✅ Results saved to: {result}")
    
    # Merge CSVs
    elif args.merge:
        logger.info(f"Merging {len(args.merge)} CSV file(s)...")
        output_file = args.output or "merged_replies.csv"
        result = app.merge_and_analyze(args.merge, output_file)
        
        if result:
            print(f"\n✅ Merged file saved to: {result}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
