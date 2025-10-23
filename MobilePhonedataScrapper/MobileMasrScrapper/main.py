# MobileMasr Scraper using Algolia Search API
import asyncio
import aiohttp
import json
from datetime import datetime
import aiofiles
import os
from pathlib import Path

# Load environment variables
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent / '.env'
    load_dotenv(dotenv_path=env_path)
except ImportError:
    print("[Warning] python-dotenv not installed. Install with: pip install python-dotenv")

class MobileMasrAlgoliaScraper:
    def __init__(self, max_concurrent=20):
        self.base_url = "https://mobilemasr.com/en/category/mobile-phone/products"
        self.algolia_app_id = os.getenv("ALGOLIA_APP_ID")
        self.algolia_api_key = os.getenv("ALGOLIA_API_KEY")
        self.algolia_index = "Variant_new_index"
        
        if not self.algolia_app_id or not self.algolia_api_key:
            raise ValueError("ALGOLIA_APP_ID and ALGOLIA_API_KEY must be set in .env file")
        
        self.products = []
        self.semaphore = asyncio.Semaphore(max_concurrent)
        
    async def search_algolia(self, session, query="", page=0, hits_per_page=100):
        """Search products using Algolia API"""
        url = f"https://{self.algolia_app_id}-dsn.algolia.net/1/indexes/{self.algolia_index}/query"
        
        headers = {
            "X-Algolia-Application-Id": self.algolia_app_id,
            "X-Algolia-API-Key": self.algolia_api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "query": query,
            "page": page,
            "hitsPerPage": hits_per_page
        }
        
        async with self.semaphore:
            try:
                async with session.post(url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        print(f"[Error] Algolia API returned status {response.status}")
                        text = await response.text()
                        print(f"[Response] {text[:500]}")
            except Exception as e:
                print(f"[Error] Failed to query Algolia: {e}")
        return None
    
    async def scrape_all_products(self, max_pages=10, search_query=""):
        """Scrape products using Algolia search"""
        print(f"\n[Start] Scraping MobileMasr via Algolia API")
        if search_query:
            print(f"[Search] Query: '{search_query}'")
        print(f"[Concurrency] Max {self.semaphore._value} concurrent requests\n")
        start_time = asyncio.get_event_loop().time()
        
        async with aiohttp.ClientSession() as session:
            print("[Step 1] Fetching products from Algolia...")
            
            # Fetch first page to get total
            first_result = await self.search_algolia(session, query=search_query, page=0)
            
            if not first_result:
                print("[Error] Failed to fetch from Algolia")
                return
            
            total_hits = first_result.get("nbHits", 0)
            total_pages = first_result.get("nbPages", 1)
            hits = first_result.get("hits", [])
            
            print(f"[Info] Found {total_hits} products across {total_pages} pages")
            print(f"[Page 1/{min(max_pages, total_pages)}] Got {len(hits)} products")
            
            # Process first page
            for hit in hits:
                product_data = self.parse_algolia_hit(hit)
                if product_data:
                    self.products.append(product_data)
            
            # Fetch remaining pages
            pages_to_fetch = min(max_pages, total_pages)
            if pages_to_fetch > 1:
                tasks = [
                    self.search_algolia(session, query=search_query, page=i)
                    for i in range(1, pages_to_fetch)
                ]
                results = await asyncio.gather(*tasks)
                
                for i, result in enumerate(results, 2):
                    if result:
                        hits = result.get("hits", [])
                        print(f"[Page {i}/{pages_to_fetch}] Got {len(hits)} products")
                        for hit in hits:
                            product_data = self.parse_algolia_hit(hit)
                            if product_data:
                                self.products.append(product_data)
            
            elapsed = asyncio.get_event_loop().time() - start_time
            
            print(f"\n[Done] Scraped {len(self.products)} products in {elapsed:.1f} seconds")
            if elapsed > 0:
                print(f"[Speed] {len(self.products)/elapsed:.1f} products/second")
    
    def parse_algolia_hit(self, hit):
        """Parse Algolia search result hit"""
        try:
            # Extract basic info
            brand = hit.get("brand_en", "N/A")
            model = hit.get("item_en", "N/A")
            ram = hit.get("ram_en", "N/A")
            storage = hit.get("storage_en", "N/A")
            color = hit.get("color_en", "N/A")
            condition = hit.get("variant_type_en", "N/A")
            battery_health = hit.get("battery_health", "N/A")
            
            # Build product name
            product_name_parts = [brand, model, storage]
            if color and color != "N/A":
                product_name_parts.append(color)
            product_name = " ".join([p for p in product_name_parts if p and p != "N/A"])
            
            # Format price to match Dubizzle style (EGP X,XXX)
            price_value = hit.get("sale_price", 0) or hit.get("original_price", 0)
            if price_value:
                price = f"EGP {price_value:,}"
            else:
                price = "N/A"
            
            # Build details object like Dubizzle
            details = {}
            
            if brand != "N/A":
                details["Brand"] = brand
            if model != "N/A":
                details["Model"] = model
            if ram != "N/A":
                details["RAM"] = ram
            if storage != "N/A":
                details["Storage"] = storage
            if color != "N/A":
                details["Color"] = color
            if condition != "N/A":
                details["Condition"] = condition
            if battery_health != "N/A":
                details["Battery Health"] = battery_health
            
            # Add warranty info
            is_warranty = hit.get("is_warranty", False)
            details["Warranty"] = "Yes" if is_warranty else "No"
            
            # Add insurance info
            is_insurance = hit.get("is_insurance", False)
            details["Insurance"] = "Yes" if is_insurance else "No"
            
            # Add SIM info
            sim_info = hit.get("sim_en", "N/A")
            if sim_info != "N/A":
                details["SIM"] = sim_info
            
            # SKU
            sku = hit.get("sku", "N/A")
            if sku != "N/A":
                details["SKU"] = sku
            
            # Get seller name (vendor store or private seller)
            seller_name = hit.get("vendor_storename") or hit.get("seller_user_name") or "N/A"
            
            # Build product object in Dubizzle format
            product = {
                "product_name": product_name,
                "price": price,
                "seller_name": seller_name,
                "location": "Egypt",
                "listing_url": f"{self.base_url}/en/product/{hit.get('slug_en', hit.get('id', ''))}",
                "details": details
            }
            return product
        except Exception as e:
            print(f"[Error] Failed to parse Algolia hit: {e}")
            import traceback
            traceback.print_exc()
        return None
    
    async def save_data(self, filename="mobilemasr_products.json"):
        """Save products to JSON file in Dubizzle format"""
        output = {
            "scraped_at": datetime.now().isoformat(),
            "total_products": len(self.products),
            "products": self.products
        }
        
        async with aiofiles.open(filename, "w", encoding="utf-8") as f:
            await f.write(json.dumps(output, indent=2, ensure_ascii=False))
        
        print(f"\n[Saved] {len(self.products)} products to {filename}")

async def main():
    print("="*60)
    print("MOBILEMASR SCRAPER (Algolia API)")
    print("="*60)
    print("\n1. Search for specific product")
    print("2. Scrape all mobile phones")
    
    choice = input("\nChoice (1 or 2): ").strip()
    
    scraper = MobileMasrAlgoliaScraper(max_concurrent=20)
    
    if choice == "1":
        query = input("Product name: ").strip()
        pages = input("Max pages (default 10): ").strip()
        pages = int(pages) if pages.isdigit() else 10
        
        await scraper.scrape_all_products(max_pages=pages, search_query=query)
        
        filename = f"mobilemasr_{query.lower().replace(' ', '_')}_results.json"
        await scraper.save_data(filename)
        
    elif choice == "2":
        pages = input("Max pages (default 10): ").strip()
        pages = int(pages) if pages.isdigit() else 10
        
        await scraper.scrape_all_products(max_pages=pages)
        await scraper.save_data()
        
    else:
        print("[Error] Invalid choice")

if __name__ == "__main__":
    asyncio.run(main())
