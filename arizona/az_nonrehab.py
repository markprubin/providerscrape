import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
from dotenv import load_dotenv

load_dotenv()

# Specialty mapping dictionary
specialty_mapping = {
    "Chiropractor": "Chiropractor",
    "Massage Therapist": "Chiropractor",
    "Naturopath": "Naturopathic Physician",
    "Dietetic": "Registered Dietician"  #Misspelled on AZ's website
}

df = pd.read_excel('/Users/markrubin/Development/providerscrape/arizona/az_nonrehab.xlsx')


def check_provider(driver, first_name, last_name, city, specialty):
    try:
        wait = WebDriverWait(driver, 10)
        mapped_specialty = specialty_mapping.get(specialty, specialty)

        def perform_search(name_input_text):

            # Enter the name and specialty
            name_input = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$txtProviderName")))
            name_input.clear()
            name_input.send_keys(name_input_text)
            print(f"Entered name: {name_input_text}")

            # Select the mapped specialty
            specialty_select = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$ddlSpecialty")))
            Select(specialty_select).select_by_visible_text(mapped_specialty)
            print(f"Selected specialty: {mapped_specialty}")

            # Click the search button
            search_button = wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$btnSearch")))
            search_button.click()
            print("Search button clicked")
            time.sleep(0.5)  # Brief wait for results

        # First Attempt with Full Name
        full_name = f"{first_name} {last_name}"
        perform_search(full_name)

        # Check for No records found message
        no_records_elements = driver.find_elements(By.XPATH, "//p[@class='alert alert-danger']")
        if no_records_elements and no_records_elements[0].is_displayed():
            print("No records found message detected with full name. Retrying with last name only.")

            # Retry with only the last name if full name not found
            perform_search(last_name)

            # Check again for No records found message
            no_records_elements = driver.find_elements(By.XPATH, "//p[@class='alert alert-danger']")
            if no_records_elements and no_records_elements[0].is_displayed():
                print("No records found message detected with last name only. Returning 'N'.")
                return "N"

        # Check Rows if Results Found
        provider_table = wait.until(EC.presence_of_element_located((By.XPATH, "//html/body/form/div[3]/div[2]/div/div/div/div/div/table/tbody")))
        provider_rows = provider_table.find_elements(By.XPATH, ".//tr")

        # Format the expected name, city, and specialty
        expected_first = first_name.strip().upper()
        expected_last = last_name.strip().upper()
        expected_city = city.upper()
        expected_specialty = mapped_specialty.strip().upper()

        found_city = False

        # Check each row for a match
        for row in provider_rows[1:]:
            try:
                provider_name = row.find_element(By.XPATH, ".//td[1]/a").text.strip().upper()
                provider_specialty = row.find_element(By.XPATH, ".//td[2]").text.strip().upper()
                provider_city = row.find_element(By.XPATH, ".//td[4]").text.strip().upper()

                print(f"Checking: {provider_name} - {provider_city} - {provider_specialty}")

                # Match on first and last name or last name alone, and exact specialty match
                if expected_first in provider_name and expected_last in provider_name and expected_specialty == provider_specialty:
                    if expected_city == provider_city:
                        print(f"Match found: {provider_name} - {provider_city} - {provider_specialty}")
                        return "Y"

            except NoSuchElementException as e:
                print(f"Element not found in row: {e}")

        if not found_city:
            print(f"No match found for {expected_first} {expected_last} in {expected_city} with specialty {expected_specialty}")
        return "N"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "N"


chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')
service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)


try:
    driver.get("https://www.azahcccs.gov/Members/ProgramsAndCoveredServices/ProviderListings/")
    print("Page loaded")

    # Update the 'State Enrolled' column based on the match
    df['State Enrolled'] = df.apply(lambda row: check_provider(driver, row['FIRST_NAME'], row['LAST_NAME'], row['CITY'], row['SPECIALTY']), axis=1)

    # # Test with specific values
    # first_name = "David"
    # last_name = "Lewandowski"
    # city = "Kayenta"
    # specialty = "Chiropractor"
    # result = check_provider(driver, first_name, last_name, city, specialty)
    # print(f"Result for {first_name} {last_name}: {result}")

finally:
    driver.quit()

# Save updated dataframe to new Excel file
df.to_excel('/Users/markrubin/Development/providerscrape/arizona/az_nonrehab.xlsx', index=False)
print("Data saved")