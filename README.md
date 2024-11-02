# Client Data Scraper

This project scrapes structured data (e.g., "About Us," "Services Offered") from client websites and stores it in JSON format.

## Directory Structure

- `src/`: Contains main Python scripts for scraping.
- `data/`: Stores JSON data and client URL list (if any).
- `config/`: Configuration file for base URL and HTML selectors.
- `logs/`: Log file for error handling and tracking progress.

## Usage

1. Install required packages:
   ```bash
   pip install beautifulsoup4 requests
