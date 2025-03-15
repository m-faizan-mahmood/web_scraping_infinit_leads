from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import time
import pandas as pd
import urllib.parse  # For URL encoding

# Path to the ChromeDriver
chrome_driver_path = r'chromedriver.exe'  # Replace with your actual path

# Output CSV filename
filename = "data_with_websites1.csv"

# Prompt user for the search query (e.g., "car dealers in USA")
search_query = input("Enter the search query (e.g., 'car dealers in USA'): ")

# Encode the search query to be URL-friendly
encoded_query = urllib.parse.quote(search_query)

# Construct the Google Maps search URL with the user-input search query
link = f"https://www.google.com/maps/search/{encoded_query}"

# Initialize WebDriver
service = Service(chrome_driver_path)
browser = webdriver.Chrome(service=service)

# Data storage lists
record = []  # Stores extracted business data
e = []  # Initialize 'e' here in the global scope to avoid scoping issues

def Selenium_extractor():
    action = ActionChains(browser)
    
    # Wait until search results are loaded
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "hfpxzc")))
    
    # Find all business listings
    listings = browser.find_elements(By.CLASS_NAME, "hfpxzc")[:2]  # Only the first 2 listings
    
    # Extract phone numbers for each of the first 2 listings
    for i, listing in enumerate(listings, 1):
        print(f"Extracting phone number from Listing {i}...")
        
        # Scroll to the element and click
        ActionChains(browser).move_to_element(listing).click().perform()
        time.sleep(5)  # Wait for the listing page to load
        
        # Wait for the phone button to appear (using explicit wait)
        phone_button = WebDriverWait(browser, 10).until(
            EC.presence_of_element_located((By.XPATH, '//button[contains(@aria-label, "Phone:")]'))
        )
        
        # Extract the phone number from the 'aria-label' attribute
        phone_number = phone_button.get_attribute('aria-label').replace("Phone: ", "").strip()
        print(f"Phone Number for Listing {i}: {phone_number}")
        
        # Extract the business name from the page
        source = browser.page_source
        soup = BeautifulSoup(source, 'html.parser')
        
        try:
            name = soup.find('h1', {"class": "DUwDvf lfPIob"}).get_text(strip=True)
            
            # Avoid duplicates
            if name and name not in e:
                e.append(name)
                
                # Extract Website
                website_tag = soup.find('a', {"class": "CsEnBe"})
                website = website_tag['href'] if website_tag else None
                
                # Store data if phone or website exists
                if phone_number or website:
                    print([name, phone_number, website])
                    record.append((name, phone_number, website))
        except Exception:
            pass  # Skip if there is any error during extraction
    
    # Save data to CSV if records exist
    if record:
        df = pd.DataFrame(record, columns=['Name', 'Phone number', 'Website'])
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"\n✅ Data has been successfully saved to {filename}!")

# Run the script
try:
    browser.get(link)
    time.sleep(10)  # Initial delay for page load
    Selenium_extractor()
finally:
    browser.quit()
