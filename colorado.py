import os

from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

load_dotenv()

# PLACE FILE PATH HERE
#df = pd.read_excel()

# Degree mapping dictionary
degree_mapping = {
    "PT": "Physical Therapist",
    "OT": "Occupational Therapist",
    "SLP": "Speech Therapist"
}

# Apply degree mapping
df["DEGREE_LONG"] = df["DEGREE"].map(degree_mapping)


def check_provider(driver, last_name, first_name, degree_long):

    try:
        driver.get("https://www.healthfirstcolorado.com/find-doctors/")
        print("Page loaded!")

        # Check for iframes
        iframes = driver.find_elements(By.TAG_NAME, "iframe")
        if iframes:
            print(f"Switching to iframe. Total iframes found: {len(iframes)}")
            driver.switch_to.frame(iframes[0])

        # Wait for "Find Providers by Name" to load and be visible
        wait = WebDriverWait(driver, 10)
        search_input = wait.until(EC.visibility_of_element_located((By.ID, "providerByName")))
        print("Search input found!")

        # Delay typing
        time.sleep(5)

        # Enter full name into search field
        full_name = f"{first_name} {last_name}"
        search_input.clear()
        search_input.send_keys(full_name)
        print(f"Entered {full_name} into search input")

        time.sleep(5)

        # Wait for provider result elements to appear
        provider_elements = wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.content.slds-text-heading_small.card-name")))
        occupation_elements = driver.find_elements(By.CSS_SELECTOR, "div.truncateText.specAndTax")
        print("Provider results located.")

        # Format the expected name
        expected_format = f"{last_name}, {first_name}"

        # Check for a match in results
        for provider, occupation in zip(provider_elements, occupation_elements):
            provider_name = provider.text.strip()
            occupation_text = occupation.text.strip().split(" — ")[0].strip()
            if occupation_text == degree_long and expected_format in provider_name:
                formatted_result = f"{provider_name}: {occupation_text}"
                print(f"Match found for {expected_format}!")

    except Exception as e:
        print(f"An error occurred: {e}")


# Path to your ChromeDriver
chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')
# Set up the Chrome service
service = Service(chrome_driver_path)
# Initialize the Chrome WebDriver with the specified service
driver = webdriver.Chrome(service=service)

try:
    df['State Enrolled'] = df.apply(lambda row: check_provider(driver, row['LAST_NAME'], row['FIRST_NAME'], row['DEGREE_LONG']), axis=1)
finally:
    driver.quit()


# Place file path here
# df.toexcel()

print(df)