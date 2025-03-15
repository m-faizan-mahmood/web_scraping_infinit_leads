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
filename = "data_with_websiteswwwww.csv"

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
e = []  # Tracks already extracted business names to avoid duplicates

def Selenium_extractor():
    action = ActionChains(browser)
    
    # Wait until search results are loaded
    WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CLASS_NAME, "hfpxzc")))
    
    # Find all business listings
    a = browser.find_elements(By.CLASS_NAME, "hfpxzc")
    
    # Scroll until at least 10 listings are available
    while len(a) < 10:
        scroll_origin = ScrollOrigin.from_element(a[-1])
        action.scroll_from_origin(scroll_origin, 0, 10).perform()
        time.sleep(3)
        a = browser.find_elements(By.CLASS_NAME, "hfpxzc")
    
    # Extract only the first 10 listings
    for element in a[:10]:  
        scroll_origin = ScrollOrigin.from_element(element)
        action.scroll_from_origin(scroll_origin, 0, 10).perform()
        action.move_to_element(element).perform()
        element.click()
        time.sleep(10)  # Allow time for the page to load
        
        # Parse the page content
        source = browser.page_source
        soup = BeautifulSoup(source, 'html.parser')
        
        try:
            # Extract Business Name
            name = soup.find('h1', {"class": "DUwDvf lfPIob"}).get_text(strip=True)
            
            # Avoid duplicates
            if name and name not in e:
                e.append(name)
                
                # Extract Phone Number (updated with the correct HTML structure)
                phone_div = soup.find('div', class_='rogA2c')
                phone = None
                if phone_div:
                    phone_number_div = phone_div.find('div', class_='Io6YTe fontBodyMedium kR99db fdkmkc')
                    if phone_number_div:
                        phone = phone_number_div.get_text(strip=True)
                
                # Extract Website
                website_tag = soup.find('a', {"class": "CsEnBe"})
                website = website_tag['href'] if website_tag else None
                
                # Store data if phone or website exists
                if phone or website:
                    print([name, phone, website])
                    record.append((name, phone, website))
        
        except (IndexError, AttributeError) as ex:
            print("Error:", ex)

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
