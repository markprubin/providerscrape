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
    "Naturopathic Physician": "Naturopathic Physician",
    "Dietetic": "Registered Dietician"  #Misspelled on AZ's website
}

# df = pd.read_excel('file path') #Add file path here


def check_provider(driver, first_name, last_name, city, specialty):
    try:
        wait = WebDriverWait(driver, 10)

        # Map the specialty using the dictionary
        mapped_specialty = specialty_mapping.get(specialty, specialty)

        # Wait for name input to be visible and enter the name value
        name_input = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$txtProviderName")))
        name_input.send_keys(Keys.CONTROL + "a")
        name_input.send_keys(Keys.DELETE)
        name_input.send_keys(first_name + " " + last_name)
        print(f"Entered name: {first_name} {last_name}")

        time.sleep(2)

        # Wait for the city input field to be visible and enter the city value
        city_input = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$txtCity")))
        city_input.send_keys(Keys.CONTROL + "a")
        city_input.send_keys(Keys.DELETE)
        city_input.send_keys(city)
        print(f"Entered city: {city}")

        time.sleep(2)

        # Wait for specialty dropdown to be visible and select the specialty value
        specialty_select = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$ddlSpecialty")))
        Select(specialty_select).select_by_visible_text(mapped_specialty)
        print(f"Selected specialty: {mapped_specialty}")

        time.sleep(2)

        # Search Button functionality
        search_button = wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$btnSearch")))
        search_button.click()
        print("Search button clicked")

        time.sleep(2)

        # Check for "No records found" message
        no_records_message = wait.until(EC.presence_of_element_located((By.XPATH, "//p[@class='alert alert-danger']")))
        try:
            if no_records_message.is_displayed():
                print("No records found message detected.")
                return "N"
        except TimeoutException as e:
            return "Y"

        # Wait for the provider rows to be visible
        provider_table = wait.until(EC.presence_of_element_located((By.XPATH, "//html/body/form/div[3]/div[2]/div/div/div/div/div/table/tbody")))
        provider_rows = provider_table.find_elements(By.XPATH, ".//tr")

        # Format the expected name
        expected_name = (first_name + " " + last_name).upper()
        expected_city = city.upper()
        expected_specialty = specialty.upper()

        for row in provider_rows[1:]:
            try:
                provider_name = row.find_element(By.XPATH, ".//td[1]/a").text.strip().upper()
                provider_city = row.find_element(By.XPATH, ".//td[2]").text.strip().upper()
                provider_specialty = row.find_element(By.XPATH, ".//td[4]").text.strip().upper()

                print(f"Checking: {provider_name} - {provider_city} - {provider_specialty}")

                if expected_name in provider_name and expected_city in provider_city and expected_specialty in provider_specialty:
                    print(f"Match found: {provider_name} - {provider_city} - {provider_specialty}")
                    return "Y"

            except NoSuchElementException as e:
                print(f"Element not found in row: {e}")

        print(f"No match found for {expected_name} in {expected_city} with specialty {expected_specialty}")
        return "N"

    except Exception as e:
        print(f"An error occurred: {e}")
        return "N"


# Specify the path to the chromedriver executable
chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')

service = Service(chrome_driver_path)
driver = webdriver.Chrome(service=service)


try:
    driver.get("https://www.azahcccs.gov/Members/ProgramsAndCoveredServices/ProviderListings/")
    print("Page loaded")

    # # Update the 'State Enrolled' column based on the match
    # df['State Enrolled'] = df.apply(lambda row: check_provider(driver, row['FIRST_NAME'], row['LAST_NAME'], row['CITY'], row['SPECIALTY']), axis=1)

    # Test with specific values
    first_name = "David"
    last_name = "Lewandowski"
    city = "Kayenta"
    specialty = "Chiropractor"
    result = check_provider(driver, first_name, last_name, city, specialty)
    print(f"Result for {first_name} {last_name}: {result}")

finally:
    driver.quit()
#
# # Save updated dataframe to new Excel file
# df.to_excel('/Users/MarkRu/OneDrive - American Specialty Health, Inc/Desktop/Development/Medicaid Scripts/arizona_scripts/az_nonrehab_updated.xlsx', index=False)
# print("Data saved")