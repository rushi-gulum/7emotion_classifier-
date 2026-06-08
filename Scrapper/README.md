# 🕷️ Twitter/X Emotion Scraper

**Automated scraper for Twitter/X tweets and replies with integrated emotion analysis.**

Scrape tweet replies, remove duplicates, classify emotions, and save results to CSV—all in one workflow.

---

## ✨ Features

- ✅ **Scrape tweets & replies** using Selenium
- ✅ **Remove duplicates** automatically
- ✅ **Classify emotions** using Flask emotion classifier
- ✅ **Batch processing** with configurable batch sizes
- ✅ **Multiple output formats** (CSV with timestamps)
- ✅ **Emotion distribution reports** with statistics
- ✅ **Merge multiple CSVs** and deduplicate
- ✅ **CLI interface** for easy automation
- ✅ **Headless mode** for server deployments
- ✅ **Comprehensive logging** for debugging

---

## 🏗️ Architecture

```
Tweet URLs
    │
    ├─▶ Selenium WebDriver
    │      └─▶ Navigate to tweet
    │      └─▶ Scroll to load replies
    │      └─▶ Extract reply texts
    │
    ├─▶ Text Cleaning & Filtering
    │      └─▶ Remove URLs, mentions, hashtags
    │      └─▶ Remove duplicates
    │
    ├─▶ Flask Emotion Classifier API
    │      └─▶ Classify 7 emotions
    │
    └─▶ Save to CSV + Generate Report
           └─▶ Emotion distribution stats
```

---

## 📦 Installation

### Step 1: Install Dependencies

```bash
cd Scrapper
pip install -r requirements.txt
```

### Step 2: Download ChromeDriver

```bash
pip install webdriver-manager
```

The `webdriver-manager` package automatically downloads the correct ChromeDriver version.

### Step 3: Ensure Flask Server is Running

```bash
# From parent directory
python run_pipeline_server.py
```

Flask will start at `http://127.0.0.1:5001`

---

## 🔧 Configuration

Edit `config.py` to customize settings:

```python
# Browser settings
HEADLESS = True  # Run browser in headless mode
IMPLICIT_WAIT = 10  # Wait time for elements
PAGE_LOAD_TIMEOUT = 30  # Page load timeout

# Scraping settings
MAX_SCROLLS = 5  # Maximum scroll attempts
SCROLL_PAUSE_TIME = 2  # Seconds between scrolls

# API settings
FLASK_API_URL = "http://127.0.0.1:5001"

# Output settings
OUTPUT_DIR = "scraped_data"
CSV_FILENAME = "tweet_replies.csv"
BATCH_SIZE = 32
```

---

## 🚀 Usage

### Command-Line Interface

#### Scrape Single Tweet
```bash
python app.py --scrape https://x.com/user/status/123 --analyze
```

#### Scrape Multiple Tweets
```bash
python app.py --scrape https://x.com/user1/status/123 https://x.com/user2/status/456 --analyze
```

#### Add Emotions to Existing CSV
```bash
python app.py --csv scraped_data/replies.csv --analyze
```

#### Merge Multiple CSVs
```bash
python app.py --merge file1.csv file2.csv file3.csv --output merged.csv
```

#### Show Browser Window (for debugging)
```bash
python app.py --scrape <URL> --analyze --no-headless
```

#### Specify Custom API URL
```bash
python app.py --scrape <URL> --analyze --api-url http://localhost:5000
```

---

## 📝 Python API

### Basic Scraping

```python
from app import ScraperApp

app = ScraperApp()

# Scrape and analyze
output_path = app.scrape_and_analyze(
    tweet_urls=["https://x.com/user/status/123"],
    output_file="replies.csv",
    analyze_emotions=True,
    headless=True
)

print(f"Results saved to: {output_path}")
```

### Add Emotions to CSV

```python
from app import ScraperApp

app = ScraperApp()

result = app.process_csv_with_emotions(
    csv_path="scraped_data/replies.csv",
    output_path="scraped_data/replies_emotions.csv"
)
```

### Merge CSVs

```python
from app import ScraperApp

app = ScraperApp()

merged = app.merge_and_analyze(
    csv_files=["file1.csv", "file2.csv", "file3.csv"],
    output_file="merged_all.csv"
)
```

### Direct Scraper Usage

```python
from twitter_scraper import TwitterScraper

with TwitterScraper(headless=False) as scraper:
    result = scraper.scrape_tweet_with_replies(
        "https://x.com/user/status/123"
    )
    
    print(f"Tweet: {result['tweet_text']}")
    print(f"Replies: {result['reply_count']}")
    
    flattened = scraper.flatten_results([result])
    # Now have list of reply records
```

---

## 📊 Output Format

