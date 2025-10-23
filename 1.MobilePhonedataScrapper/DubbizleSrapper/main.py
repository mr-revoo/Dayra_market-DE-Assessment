# Fast async Selenium Dubizzle scraper
import asyncio
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import json
from datetime import datetime
import aiofiles
import time
from concurrent.futures import ThreadPoolExecutor

class DubizzleScraper:
    def __init__(self, max_workers=10):
        self.base_url = "https://www.dubizzle.com.eg/en/mobile-phones-tablets-accessories-numbers/mobile-phones/"
        self.products = []
        self.max_workers = max_workers
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        
    def create_driver(self):
        """Create optimized headless Chrome driver"""
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-images')
        options.add_argument('--blink-settings=imagesEnabled=false')
        options.add_argument('--disable-javascript')  # Disable JS for product pages - we only need HTML
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        options.page_load_strategy = 'eager'
        
        driver = webdriver.Chrome(options=options)
        driver.set_page_load_timeout(15)  # Reduced timeout
        driver.implicitly_wait(2)  # Reduced wait
        
        return driver
    
    def fetch_page_sync(self, url, enable_js=False, max_retries=2):
        """Synchronous page fetch for thread pool with retry logic"""
        for attempt in range(max_retries):
            driver = self.create_driver()
            try:
                # Enable JS only for listing pages
                if enable_js:
                    driver.execute_cdp_cmd('Network.setUserAgentOverride', {
                        "userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                    })
                    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
                
                driver.get(url)
                time.sleep(1 if not enable_js else 3)
                
                html = driver.page_source
                
                # Check for error page only on listing pages
                if enable_js and ("حدث خطأ ما" in html or "Something went wrong" in html):
                    driver.refresh()
                    time.sleep(3)
                    html = driver.page_source
                
                # Verify we got valid content
                if html and len(html) > 1000:
                    return html
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    print(f"[Error] Failed {url} after {max_retries} attempts")
            finally:
                try:
                    driver.quit()
                except:
                    pass
                    
        return None
    
    async def fetch_page(self, url, enable_js=False):
        """Async wrapper for page fetch"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, self.fetch_page_sync, url, enable_js)
    
    def parse_listing_page(self, html):
        """Extract product URLs from listing page"""
        soup = BeautifulSoup(html, "lxml")
        listing_items = soup.find_all("li", attrs={"aria-label": "Listing"})
        
        if not listing_items:
            listing_items = soup.find_all("article")
        
        urls = []
        for item in listing_items:
            try:
                article = item if item.name == "article" else item.find("article")
                if article:
                    link = article.find("a", href=True)
                    if link and link["href"]:
                        full_url = f"https://www.dubizzle.com.eg{link['href']}"
                        if "/ad/" in full_url:
                            urls.append(full_url)
            except:
                continue
        return urls
    
    def parse_product_details(self, html, url):
        """Extract product details from product page"""
        try:
            soup = BeautifulSoup(html, "lxml")
            
            h1 = soup.find("h1")
            product_name = h1.get_text(strip=True) if h1 else "N/A"
            
            price_span = soup.find("span", class_="_24469da7", attrs={"aria-label": "Price"})
            price = price_span.get_text(strip=True) if price_span else "N/A"
            
                        # Try to find seller name (normal users)
            seller_span = soup.find("span", class_="_8206696c b7af14b4")
            
            # If not found or contains "See profile", try verified user structure
            if not seller_span or "See profile" in seller_span.get_text(strip=True):
                # For verified users, look for the name in a different location
                # Usually in a span or div before the "See profile" link
                verified_container = soup.find("div", class_="_92439ac7")
                if verified_container:
                    name_span = verified_container.find("span", class_="_9a85fb36 b7af14b4")
                    if name_span and "See profile" not in name_span.get_text(strip=True):
                        seller_span = name_span
            
            seller_name = seller_span.get_text(strip=True) if seller_span and "See profile" not in seller_span.get_text(strip=True) else "N/A"
            location_span = soup.find("span", attrs={"aria-label": "Location"})
            location = location_span.get_text(strip=True) if location_span else "N/A"
            
            details = {}
            detail_containers = soup.find_all("div", class_="_92439ac7")
            for container in detail_containers:
                inner_divs = container.find_all("div", class_="_9a8eacd9")
                for div in inner_divs:
                    spans = div.find_all("span")
                    if len(spans) >= 2:
                        key = spans[0].get_text(strip=True)
                        value = spans[1].get_text(strip=True)
                        details[key] = value
            
            return {
                "product_name": product_name,
                "price": price,
                "seller_name": seller_name,
                "location": location,
                "listing_url": url,
                "details": details
            }
        except:
            return None
    
    async def fetch_product_details(self, url, index, total):
        """Fetch and parse product page with retry"""
        html = await self.fetch_page(url, enable_js=False)
        if html:
            result = self.parse_product_details(html, url)
            if result:
                if (index + 1) % 10 == 0:
                    print(f"[Progress] {index + 1}/{total} products scraped")
                return result
            else:
                print(f"[Warning] Failed to parse product {index + 1}/{total}")
        else:
            print(f"[Warning] Failed to fetch product {index + 1}/{total}")
        return None
    
    async def scrape_all_pages(self, max_pages=10):
        """Scrape all pages"""
        print(f"\n[Start] Scraping {max_pages} pages from Dubizzle")
        print(f"[Workers] {self.max_workers} parallel browsers\n")
        start_time = time.time()
        
        print("[Step 1] Fetching listing pages...")
        listing_urls = [f"{self.base_url}?page={i}" for i in range(1, max_pages + 1)]
        
        listing_tasks = [self.fetch_page(url, enable_js=True) for url in listing_urls]  # Enable JS for listings
        listing_results = await asyncio.gather(*listing_tasks)
        
        all_urls = []
        for i, html in enumerate(listing_results, 1):
            if html:
                urls = self.parse_listing_page(html)
                all_urls.extend(urls)
                print(f"[Page {i}] Found {len(urls)} products")
        
        unique_urls = list(set(all_urls))
        print(f"\n[Step 1 Done] Found {len(unique_urls)} unique products")
        
        if not unique_urls:
            print("[Error] No products found")
            return
        
        print(f"\n[Step 2] Scraping product details (JS disabled for speed)...")
        detail_tasks = [self.fetch_product_details(url, i, len(unique_urls)) for i, url in enumerate(unique_urls)]
        results = await asyncio.gather(*detail_tasks, return_exceptions=True)
        
        self.products = [r for r in results if r and not isinstance(r, Exception)]
        
        failed_count = len(unique_urls) - len(self.products)
        elapsed = time.time() - start_time
        
        print(f"\n[Done] Scraped {len(self.products)}/{len(unique_urls)} products in {elapsed:.1f} seconds")
        if failed_count > 0:
            print(f"[Warning] {failed_count} products failed to scrape")
        if elapsed > 0:
            print(f"[Speed] {len(self.products)/elapsed:.1f} products/second")
    
    async def scrape_search(self, query, max_pages=10):
        """Search and scrape specific products"""
        query_slug = f"q-{query.lower().replace(' ', '-')}/"
        search_url = f"{self.base_url}{query_slug}"
        
        print(f"\n[Search] Query: '{query}'")
        print(f"[URL] {search_url}")
        print(f"[Workers] {self.max_workers} parallel browsers\n")
        start_time = time.time()
        
        self.products = []
        
        print("[Step 1] Fetching search results...")
        all_urls = []
        
        search_urls = [f"{search_url}?page={i}" for i in range(1, max_pages + 1)]
        search_tasks = [self.fetch_page(url, enable_js=True) for url in search_urls]  # Enable JS for search
        search_results = await asyncio.gather(*search_tasks)
        
        for i, html in enumerate(search_results, 1):
            if html:
                urls = self.parse_listing_page(html)
                if urls:
                    all_urls.extend(urls)
                    print(f"[Page {i}] Found {len(urls)} products")
        
        unique_urls = list(set(all_urls))
        print(f"\n[Step 1 Done] Found {len(unique_urls)} unique products")
        
        if not unique_urls:
            print("[Error] No products found")
            return
        
        print(f"\n[Step 2] Scraping product details (JS disabled for speed)...")
        detail_tasks = [self.fetch_product_details(url, i, len(unique_urls)) for i, url in enumerate(unique_urls)]
        results = await asyncio.gather(*detail_tasks, return_exceptions=True)
        
        self.products = [r for r in results if r and not isinstance(r, Exception)]
        
        failed_count = len(unique_urls) - len(self.products)
        elapsed = time.time() - start_time
        
        print(f"\n[Done] Scraped {len(self.products)}/{len(unique_urls)} products in {elapsed:.1f} seconds")
        if failed_count > 0:
            print(f"[Warning] {failed_count} products failed to scrape")
        if elapsed > 0:
            print(f"[Speed] {len(self.products)/elapsed:.1f} products/second")
    
    async def save_data(self, filename="dubizzle_products.json"):
        """Save products to JSON file"""
        output = {
            "scraped_at": datetime.now().isoformat(),
            "total_products": len(self.products),
            "products": self.products
        }
        
        async with aiofiles.open(filename, "w", encoding="utf-8") as f:
            await f.write(json.dumps(output, indent=2, ensure_ascii=False))
        
        print(f"\n[Saved] {len(self.products)} products to {filename}")
    
    def cleanup(self):
        """Cleanup thread pool"""
        self.executor.shutdown(wait=True)

async def main():
    print("="*60)
    print("DUBIZZLE SCRAPER (Selenium)")
    print("="*60)
    print("\n1. Search for specific product")
    print("2. Scrape all mobile phones")
    
    choice = input("\nChoice (1 or 2): ").strip()
    
    scraper = DubizzleScraper(max_workers=10)
    
    try:
        if choice == "1":
            query = input("Product name: ").strip()
            if not query:
                print("[Error] Search query cannot be empty")
                return
            
            pages = input("Max pages (default 10): ").strip()
            pages = int(pages) if pages.isdigit() else 10
            
            await scraper.scrape_search(query, max_pages=pages)
            
            filename = f"{query.lower().replace(' ', '_')}_results.json"
            await scraper.save_data(filename)
            
        elif choice == "2":
            pages = input("Max pages (default 10): ").strip()
            pages = int(pages) if pages.isdigit() else 10
            
            await scraper.scrape_all_pages(max_pages=pages)
            await scraper.save_data()
            
        else:
            print("[Error] Invalid choice")
    finally:
        scraper.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
