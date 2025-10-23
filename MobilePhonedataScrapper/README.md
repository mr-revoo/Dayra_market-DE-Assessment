# Mobile Phone Data Scraper

A comprehensive web scraper for extracting mobile phone listings and details from Egyptian e-commerce platforms.

## Overview

This project contains two specialized scrapers:

- **Dubizzle Scraper**: Scrapes mobile phone listings from Dubizzle Egypt using Selenium
- **Mobile Masr Scraper**: Scrapes mobile phone data from Mobile Masr using aiohttp

## Features

- **Async/Concurrent Scraping**: High-performance parallel scraping with configurable workers
- **Search Functionality**: Search for specific phone models or scrape all listings
- **Detailed Extraction**: Captures product name, price, seller info, location, and specifications
- **JSON Export**: Saves scraped data in structured JSON format with timestamps
- **Interactive CLI**: User-friendly command-line interface
- **Retry Logic**: Automatic retry on failed requests
- **Optimized Performance**: Headless browsing with disabled images and optimized timeouts

## Requirements

- Python 3.11+
- Chrome/Chromium browser (for Dubizzle scraper)
- ChromeDriver (automatically managed by Selenium)

## Dependencies

The project uses the following Python packages:

- `selenium` - For browser automation (Dubizzle scraper)
- `beautifulsoup4` - For HTML parsing
- `lxml` - Fast XML/HTML parser
- `aiohttp` - Async HTTP client (Mobile Masr scraper)
- `aiofiles` - Async file I/O
- `requests` - HTTP library (for testing)

## Installation & Setup

### Quick Setup (Recommended)

#### Linux/macOS:
```bash
chmod +x setup.sh
./setup.sh
```

#### Windows:
```cmd
setup.bat
```

These scripts will:
1. Create a virtual environment
2. Install all required dependencies
3. Launch the scraper in interactive mode

### Manual Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

2. **Activate the virtual environment:**
   - Linux/macOS: `source .venv/bin/activate`
   - Windows: `.venv\Scripts\activate`

3. **Install dependencies:**
   ```bash
   pip install selenium beautifulsoup4 lxml aiohttp aiofiles requests
   ```

## Usage

### Running the Main Scraper

```bash
python main.py
```

The interactive menu will prompt you to:
1. Search for a specific product (e.g., "iPhone 13", "Samsung Galaxy")
2. Scrape all mobile phone listings

You'll also be asked to specify the maximum number of pages to scrape.

### Running Individual Scrapers

**Dubizzle Scraper:**
```bash
python DubbizleSrapper/main.py
```

**Mobile Masr Scraper:**
```bash
python MobileMasrScrapper/main.py
```

## Output

Scraped data is saved as JSON files in the respective scraper directories:

- `DubbizleSrapper/dubizzle_products.json` - All listings from Dubizzle
- `DubbizleSrapper/{query}_results.json` - Search results (e.g., `iphone_13_results.json`)
- `MobileMasrScrapper/mobilemasr_products.json` - All listings from Mobile Masr
- `MobileMasrScrapper/mobilemasr_{query}_results.json` - Search results

### JSON Structure

```json
{
  "scraped_at": "2025-10-23T12:00:00",
  "total_products": 150,
  "products": [
    {
      "product_name": "iPhone 13 Pro Max",
      "price": "25,000 EGP",
      "seller_name": "John Doe",
      "location": "Cairo, Egypt",
      "listing_url": "https://...",
      "details": {
        "Brand": "Apple",
        "Condition": "Used",
        "Storage": "256 GB"
      }
    }
  ]
}
```

## Performance

- **Parallel Workers**: Configurable (default: 10 concurrent browsers)
- **Speed**: ~10-20 products per second (depending on network and system)
- **Optimization**: Headless mode, disabled images, eager page loading

## Configuration

You can adjust scraping parameters in the code:

- `max_workers`: Number of parallel browsers (default: 10)
- `max_pages`: Number of listing pages to scrape
- Timeout values and retry logic in the scraper classes

## Troubleshooting

**ChromeDriver Issues:**
- Ensure Chrome/Chromium is installed
- Selenium will auto-download compatible ChromeDriver

**Connection Errors:**
- Check your internet connection
- Some sites may have rate limiting - reduce `max_workers` if needed

**No Products Found:**
- Verify the website structure hasn't changed
- Check if the search query is valid

## Project Structure

```
MobilePhonedataScrapper/
├── main.py                 # Main Dubizzle scraper
├── test.py                 # Testing utilities
├── DubbizleSrapper/
│   ├── main.py            # Dubizzle scraper module
│   └── *.json             # Output files
├── MobileMasrScrapper/
│   ├── main.py            # Mobile Masr scraper module
│   └── *.json             # Output files
└── README.md              # This file
```

## Notes

- The scrapers are designed for educational and research purposes
- Respect website terms of service and rate limits
- Data accuracy depends on source website structure
- Chrome browser must be installed for Selenium-based scrapers

## License

This project is for educational purposes. Please respect the terms of service of the websites being scraped.
