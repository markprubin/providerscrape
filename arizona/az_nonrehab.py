from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pandas as pd

# Specialty mapping dictionary
specialty_mapping = {
    "Chiropractor": "Chiropractor",
    "Massage Therapist": "Chiropractor",
    "Naturopathic Physician": "Naturopathic Physician",
    "Dietetic": "Registered Dietician"
}

df = pd.read_excel('file path') #Add file path here

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
        if no_records_message.is_displayed():
            print("No records found message detected.")
            return "N"
        except TimeoutException as e:
            return "Y"