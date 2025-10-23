#!/usr/bin/env python3
"""
Mobile Phone Data Scraper - Unified Interactive CLI
Runs both Dubizzle and MobileMasr scrapers
"""

import asyncio
import sys
import os

# Add subdirectories to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'DubbizleSrapper'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'MobileMasrScrapper'))

# Import scrapers
from DubbizleSrapper.main import DubizzleScraper
from MobileMasrScrapper.main import MobileMasrAlgoliaScraper


def print_header():
    """Print application header"""
    print("=" * 70)
    print("MOBILE PHONE DATA SCRAPER".center(70))
    print("Unified Interactive CLI for Dubizzle & MobileMasr".center(70))
    print("=" * 70)
    print()


def print_menu():
    """Print main menu"""
    print("Available Scrapers:")
    print()
    print("  1. Dubizzle Scraper (Selenium-based)")
    print("  2. MobileMasr Scraper (Algolia API)")
    print("  3. Run Both Scrapers")
    print("  4. Exit")
    print()


async def run_dubizzle():
    """Run Dubizzle scraper"""
    print("\n" + "=" * 70)
    print("DUBIZZLE SCRAPER (Selenium)".center(70))
    print("=" * 70)
    print()
    print("Options:")
    print("  1. Search for specific product")
    print("  2. Scrape all mobile phones")
    print()
    
    choice = input("Choice (1 or 2): ").strip()
    
    scraper = DubizzleScraper(max_workers=10)
    
    try:
        if choice == "1":
            query = input("Product name: ").strip()
            if not query:
                print("[Error] Search query cannot be empty")
                return
            
            pages = input("Max pages (default 10): ").strip()
            pages = int(pages) if pages.isdigit() else 10
            
            # Change to DubbizleSrapper directory for output
            original_dir = os.getcwd()
            os.chdir(os.path.join(os.path.dirname(__file__), 'DubbizleSrapper'))
            
            await scraper.scrape_search(query, max_pages=pages)
            filename = f"{query.lower().replace(' ', '_')}_results.json"
            await scraper.save_data(filename)
            
            os.chdir(original_dir)
            
        elif choice == "2":
            pages = input("Max pages (default 10): ").strip()
            pages = int(pages) if pages.isdigit() else 10
            
            # Change to DubbizleSrapper directory for output
            original_dir = os.getcwd()
            os.chdir(os.path.join(os.path.dirname(__file__), 'DubbizleSrapper'))
            
            await scraper.scrape_all_pages(max_pages=pages)
            await scraper.save_data()
            
            os.chdir(original_dir)
            
        else:
            print("[Error] Invalid choice")
    finally:
        scraper.cleanup()


async def run_mobilemasr():
    """Run MobileMasr scraper"""
    print("\n" + "=" * 70)
    print("MOBILEMASR SCRAPER (Algolia API)".center(70))
    print("=" * 70)
    print()
    print("Options:")
    print("  1. Search for specific product")
    print("  2. Scrape all mobile phones")
    print()
    
    choice = input("Choice (1 or 2): ").strip()
    
    scraper = MobileMasrAlgoliaScraper(max_concurrent=20)
    
    if choice == "1":
        query = input("Product name: ").strip()
        pages = input("Max pages (default 10): ").strip()
        pages = int(pages) if pages.isdigit() else 10
        
        # Change to MobileMasrScrapper directory for output
        original_dir = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), 'MobileMasrScrapper'))
        
        await scraper.scrape_all_products(max_pages=pages, search_query=query)
        filename = f"mobilemasr_{query.lower().replace(' ', '_')}_results.json"
        await scraper.save_data(filename)
        
        os.chdir(original_dir)
        
    elif choice == "2":
        pages = input("Max pages (default 10): ").strip()
        pages = int(pages) if pages.isdigit() else 10
        
        # Change to MobileMasrScrapper directory for output
        original_dir = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), 'MobileMasrScrapper'))
        
        await scraper.scrape_all_products(max_pages=pages)
        await scraper.save_data()
        
        os.chdir(original_dir)
        
    else:
        print("[Error] Invalid choice")


async def run_both():
    """Run both scrapers sequentially"""
    print("\n" + "=" * 70)
    print("RUNNING BOTH SCRAPERS".center(70))
    print("=" * 70)
    print()
    
    # Get common settings
    print("Common Settings:")
    search_mode = input("Search mode? (y/N): ").strip().lower() == 'y'
    
    query = ""
    if search_mode:
        query = input("Product name: ").strip()
        if not query:
            print("[Error] Search query cannot be empty")
            return
    
    pages = input("Max pages (default 10): ").strip()
    pages = int(pages) if pages.isdigit() else 10
    
    # Run Dubizzle
    print("\n" + "-" * 70)
    print("Starting Dubizzle Scraper...".center(70))
    print("-" * 70)
    dubizzle_scraper = DubizzleScraper(max_workers=10)
    
    try:
        original_dir = os.getcwd()
        os.chdir(os.path.join(os.path.dirname(__file__), 'DubbizleSrapper'))
        
        if search_mode:
            await dubizzle_scraper.scrape_search(query, max_pages=pages)
            filename = f"{query.lower().replace(' ', '_')}_results.json"
            await dubizzle_scraper.save_data(filename)
        else:
            await dubizzle_scraper.scrape_all_pages(max_pages=pages)
            await dubizzle_scraper.save_data()
        
        os.chdir(original_dir)
    finally:
        dubizzle_scraper.cleanup()
    
    # Run MobileMasr
    print("\n" + "-" * 70)
    print("Starting MobileMasr Scraper...".center(70))
    print("-" * 70)
    mobilemasr_scraper = MobileMasrAlgoliaScraper(max_concurrent=20)
    
    original_dir = os.getcwd()
    os.chdir(os.path.join(os.path.dirname(__file__), 'MobileMasrScrapper'))
    
    if search_mode:
        await mobilemasr_scraper.scrape_all_products(max_pages=pages, search_query=query)
        filename = f"mobilemasr_{query.lower().replace(' ', '_')}_results.json"
        await mobilemasr_scraper.save_data(filename)
    else:
        await mobilemasr_scraper.scrape_all_products(max_pages=pages)
        await mobilemasr_scraper.save_data()
    
    os.chdir(original_dir)
    
    print("\n" + "=" * 70)
    print("BOTH SCRAPERS COMPLETED".center(70))
    print("=" * 70)


async def main():
    """Main application loop"""
    while True:
        print_header()
        print_menu()
        
        choice = input("Select an option (1-4): ").strip()
        
        if choice == "1":
            await run_dubizzle()
        elif choice == "2":
            await run_mobilemasr()
        elif choice == "3":
            await run_both()
        elif choice == "4":
            print("\nExiting... Goodbye!")
            break
        else:
            print("\n[Error] Invalid choice. Please select 1-4.")
        
        # Ask if user wants to continue
        print()
        continue_choice = input("Run another scraper? (Y/n): ").strip().lower()
        if continue_choice == 'n':
            print("\nExiting... Goodbye!")
            break
        print("\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
        sys.exit(0)
