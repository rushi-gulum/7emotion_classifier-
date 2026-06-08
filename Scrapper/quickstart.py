# ========================================================
# Quick Start Guide for Twitter Emotion Scraper
# ========================================================

"""
Quick commands to get started with the scraper.
"""

import os
import sys

def print_header(text):
    """Print formatted header."""
    print(f"\n{'='*60}")
    print(f"  {text}")
    print('='*60)


def setup():
    """Setup and installation instructions."""
    print_header("🚀 SETUP & INSTALLATION")
    
    print("\n1️⃣  Install Dependencies:")
    print("   pip install -r requirements.txt")
    
    print("\n2️⃣  Verify ChromeDriver Installation:")
    print("   python -c \"from webdriver_manager.chrome import ChromeDriverManager; print('✅ ChromeDriver OK')\"")
    
    print("\n3️⃣  Start Flask Emotion Server (in separate terminal):")
    print("   cd ..")
    print("   python run_pipeline_server.py")
    print("   # Wait for: ✅ Model loaded on DEVICE")
    
    print("\n✅ Setup complete!")


def quick_commands():
    """Show quick command examples."""
    print_header("⚡ QUICK COMMANDS")
    
    print("\n1. Scrape Single Tweet (Easiest):")
    print("   python app.py --scrape https://x.com/user/status/123 --analyze")
    
    print("\n2. Scrape Multiple Tweets:")
    print("   python app.py --scrape URL1 URL2 URL3 --analyze --output results.csv")
    
    print("\n3. Add Emotions to Existing CSV:")
    print("   python app.py --csv scraped_data/replies.csv --analyze")
    
    print("\n4. Merge & Deduplicate Multiple CSVs:")
    print("   python app.py --merge file1.csv file2.csv file3.csv --output merged.csv")
    
    print("\n5. Show Browser Window (for debugging):")
    print("   python app.py --scrape URL --analyze --no-headless")
    
    print("\n6. Custom API URL:")
    print("   python app.py --scrape URL --api-url http://localhost:5000 --analyze")


def workflow():
    """Show example workflow."""
    print_header("🔄 EXAMPLE WORKFLOW")
    
    print("\nStep 1: Start emotion classifier (Terminal 1)")
    print("   cd ..")
    print("   python run_pipeline_server.py")
    print("   # Keep this running...\n")
    
    print("Step 2: Scrape tweets (Terminal 2)")
    print("   python app.py --scrape https://x.com/user/status/123 \\")
    print("       https://x.com/user/status/456 \\")
    print("       --analyze --output batch1.csv")
    print("   # Wait for completion...\n")
    
    print("Step 3: Check results")
    print("   head -20 scraped_data/batch1.csv")
    print("   # View emotion statistics displayed in console\n")
    
    print("Step 4: Generate report")
    print("   python")
    print("   from utils import generate_emotion_report")
    print("   generate_emotion_report('scraped_data/batch1.csv')")


def python_api():
    """Show Python API examples."""
    print_header("🐍 PYTHON API EXAMPLES")
    
    print("\nBasic Usage:")
    print("""
from app import ScraperApp

app = ScraperApp()

# Scrape and analyze
result = app.scrape_and_analyze(
    tweet_urls=["https://x.com/user/status/123"],
    analyze_emotions=True
)

print(f"Results: {result}")
    """)
    
    print("\nAdd Emotions to CSV:")
    print("""
app.process_csv_with_emotions(
    csv_path="scraped_data/replies.csv",
    output_path="scraped_data/replies_emotions.csv"
)
    """)
    
    print("\nDirect Scraper Usage:")
    print("""
from twitter_scraper import TwitterScraper

with TwitterScraper(headless=False) as scraper:
    result = scraper.scrape_tweet_with_replies(
        "https://x.com/user/status/123"
    )
    print(f"Collected {result['reply_count']} replies")
    """)


