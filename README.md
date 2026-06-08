#  Tweet Emotion Analyzer — Complete System

**A complete local emotion analysis ecosystem: PyTorch BiLSTM model + Flask API + Selenium scraper + Chrome extension.**

Scrape tweet replies, classify emotions (7 classes), visualize results with color-coded highlights—all locally with zero privacy concerns.

**Author:** Rushi Gulumkar

---


##  Quick Start (5 Minutes)

```bash
# 1. Install & setup
pip install -r requirements.txt
conda create -n emotions python=3.10 && conda activate emotions

# 2. Start Flask server (Terminal 1)
python run_pipeline_server.py

# 3. Scrape & analyze (Terminal 2)
cd Scrapper
python app.py --scrape https://x.com/user/status/123 --analyze

# 4. View results
head -20 scraped_data/tweet_replies.csv
```

---

##  System Components

### 1️ Emotion Classifier Model
- **Architecture**: BiLSTM (2 layers, 256 hidden) + Self-Attention + Dense
- **Training**: 35 epochs on GoEmotions 7-class balanced dataset
- **Performance**: 50ms CPU / 5ms GPU per text
- **Emotions**: Joy, Anger, Sadness, Fear, Disgust, Surprise, Neutral
- **Files**: `best_model.pth` (weights), `vocab.pkl`, `label_encoder.pkl`

### 2️ Flask API Backend
- **Endpoints**: `/analyze` (counts), `/label_texts` (labels per text)
- **Port**: 5001
- **Features**: CORS enabled, batch processing, model caching
- **Input**: JSON with text array
- **Output**: JSON with emotion predictions

### 3️ Selenium Web Scraper
- **Automation**: Browser auto-scroll to load replies
- **Text Processing**: Clean URLs, mentions, hashtags
- **Deduplication**: Automatic duplicate removal
- **Batch Processing**: Process 1000+ texts efficiently
- **Location**: `Scrapper/` folder (9 modules, 70+ KB)

### 4️ CLI & Python API
- **CLI**: Full command-line interface with argparse
- **Workflows**: Single scrape, batch scrape, CSV processing, file merging
- **Python API**: Programmatic access for automation
- **Logging**: Comprehensive debug output

---

##  Installation

### Main Project
```bash
pip install -r requirements.txt
# Installs: torch, flask, tensorflow, pandas, scikit-learn, tqdm

# Optional: GPU support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

### Scraper Module
```bash
cd Scrapper
pip install -r requirements.txt
# Installs: selenium, webdriver-manager, pandas, requests
# webdriver-manager auto-downloads ChromeDriver
```

---

##  Usage Guide

### Method 1: Command Line (Easiest)

**Scrape single tweet:**
```bash
cd Scrapper
python app.py --scrape https://x.com/user/status/123 --analyze
```

**Scrape multiple tweets:**
```bash
python app.py --scrape URL1 URL2 URL3 --analyze --output results.csv
```

**Add emotions to CSV:**
```bash
python app.py --csv existing_data.csv --analyze
```

**Merge multiple CSVs:**
```bash
python app.py --merge batch1.csv batch2.csv batch3.csv --output merged.csv
```

**Interactive guide:**
```bash
python quickstart.py
```

---

## 📊 Complete Workflow

```
START: Tweet URLs
  ↓
[Scraper] Navigate + Extract Replies
  ↓
[Processor] Clean Text + Remove Duplicates
  ↓
[Classifier] BiLSTM Model (Flask API)
  ↓
[Output] CSV with Emotion Labels + Statistics
  ↓
RESULT: scraped_data/*.csv
```

**Output CSV Format:**
```
scraped_at | text | author | tweet_url | source | emotion
2024-06-09 10:30:45 | amazing project! | N/A | https://x.com/.../123 | twitter_scraper | joy
```

---


##  Emotion Classes

| Emotion | Color | Hex | Example |
|---------|-------|-----|---------|
| Joy |  Green | #4CAF50 | "Love this!" |
| Anger |  Red | #FF5722 | "Hate it!" |
| Sadness |  Yellow | #FFC107 | "So sad..." |
| Fear |  Blue | #2196F3 | "Terrified!" |
| Disgust | Purple | #9C27B0 | "Gross!" |
| Surprise |  Pink | #E91E63 | "Wow!" |
| Neutral |  Cyan | #00BCD4 | "OK then" |

---

## 🔧 Configuration

**Main Settings** (`Scrapper/config.py`):
```python
HEADLESS = True              # Run browser without GUI (faster)
FLASK_API_URL = "http://127.0.0.1:5001"  # Emotion API
MAX_SCROLLS = 5              # Replies loading scrolls
BATCH_SIZE = 32              # Texts per emotion batch
OUTPUT_DIR = "scraped_data"  # Results directory
```

**Model Settings** (automatic):
- Vocab size: 23,810 tokens
- Embedding: 300 dims
- LSTM: 256 hidden, 2 layers, bidirectional
- Input length: 60-100 tokens (padded)

---

##  Important Notes

**Legal:** Respect Twitter/X ToS — don't scrape excessively, use data responsibly  
**Privacy:** All processing is local, no data sent to external services  
**Accuracy:** Works best on complete sentences; short tweets may vary  
**GPU:** Install CUDA for 10x speedup: `pip install torch --index-url https://download.pytorch.org/whl/cu118`

---

##  Documentation

- **Main project**: See this README
- **Scraper details**: Read `Scrapper/README.md`
- **Examples**: Run `python Scrapper/examples.py` or check `Scrapper/examples.py`
- **Quick start**: `python Scrapper/quickstart.py`
- **Tests**: `python Scrapper/test.py`

---

##  Use Cases

1 Social media sentiment analysis  
2 Crisis monitoring (track public emotion)  
3 Trend analysis (emotion by topic)  
4 Research (labeled emotion dataset)  
5 Content moderation (flag toxic sentiment)  
6 Competitive intelligence (monitor mentions)  

---

##  Acknowledgments

- **GoEmotions dataset**: Google Research
- **Framework**: PyTorch, Flask
- **Automation**: Selenium, webdriver-manager
- **Data**: Pandas, scikit-learn



