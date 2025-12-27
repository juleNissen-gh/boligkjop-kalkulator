"""
Web scraper for finn.no property listings in Trondheim using Selenium
Extracts: Total price (inkl. fellesgjeld), Number of bedrooms, and Felleskostnad
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
import time
import json
from typing import List, Dict
import re
from loan_calculator import calculate_loan


class FinnPropertyScraperSelenium:
    def __init__(self, headless: bool = True):
        """
        Initialize the scraper with Selenium
        headless: Run browser in headless mode (no visible window)
        """
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

        # Auto-install ChromeDriver
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.base_url = "https://www.finn.no"
        self.wait = WebDriverWait(self.driver, 10)

    def get_property_listings(self, search_url: str = None) -> List[str]:
        """
        Get property listing URLs from search results
        search_url: Custom search URL with filters, or None for default Trondheim search
        """
        if search_url is None:
            search_url = f"{self.base_url}/realestate/homes/search.html?location=0.20001"

        property_urls = []

        try:
            print(f"Loading search page: {search_url}")
            self.driver.get(search_url)

            # Wait for page to load
            time.sleep(1)

            # Try to find property links
            # Look for links that contain /realestate/homes/ad.html
            links = self.driver.find_elements(By.TAG_NAME, 'a')

            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and ('/realestate/homes/ad.html' in href or '/ad.html?finnkode=' in href):
                        # Skip project listings (multiple apartments) and planned properties
                        if '/realestate/project/' in href or '/realestate/projectsingle/' in href or '/realestate/planned/' in href:
                            continue
                        if href not in property_urls:
                            property_urls.append(href)
                except:
                    continue

            print(f"Found {len(property_urls)} property listings")

            if len(property_urls) == 0:
                # Save screenshot for debugging
                self.driver.save_screenshot('finn_search_screenshot.png')
                print("No properties found. Screenshot saved to finn_search_screenshot.png")
                print("Check if there are actually listings on finn.no for Trondheim")

        except Exception as e:
            print(f"Error fetching listings: {e}")
            self.driver.save_screenshot('error_screenshot.png')

        return property_urls

    def scrape_property(self, url: str) -> Dict:
        """
        Scrape individual property page for required information
        """
        property_data = {
            'url': url,
            'totalpris_inkl_fellesgjeld': None,
            'antall_soverom': None,
            'felleskostnad': None
        }

        try:
            self.driver.get(url)
            time.sleep(1.5)  # Increased wait time for page to load

            # Check if we got blocked or redirected
            current_url = self.driver.current_url
            if 'blocked' in current_url.lower() or current_url != url:
                print(f"  WARNING: Possible redirect or block. Current URL: {current_url}")
                property_data['error'] = f'Redirected to {current_url}'
                return property_data

            # Get all text content
            page_text = self.driver.page_source

            # Try to find elements with specific text
            # Strategy 1: Look for dl/dt/dd elements (definition lists)
            try:
                dl_elements = self.driver.find_elements(By.TAG_NAME, 'dl')
                for dl in dl_elements:
                    try:
                        dts = dl.find_elements(By.TAG_NAME, 'dt')
                        dds = dl.find_elements(By.TAG_NAME, 'dd')

                        for dt, dd in zip(dts, dds):
                            label = dt.text.lower().strip()
                            value = dd.text.strip()

                            if 'totalpris' in label:
                                property_data['totalpris_inkl_fellesgjeld'] = self._extract_price(value)

                            elif 'soverom' in label:
                                property_data['antall_soverom'] = self._extract_number(value)

                            elif 'felleskost' in label or 'fellesutgifter' in label:
                                property_data['felleskostnad'] = self._extract_price(value)
                    except:
                        continue
            except:
                pass

            # Strategy 2: Search through all visible text on the page
            try:
                body_text = self.driver.find_element(By.TAG_NAME, 'body').text

                # Look for "Totalpris" followed by a price
                totalpris_match = re.search(r'Totalpris.*?(\d[\d\s]+)', body_text)
                if totalpris_match and not property_data['totalpris_inkl_fellesgjeld']:
                    property_data['totalpris_inkl_fellesgjeld'] = self._extract_price(totalpris_match.group(1))

                # Look for bedroom count
                soverom_match = re.search(r'(\d+)\s*soverom', body_text, re.IGNORECASE)
                if soverom_match and not property_data['antall_soverom']:
                    property_data['antall_soverom'] = int(soverom_match.group(1))

                # Look for felleskostnad (multiple patterns)
                felles_match = re.search(r'Felleskost(?:nad|/mnd\.).*?(\d[\d\s]+)', body_text)
                if felles_match and not property_data['felleskostnad']:
                    property_data['felleskostnad'] = self._extract_price(felles_match.group(1))

            except:
                pass

            # Strategy 3: Try to find data in structured elements
            try:
                # Look for divs or sections with class containing "info", "data", "details"
                info_sections = self.driver.find_elements(By.XPATH,
                    "//*[contains(@class, 'info') or contains(@class, 'data') or contains(@class, 'details')]")

                for section in info_sections:
                    text = section.text

                    if 'Totalpris' in text and not property_data['totalpris_inkl_fellesgjeld']:
                        property_data['totalpris_inkl_fellesgjeld'] = self._extract_price(text)

                    if 'soverom' in text.lower() and not property_data['antall_soverom']:
                        property_data['antall_soverom'] = self._extract_number(text)

                    if 'Felleskostnad' in text and not property_data['felleskostnad']:
                        property_data['felleskostnad'] = self._extract_price(text)
            except:
                pass

        except Exception as e:
            print(f"  ERROR scraping property {url}: {e}")
            property_data['error'] = str(e)

        # Log what we found (or didn't find)
        missing = []
        if not property_data['totalpris_inkl_fellesgjeld']:
            missing.append('totalpris')
        if not property_data['antall_soverom']:
            missing.append('soverom')
        if not property_data['felleskostnad']:
            missing.append('felleskostnad')

        if missing:
            print(f"  WARNING: Missing data: {', '.join(missing)}")
            # Save screenshot for debugging
            try:
                screenshot_name = f"debug_{url.split('finnkode=')[-1]}.png"
                self.driver.save_screenshot(screenshot_name)
                print(f"  Screenshot saved to {screenshot_name}")
            except:
                pass

        return property_data

    def _extract_price(self, text: str) -> int:
        """Extract price from text (removes spaces, 'kr', etc.)"""
        if not text:
            return None
        # Remove non-numeric characters except digits
        numbers = re.findall(r'\d+', text.replace(' ', ''))
        if numbers:
            return int(''.join(numbers))
        return None

    def _extract_number(self, text: str) -> int:
        """Extract a single number from text"""
        if not text:
            return None
        numbers = re.findall(r'\d+', text)
        if numbers:
            return int(numbers[0])
        return None

    def scrape_all(self, search_url: str = None, max_price: int = None, loan_params: dict = None) -> List[Dict]:
        """
        Scrape all properties from Trondheim
        search_url: Custom search URL with filters
        max_price: Maximum property price to consider
        loan_params: Loan calculation parameters
        """
        try:
            print("Fetching property listings...")
            property_urls = self.get_property_listings(search_url=search_url)

            results = []
            consecutive_over_budget = 0
            max_consecutive_over_budget = 3  # Stop after 3 consecutive properties over budget

            for i, url in enumerate(property_urls, 1):
                print(f"Scraping property {i}/{len(property_urls)}: {url}")
                data = self.scrape_property(url)

                # Filter by max price if specified
                if max_price and data.get('totalpris_inkl_fellesgjeld'):
                    if data['totalpris_inkl_fellesgjeld'] > max_price:
                        print(f"  Skipping: price {data['totalpris_inkl_fellesgjeld']:,} kr > {max_price:,} kr")
                        consecutive_over_budget += 1

                        # If results are sorted by price and we've hit multiple over budget, stop
                        if consecutive_over_budget >= max_consecutive_over_budget:
                            print(f"\nStopping: Found {max_consecutive_over_budget} consecutive properties over budget.")
                            print(f"Remaining properties will also be over {max_price:,} kr.")
                            break
                        continue
                    else:
                        # Reset counter if we find one within budget
                        consecutive_over_budget = 0

                # Calculate loan if we have all required data and loan_params
                if loan_params and data.get('totalpris_inkl_fellesgjeld') and data.get('antall_soverom') and data.get('felleskostnad'):
                    try:
                        loan_result = calculate_loan(
                            property_price=data['totalpris_inkl_fellesgjeld'],
                            down_payment=loan_params['down_payment'],
                            loan_term_years=loan_params['loan_term_years'],
                            annual_interest_rate=loan_params['annual_interest_rate'],
                            num_bedrooms=data['antall_soverom'],
                            num_co_owners=loan_params['num_co_owners'],
                            rent_per_room=loan_params['rent_per_room'],
                            total_common_costs=data['felleskostnad'],
                            annual_appreciation_rate=loan_params['annual_appreciation_rate'],
                        )
                        data['loan_calculation'] = loan_result
                    except Exception as e:
                        print(f"  Error calculating loan: {e}")
                        data['loan_calculation'] = None

                results.append(data)

                # Be polite - add delay between requests (increased to avoid rate limiting)
                time.sleep(1.0)

            # Sort by net_monthly_cost if loan calculations were done
            if loan_params:
                results = sorted(
                    results,
                    key=lambda x: x.get('loan_calculation', {}).get('net_monthly_cost', float('inf'))
                )

            return results

        finally:
            # Always close the browser
            self.close()

    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()


def main():
    """
    Example usage
    """
    # Try to load personal config, fall back to example values
    try:
        from my_config import SEARCH_URL, LOAN_PARAMS, MAX_PRICE
        search_url = SEARCH_URL
        loan_params = LOAN_PARAMS
        max_price = MAX_PRICE
        print("Using configuration from my_config.py")
    except ImportError:
        print("my_config.py not found - using example values")
        print("Create my_config.py with your personal settings (see README)")

        # Example values - replace these or create my_config.py
        search_url = "<Insert your finn.no search URL here>"
        loan_params = {
            'down_payment': 500_000,  # Your down payment (egenkapital)
            'loan_term_years': 30,
            'annual_interest_rate': 0.05,
            'num_co_owners': 2,
            'rent_per_room': 6_000,
            'annual_appreciation_rate': 0.03,
        }
        max_price = 5_000_000

    scraper = FinnPropertyScraperSelenium(headless=False)  # Set to True to hide browser

    try:
        # Scrape all properties up to max_price
        properties = scraper.scrape_all(
            search_url=search_url,
            max_price=max_price,
            loan_params=loan_params
        )

        # Display results
        print("\n" + "="*80)
        print("RESULTS (sorted by lowest net monthly cost)")
        print("="*80 + "\n")

        for i, prop in enumerate(properties, 1):
            print(f"Property {i}:")
            print(f"  URL: {prop.get('url')}")

            price = prop.get('totalpris_inkl_fellesgjeld')
            print(f"  Totalpris: {price:,} kr" if price else "  Totalpris: N/A")
            print(f"  Antall soverom: {prop.get('antall_soverom')}" if prop.get('antall_soverom') else "  Antall soverom: N/A")

            felles = prop.get('felleskostnad')
            print(f"  Felleskostnad: {felles:,} kr" if felles else "  Felleskostnad: N/A")

            if prop.get('loan_calculation'):
                loan = prop['loan_calculation']
                print(f"\n  === Lånekalkulator ===")
                print(f"  Månedlig lånebetaling:        {loan['monthly_payment']:>10,.0f} kr")
                print(f"  Din del av felleskostnad:     {loan['your_common_costs']:>10,.0f} kr")
                print(f"  Din andel av utleieinntekt:   {loan['your_rental_income']:>10,.0f} kr")
                print(f"  Netto månedlig kostnad:       {loan['net_monthly_cost']:>10,.0f} kr")
                print(f"  Netto etter verdistigning:    {loan['net_after_appreciation']:>10,.0f} kr")
            print()

        # Save to JSON file
        with open('finn_properties_selenium.json', 'w', encoding='utf-8') as f:
            json.dump(properties, f, ensure_ascii=False, indent=2)

        print(f"Results saved to finn_properties_selenium.json")
        print(f"Total properties found: {len(properties)}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        scraper.close()


if __name__ == "__main__":
    main()