def troubleshooting():
    """Troubleshooting guide."""
    print_header("🔧 TROUBLESHOOTING")
    
    print("\n❌ Error: ChromeDriver not found")
    print("   ✅ Solution: pip install webdriver-manager")
    
    print("\n❌ Error: Connection refused (Flask API)")
    print("   ✅ Solution: Start Flask server: python run_pipeline_server.py")
    
    print("\n❌ Error: No replies extracted")
    print("   ✅ Solution: Try with --no-headless to debug:")
    print("      python app.py --scrape URL --no-headless")
    
    print("\n❌ Error: Timeout exception")
    print("   ✅ Solution: Increase EXPLICIT_WAIT in config.py")
    
    print("\n❌ Error: Encoding issues with CSV")
    print("   ✅ Solution: Ensure CSV is UTF-8 encoded")
    
    print("\n❌ Warning: Very slow scraping")
    print("   ✅ Solution: Use default headless mode (faster)")
    print("      Don't use --no-headless unless debugging")


def tips():
    """Useful tips and best practices."""
    print_header("💡 TIPS & BEST PRACTICES")
    
    print("\n⚡ Performance:")
    print("   • Use headless mode (default) for 2-3x speedup")
    print("   • Batch scrape multiple tweets instead of one-by-one")
    print("   • Use merge + deduplicate for large datasets")
    
    print("\n🎯 Accuracy:")
    print("   • Emotion classifier works best on complete sentences")
    print("   • Short/fragmented tweets may have lower accuracy")
    print("   • Check predictions manually for important decisions")
    
    print("\n📊 Data Management:")
    print("   • Always remove duplicates before analysis")
    print("   • Save intermediate results to avoid re-scraping")
    print("   • Use timestamps in CSV for tracking batch collection")
    
    print("\n⚠️  Legal:")
    print("   • Respect Twitter/X Terms of Service")
    print("   • Don't scrape at very high frequency")
    print("   • Use data responsibly and legally")
    
    print("\n🐛 Debugging:")
    print("   • Run with --no-headless to see browser")
    print("   • Check logs in console for detailed error messages")
    print("   • Test with simple tweet first before bulk scraping")


def file_structure():
    """Show file structure."""
    print_header("📁 FILE STRUCTURE")
    
    print("""
Scrapper/
├── app.py                    # Main application + CLI
├── twitter_scraper.py        # Selenium web scraper
├── utils.py                  # Utility functions
├── config.py                 # Configuration settings
├── examples.py               # Usage examples
├── quickstart.py             # This file
├── requirements.txt          # Dependencies
└── README.md                 # Full documentation

Generated Files:
scraped_data/
├── tweet_replies.csv         # Default output
├── batch1.csv
├── batch2.csv
└── merged_all.csv
    """)


def main():
    """Interactive quick start menu."""
    while True:
        print_header("🕷️  TWITTER EMOTION SCRAPER - QUICK START")
        
        print("\nSelect an option:")
        print("  1. Setup & Installation")
        print("  2. Quick Commands")
        print("  3. Example Workflow")
        print("  4. Python API Examples")
        print("  5. Troubleshooting")
        print("  6. Tips & Best Practices")
        print("  7. File Structure")
        print("  8. Exit")
        
        choice = input("\nEnter choice (1-8): ").strip()
        
        if choice == "1":
            setup()
        elif choice == "2":
            quick_commands()
        elif choice == "3":
            workflow()
        elif choice == "4":
            python_api()
        elif choice == "5":
            troubleshooting()
        elif choice == "6":
            tips()
        elif choice == "7":
            file_structure()
        elif choice == "8":
            print("\n✅ Goodbye!\n")
            break
        else:
            print("\n❌ Invalid choice. Try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "setup":
            setup()
        elif command == "commands":
            quick_commands()
        elif command == "workflow":
            workflow()
        elif command == "api":
            python_api()
        elif command == "troubleshoot":
            troubleshooting()
        elif command == "tips":
            tips()
        elif command == "files":
            file_structure()
        else:
            print("Usage: python quickstart.py [setup|commands|workflow|api|troubleshoot|tips|files]")
    else:
        main()
