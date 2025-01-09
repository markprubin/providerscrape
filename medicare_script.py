import os
import ast
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


import time
from dotenv import load_dotenv

load_dotenv()

# Path to your ChromeDriver
chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')
# Set up the Chrome service
service = Service(chrome_driver_path)
# Initialize the Chrome WebDriver with the specified service
driver = webdriver.Chrome(service=service)
driver.maximize_window()

# Directory for screenshots
screenshots_dir = os.path.join(os.path.dirname(__file__), 'screenshots')

# Create the screenshots directory if it doesn't exist
if not os.path.exists(screenshots_dir):
    os.makedirs(screenshots_dir)


def enter_fullscreen():
    try:
        # Wait for the fullscreen button to be clickable, then click it
        fullscreen_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "DataTableStatusBar__fullScreenBtn"))
        )
        fullscreen_button.click()
        print("Fullscreen mode enabled.")
    except Exception as e:
        print("Error while enabling fullscreen:", e)
        driver.quit()


# Function to search NPI and save a screenshot
def search_npi_and_save(npi, output_screenshot):

    url = "https://data.cms.gov/provider-characteristics/medicare-provider-supplier-enrollment/medicare-fee-for-service-public-provider-enrollment/data"

    driver.get(url)

    enter_fullscreen()

    try:
        # Wait for the search input to be available, then enter the NPI and submit
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".search_input.form-control"))
        )
        search_box.send_keys(str(npi))
        search_box.send_keys(Keys.RETURN)
    except Exception as e:
        print("Error:", e)
        driver.quit()
        return

    # Wait for results to load
    time.sleep(2)  # Adjust if needed based on connection speed and site response time

    # Take a screenshot and save it as PNG
    driver.save_screenshot(output_screenshot)
    print(f"Screenshot saved to {output_screenshot}")

# Parse Lists
doc_ids = ast.literal_eval(os.getenv('DOCID_LIST'))
npi_numbers = ast.literal_eval(os.getenv('NPI_LIST'))

if len(doc_ids) != len(npi_numbers):
    print('Error: DOCID_LIST and NPI_LIST must have same # of entries')
else:
    # Open the website and enter fullscreen mode once
    driver.get("https://data.cms.gov/provider-characteristics/medicare-provider-supplier-enrollment/medicare-fee-for-service-public-provider-enrollment/data")
    enter_fullscreen()

    for doc_id, npi_number in zip(doc_ids, npi_numbers):
        output_screenshot_path = os.path.join(screenshots_dir, f"{doc_id}_Medicare.png")
        search_npi_and_save(npi_number, output_screenshot_path)


driver.quit()
