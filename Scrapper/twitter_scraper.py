# ========================================================
# Twitter/X Scraper using Selenium
# ========================================================

import time
import logging
from typing import List, Dict, Optional
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, StaleElementReferenceException
)
from config import *
from utils import clean_text, filter_empty_texts, remove_duplicates

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TwitterScraper:
    """
    Scraper for Twitter/X tweets and replies using Selenium.
    """
    
    def __init__(self, headless: bool = True, driver_path: Optional[str] = None):
        """
        Initialize Twitter scraper.
        
        Args:
            headless: Run browser in headless mode
            driver_path: Path to ChromeDriver (auto-detect if None)
        """
        self.driver = None
        self.wait = None
        self.headless = headless
        self.driver_path = driver_path
        self._init_driver()
    
    def _init_driver(self):
        """Initialize Selenium WebDriver."""
        try:
            logger.info("Initializing Chrome WebDriver...")
            
            options = ChromeOptions()
            
            if self.headless:
                options.add_argument("--headless")
            
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument(f"user-agent={USER_AGENT}")
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option('useAutomationExtension', False)
            
            if self.driver_path:
                self.driver = webdriver.Chrome(self.driver_path, options=options)
            else:
                self.driver = webdriver.Chrome(options=options)
            
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(IMPLICIT_WAIT)
            self.wait = WebDriverWait(self.driver, EXPLICIT_WAIT)
            
            logger.info("✅ WebDriver initialized successfully")
        
        except Exception as e:
            logger.error(f"❌ Failed to initialize WebDriver: {e}")
            logger.error("Make sure ChromeDriver is installed: pip install webdriver-manager")
            raise
    
    def navigate_to_tweet(self, tweet_url: str) -> bool:
        """
        Navigate to a tweet URL.
        
        Args:
            tweet_url: URL of the tweet
        
        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"Navigating to: {tweet_url}")
            self.driver.get(tweet_url)
            
            # Wait for page to load
            time.sleep(2)
            logger.info("✅ Page loaded")
            
            return True
        
        except TimeoutException:
            logger.error(f"❌ Page load timeout for {tweet_url}")
            return False
        
        except Exception as e:
            logger.error(f"❌ Error navigating to {tweet_url}: {e}")
            return False
    
    def extract_tweet_text(self) -> Optional[str]:
        """
        Extract the main tweet text from current page.
        
        Returns:
            Tweet text or None if not found
        """
        try:
            tweet_text_elem = self.driver.find_element(By.CSS_SELECTOR, TEXT_SELECTOR)
            text = tweet_text_elem.text.strip()
            
            if text:
                logger.info(f"📝 Tweet text: {text[:100]}...")
                return text
            
            return None
        
        except NoSuchElementException:
            logger.warning("Could not find tweet text element")
            return None
    
    def scroll_to_load_replies(self, max_scrolls: int = MAX_SCROLLS) -> int:
        """
        Scroll down to load more replies.
        
        Args:
            max_scrolls: Maximum number of scrolls to perform
        
        Returns:
            Number of scrolls performed
        """
        scroll_count = 0
        prev_height = 0
        
        logger.info(f"Scrolling to load replies (max {max_scrolls} scrolls)...")
        
        for i in range(max_scrolls):
            # Get current scroll height
            current_height = self.driver.execute_script(
                "return document.documentElement.scrollHeight"
            )
            
            if current_height == prev_height:
                logger.info("No new content loaded, stopping scroll")
                break
            
            # Scroll down
            self.driver.execute_script(
                "window.scrollTo(0, document.documentElement.scrollHeight);"
            )
            
            prev_height = current_height
            scroll_count += 1
            
            logger.info(f"Scroll {scroll_count}/{max_scrolls} completed")
            time.sleep(SCROLL_PAUSE_TIME)
        
        logger.info(f"✅ Completed {scroll_count} scrolls")
        return scroll_count
    
    def extract_all_replies(self) -> List[str]:
        """
        Extract all visible reply texts from current page.
        
        Returns:
            List of reply texts
        """
        try:
            logger.info("Extracting reply texts...")
            
            reply_elements = self.driver.find_elements(By.CSS_SELECTOR, REPLY_SELECTOR)
            logger.info(f"Found {len(reply_elements)} reply elements")
            
            replies = []
            
            for idx, element in enumerate(reply_elements, 1):
                try:
                    text_elem = element.find_element(By.CSS_SELECTOR, TEXT_SELECTOR)
                    text = text_elem.text.strip()
                    
                    if text:
                        cleaned = clean_text(text)
                        if cleaned:  # Only add non-empty cleaned text
                            replies.append(text)
                            if idx % 10 == 0:
                                logger.info(f"  Extracted {idx} replies...")
                
                except (NoSuchElementException, StaleElementReferenceException):
                    continue
            
            logger.info(f"✅ Extracted {len(replies)} replies total")
            return replies
        
        except Exception as e:
            logger.error(f"❌ Error extracting replies: {e}")
            return []
    
    def scrape_tweet_with_replies(self, tweet_url: str) -> Dict:
        """
        Scrape a tweet and all its replies.
        
        Args:
            tweet_url: URL of the tweet to scrape
        
        Returns:
            Dictionary with tweet data and replies
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Starting scrape for: {tweet_url}")
        logger.info('='*60)
        
        if not self.navigate_to_tweet(tweet_url):
            return {}
        
        # Extract main tweet
        tweet_text = self.extract_tweet_text()
        
        if not tweet_text:
            logger.warning("Could not extract tweet text")
            tweet_text = "N/A"
        
        # Scroll to load replies
        self.scroll_to_load_replies()
        
        # Extract all replies
        replies = self.extract_all_replies()
        replies = filter_empty_texts(replies)
        
        logger.info(f"\n📊 Scrape Summary:")
        logger.info(f"  Main tweet: {tweet_text[:80]}...")
        logger.info(f"  Total replies: {len(replies)}")
        
        return {
            "tweet_url": tweet_url,
            "tweet_text": tweet_text,
            "replies": replies,
            "reply_count": len(replies)
        }
    
    def scrape_multiple_tweets(self, tweet_urls: List[str]) -> List[Dict]:
        """
        Scrape multiple tweets with their replies.
        
        Args:
            tweet_urls: List of tweet URLs
        
        Returns:
            List of dictionaries with tweet data
        """
        results = []
        
        for idx, url in enumerate(tweet_urls, 1):
            logger.info(f"\n[{idx}/{len(tweet_urls)}] Processing: {url}")
            
            data = self.scrape_tweet_with_replies(url)
            
            if data:
                results.append(data)
                time.sleep(2)  # Polite delay between requests
        
        logger.info(f"\n✅ Completed scraping {len(results)}/{len(tweet_urls)} tweets")
        
        return results
    
    def flatten_results(self, results: List[Dict]) -> List[Dict]:
        """
        Flatten scraped data into list of reply records.
        
        Each record contains: text, author (N/A), tweet_url, source
        """
        flattened = []
        
        for result in results:
            tweet_url = result.get("tweet_url", "")
            
            for reply_text in result.get("replies", []):
                flattened.append({
                    "text": reply_text,
                    "author": "N/A",  # Selenium scraper doesn't extract author
                    "tweet_url": tweet_url,
                    "source": "twitter_scraper"
                })
        
        return flattened
    
    def close(self):
        """Close the WebDriver."""
        if self.driver:
            self.driver.quit()
            logger.info("✅ WebDriver closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# ========= USAGE EXAMPLE =========
if __name__ == "__main__":
    # Example usage
    tweet_urls = [
        "https://twitter.com/GavinNewsom/status/1234567890",  # Replace with real URL
        "https://x.com/elonmusk/status/9876543210",  # Replace with real URL
    ]
    
    try:
        with TwitterScraper(headless=False) as scraper:  # Set to True for headless
            results = scraper.scrape_multiple_tweets(tweet_urls)
            
            # Flatten and display
            flattened = scraper.flatten_results(results)
            print(f"\n✅ Collected {len(flattened)} replies")
            
            for i, record in enumerate(flattened[:5], 1):
                print(f"\n{i}. {record['text'][:100]}...")
    
    except Exception as e:
        logger.error(f"Error: {e}")
