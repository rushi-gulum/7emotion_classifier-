# ========================================================
# Installation Test & Validation Script
# ========================================================

"""
This script validates that all dependencies are installed
and the scraper is ready to use.

Usage:
    python test.py              # Run all tests
    python test.py --quick      # Run quick tests only
    python test.py --deep       # Run all + API test
"""

import sys
import importlib
from pathlib import Path

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"


def print_header(text):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}  {text}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")


def print_pass(text):
    print(f"{GREEN}✅ {text}{RESET}")


def print_fail(text):
    print(f"{RED}❌ {text}{RESET}")


def print_warn(text):
    print(f"{YELLOW}⚠️  {text}{RESET}")


def test_imports():
    """Test if all required packages are installed."""
    print_header("TEST 1: Package Imports")
    
    packages = {
        "selenium": "Selenium",
        "webdriver_manager": "WebDriver Manager",
        "pandas": "Pandas",
        "requests": "Requests",
    }
    
    all_passed = True
    
    for module, name in packages.items():
        try:
            importlib.import_module(module)
            print_pass(f"{name} is installed")
        except ImportError:
            print_fail(f"{name} is NOT installed")
            all_passed = False
    
    return all_passed


def test_local_modules():
    """Test if local modules can be imported."""
    print_header("TEST 2: Local Module Imports")
    
    modules = [
        ("config", "Configuration module"),
        ("utils", "Utilities module"),
        ("twitter_scraper", "Twitter Scraper module"),
        ("app", "Main Application module"),
    ]
    
    all_passed = True
    
    for module_name, description in modules:
        try:
            importlib.import_module(module_name)
            print_pass(f"{description} ({module_name}.py)")
        except ImportError as e:
            print_fail(f"{description} ({module_name}.py): {e}")
            all_passed = False
    
    return all_passed


def test_files():
    """Check if all required files exist."""
    print_header("TEST 3: File Integrity")
    
    required_files = [
        "config.py",
        "utils.py",
        "twitter_scraper.py",
        "app.py",
        "examples.py",
        "quickstart.py",
        "requirements.txt",
        "README.md",
    ]
    
    all_passed = True
    
    for filename in required_files:
        filepath = Path(filename)
        if filepath.exists():
            size_kb = filepath.stat().st_size / 1024
            print_pass(f"{filename} ({size_kb:.1f} KB)")
        else:
            print_fail(f"{filename} is MISSING")
            all_passed = False
    
    return all_passed


def test_output_dir():
    """Check/create output directory."""
    print_header("TEST 4: Output Directory")
    
    try:
        output_dir = Path("scraped_data")
        output_dir.mkdir(exist_ok=True)
        print_pass(f"Output directory ready: {output_dir.absolute()}")
        return True
    except Exception as e:
        print_fail(f"Could not create output directory: {e}")
        return False


def test_config():
    """Test configuration loading."""
    print_header("TEST 5: Configuration")
    
    try:
        from config import (
            FLASK_API_URL, HEADLESS, OUTPUT_DIR,
            MAX_SCROLLS, BATCH_SIZE, CHROME_DRIVER_PATH
        )
        
        print_pass(f"Flask API URL: {FLASK_API_URL}")
        print_pass(f"Headless mode: {HEADLESS}")
        print_pass(f"Output directory: {OUTPUT_DIR}")
        print_pass(f"Max scrolls: {MAX_SCROLLS}")
        print_pass(f"Batch size: {BATCH_SIZE}")
        print_pass(f"ChromeDriver auto-detect: {CHROME_DRIVER_PATH is None}")
        
        return True
    except Exception as e:
        print_fail(f"Configuration error: {e}")
        return False


def test_api_connection():
    """Test Flask API connection."""
    print_header("TEST 6: Flask API Connection")
    
    try:
        import requests
        from config import FLASK_API_URL
        
        # Try to connect
        response = requests.get(f"{FLASK_API_URL}/", timeout=5)
        print_pass(f"Connected to Flask API at {FLASK_API_URL}")
        print_pass(f"Response status: {response.status_code}")
        
        return True
    
    except requests.exceptions.ConnectionError:
        print_warn("Flask API is not running (this is OK for now)")
        print("  Start it with: python ../run_pipeline_server.py")
        return False
    
    except Exception as e:
        print_warn(f"Could not test API: {e}")
        return False


