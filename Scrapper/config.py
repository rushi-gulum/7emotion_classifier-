# ========================================================
# Configuration for Twitter Scraper
# ========================================================

# ========= BROWSER SETTINGS =========
CHROME_DRIVER_PATH = None  # Auto-detect if None; set manually if needed
HEADLESS = True  # Run browser in headless mode (no GUI)
IMPLICIT_WAIT = 10  # Seconds to wait for elements
EXPLICIT_WAIT = 15  # Seconds for explicit waits
PAGE_LOAD_TIMEOUT = 30  # Page load timeout in seconds

# ========= SCRAPING SETTINGS =========
SCROLL_PAUSE_TIME = 2  # Time to pause between scrolls (seconds)
MAX_SCROLLS = 5  # Maximum number of scroll attempts
TWEET_SELECTOR = "[data-testid='tweet']"  # Twitter tweet container
REPLY_SELECTOR = "[data-testid='tweet']"  # Reply container (same as tweets)
TEXT_SELECTOR = "[data-testid='tweetText'] span"  # Tweet text
LOAD_REPLIES_BUTTON = "text=Show"  # Button to load hidden replies

# ========= API SETTINGS =========
FLASK_API_URL = "http://127.0.0.1:5001"  # Flask emotion classifier API
ANALYZE_ENDPOINT = "/analyze"  # Bulk analyze endpoint
LABEL_ENDPOINT = "/label_texts"  # Label texts endpoint

# ========= OUTPUT SETTINGS =========
OUTPUT_DIR = "scraped_data"  # Directory to save CSV files
CSV_FILENAME = "tweet_replies.csv"  # Default output filename
INCLUDE_TIMESTAMPS = True  # Include collection timestamp in output
BATCH_SIZE = 32  # Process emotions in batches

# ========= TWITTER URLS =========
TWITTER_BASE_URL = "https://twitter.com"
TWITTER_X_BASE_URL = "https://x.com"

# ========= RETRY SETTINGS =========
MAX_RETRIES = 3  # Maximum retry attempts
RETRY_DELAY = 5  # Delay between retries (seconds)

# ========= USER AGENT =========
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
