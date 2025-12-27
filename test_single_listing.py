"""
Test scraper on a single listing to debug
"""
from finn_scraper_selenium import FinnPropertyScraperSelenium
import json

url = "https://www.finn.no/realestate/homes/ad.html?finnkode=443125576"

scraper = FinnPropertyScraperSelenium(headless=False)

try:
    print(f"Testing URL: {url}\n")

    data = scraper.scrape_property(url)

    print("\n=== RESULTS ===")
    print(json.dumps(data, indent=2, ensure_ascii=False))

    # Also save page source for inspection
    with open('page_source.html', 'w', encoding='utf-8') as f:
        f.write(scraper.driver.page_source)
    print("\nPage source saved to page_source.html for inspection")

finally:
    input("\nPress Enter to close browser...")
    scraper.close()
