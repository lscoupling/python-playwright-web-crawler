# python-playwright-web-crawler
Python + Playwright + Web Crawler

## CMoney Stock Data Crawler

This repository contains a web crawler that uses Playwright to scrape stock data from the CMoney website.

### Features

- Asynchronous web scraping using Playwright
- Captures stock data for specified date ranges
- Automatically skips weekends
- Saves data in JSON format
- Supports multiple stocks

### Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Install Playwright browsers:
```bash
playwright install chromium
```

### Usage

Run the crawler:
```bash
python cmoney_capture_multi.py
```

### Configuration

Edit `cmoney_capture_multi.py` to configure:
- `STOCKS`: Dictionary of stock names and IDs
- `START_DATE`: Start date for data collection
- `END_DATE`: End date for data collection

### Output

Data will be saved in `data_{stock_name}_{stock_id}/` directories with filenames in the format `{stock_id}_{YYYYMMDD}.json`.