def test_chromedriver():
    """Test ChromeDriver availability."""
    print_header("TEST 7: ChromeDriver")
    
    try:
        from selenium import webdriver
        from webdriver_manager.chrome import ChromeDriverManager
        
        # Try to initialize
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        
        driver = webdriver.Chrome(options=options)
        print_pass("ChromeDriver initialized successfully")
        
        # Get version info
        version = driver.capabilities.get('browserVersion', 'Unknown')
        print_pass(f"Chrome version: {version}")
        
        driver.quit()
        return True
    
    except Exception as e:
        print_fail(f"ChromeDriver error: {e}")
        print("  Install with: pip install webdriver-manager")
        return False


def test_selenium_scraper():
    """Test TwitterScraper class instantiation."""
    print_header("TEST 8: TwitterScraper Class")
    
    try:
        from twitter_scraper import TwitterScraper
        
        # Just test instantiation (don't actually scrape)
        print("Attempting to initialize TwitterScraper...")
        scraper = TwitterScraper(headless=True)
        print_pass("TwitterScraper initialized successfully")
        
        scraper.close()
        return True
    
    except Exception as e:
        print_fail(f"TwitterScraper error: {e}")
        return False


def test_utilities():
    """Test utility functions."""
    print_header("TEST 9: Utility Functions")
    
    try:
        from utils import clean_text, filter_empty_texts, remove_duplicates
        
        # Test clean_text
        test_text = "Check this out! http://example.com @user #hashtag"
        cleaned = clean_text(test_text)
        print_pass(f"Text cleaning works: '{test_text}' → '{cleaned}'")
        
        # Test filter_empty_texts
        texts = ["hello", "  ", "", "world"]
        filtered = filter_empty_texts(texts)
        print_pass(f"Text filtering works: {len(texts)} → {len(filtered)} items")
        
        # Test remove_duplicates
        data = [
            {"text": "hello"},
            {"text": "hello"},
            {"text": "world"},
        ]
        unique, removed = remove_duplicates(data)
        print_pass(f"Deduplication works: {len(data)} → {len(unique)} unique ({removed} removed)")
        
        return True
    
    except Exception as e:
        print_fail(f"Utility functions error: {e}")
        return False


def run_all_tests(skip_chromedriver=False, skip_api=False):
    """Run all tests."""
    print_header("🕷️  TWITTER EMOTION SCRAPER - TEST SUITE")
    
    tests = [
        ("Package Imports", test_imports, True),
        ("Local Modules", test_local_modules, True),
        ("File Integrity", test_files, True),
        ("Output Directory", test_output_dir, True),
        ("Configuration", test_config, True),
        ("Utility Functions", test_utilities, True),
    ]
    
    if not skip_chromedriver:
        tests.append(("ChromeDriver", test_chromedriver, True))
    
    if not skip_api:
        tests.insert(5, ("Flask API", test_api_connection, False))
    
    results = []
    
    for test_name, test_func, is_required in tests:
        try:
            result = test_func()
            results.append((test_name, result, is_required))
        except Exception as e:
            print_fail(f"Test exception: {e}")
            results.append((test_name, False, is_required))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}\n")
    
    for test_name, result, is_required in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        required = "(REQUIRED)" if is_required else "(OPTIONAL)"
        print(f"  {status} {test_name} {required}")
    
    # Overall status
    print()
    
    failed_required = sum(1 for _, result, req in results if not result and req)
    
    if failed_required == 0:
        print_pass("All required tests passed! ✅")
        print("\nYou can now use the scraper:")
        print("  python app.py --scrape <URL> --analyze")
        print("  python quickstart.py  # Interactive guide")
        return True
    else:
        print_fail(f"{failed_required} required test(s) failed ❌")
        print("\nPlease fix the issues above and try again.")
        return False


def main():
    """Main entry point."""
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg == "--quick":
            print("Running quick tests (skipping ChromeDriver and API)...")
            run_all_tests(skip_chromedriver=True, skip_api=True)
        elif arg == "--deep":
            print("Running all tests including ChromeDriver initialization...")
            run_all_tests(skip_chromedriver=False, skip_api=False)
        else:
            print(f"Unknown argument: {arg}")
            print("Usage: python test.py [--quick|--deep]")
    else:
        # Default: run all tests
        run_all_tests()


if __name__ == "__main__":
    main()