### CSV Columns

| Column | Type | Description |
|--------|------|-------------|
| `scraped_at` | datetime | When the data was scraped |
| `text` | string | Reply text (cleaned) |
| `author` | string | Tweet author (N/A if not extracted) |
| `tweet_url` | string | URL of the original tweet |
| `source` | string | Scraper type ("twitter_scraper") |
| `emotion` | string | Predicted emotion (if analyzed) |

### Example CSV

```csv
scraped_at,text,author,tweet_url,source,emotion
2024-06-09 10:30:45,this is absolutely wonderful,N/A,https://x.com/user/status/123,twitter_scraper,joy
2024-06-09 10:30:45,really disappointed with this,N/A,https://x.com/user/status/123,twitter_scraper,sadness
```

---

## 📈 Output Example

```
============================================================
STEP 1: SCRAPING TWEETS
============================================================
Navigating to: https://x.com/user/status/123
✅ Page loaded
📝 Tweet text: This is a great project...
Scroll 1/5 completed
Scroll 2/5 completed
✅ Extracted 42 replies

============================================================
STEP 2: REMOVING DUPLICATES
============================================================
✅ 2 duplicates removed, 40 unique records

============================================================
STEP 3: ANALYZING EMOTIONS
============================================================
Sending 40 texts to http://127.0.0.1:5001/label_texts
✅ API response: 200
✅ Classified 40 texts

============================================================
STEP 4: SAVING RESULTS
============================================================
✅ Saved 40 records to scraped_data/tweet_replies.csv

============================================================
STEP 5: STATISTICS
============================================================
📊 SCRAPING STATISTICS
============================================================
Total records scraped: 40

🎭 Emotion Distribution:
  joy        →   15 ( 37.5%)
  neutral    →   12 ( 30.0%)
  sadness    →    8 ( 20.0%)
  anger      →    5 ( 12.5%)

Average text length: 120 characters
============================================================
```

---

## 🔍 Module Overview

### `config.py`
Configuration file with all customizable settings.

### `utils.py`
Utility functions:
- Text cleaning & filtering
- API communication
- CSV handling (save, load, merge)
- Statistics & reporting
- Batch processing

### `twitter_scraper.py`
Main Selenium scraper:
- `TwitterScraper` class for Web scraping
- Tweet & reply extraction
- Automatic scroll loading
- Error handling & retries

### `app.py`
Main application:
- `ScraperApp` class for orchestration
- CLI interface
- Workflow automation
- Integration layer

---

## ⚡ Performance Tips

1. **Batch Processing**: API automatically batches texts (default: 32)
2. **Headless Mode**: Much faster than showing browser window
3. **Skip Browser**: Use `--no-headless` only for debugging
4. **Merge First**: If scraping multiple times, merge CSVs and deduplicate
5. **Cache Results**: Save intermediate CSVs to avoid re-scraping

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| **ChromeDriver not found** | Run `pip install webdriver-manager` |
| **Connection refused on API** | Start Flask: `python run_pipeline_server.py` |
| **No replies extracted** | Check if tweet has visible replies; try `--no-headless` |
| **Timeout errors** | Increase `EXPLICIT_WAIT` in config.py |
| **Unicode/encoding errors** | Ensure CSV is UTF-8 encoded |
| **Too slow** | Use `--headless` mode (default) |
| **Stale element errors** | Reduce `MAX_SCROLLS` in config.py |

---

## 📝 Example Workflow

```bash
# 1. Start emotion classifier
python ../run_pipeline_server.py &

# 2. Scrape tweets
python app.py --scrape \
  https://x.com/user1/status/123 \
  https://x.com/user2/status/456 \
  --analyze \
  --output batch1.csv

# 3. Scrape more tweets
python app.py --scrape \
  https://x.com/user3/status/789 \
  --analyze \
  --output batch2.csv

# 4. Merge all batches
python app.py --merge batch1.csv batch2.csv --output final_results.csv

# 5. Review results
head -20 final_results.csv
```

---

## 🔐 Legal Notice

⚠️ **Respect Twitter/X Terms of Service:**
- Don't scrape at high frequency (rate limiting)
- Don't store large datasets without permission
- Use scraped data responsibly
- Check local laws regarding web scraping

---

## 🙏 Acknowledgments

- **Selenium**: Web browser automation
- **Pandas**: Data manipulation
- **webdriver-manager**: ChromeDriver management
- **Emotion Classifier**: Flask backend with PyTorch model

---

## 📞 Support

For issues or suggestions:
1. Check configuration settings
2. Review troubleshooting section
3. Run with `--no-headless` to debug
4. Check logs for error messages

---

**Last Updated:** June 2026  
**Version:** 1.0.0
