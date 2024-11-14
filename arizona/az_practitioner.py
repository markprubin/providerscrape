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

# Degree mapping dictionary
specialty_mapping = {
    "OT": "Therapist-Occupational",
    "PT": "Therapist-Physical",
    "LPT": "Therapist-Psychiatric"
}

df = pd.read_excel('/Users/MarkRu/OneDrive - American Specialty Health, Inc/Desktop/Development/Medicaid Scripts/arizona_scripts/az_practitioner.xlsx')

def check_provider(driver, first_name, last_name, speciality):
    try:
        wait = WebDriverWait(driver, 5)
        mapped_specialty = specialty_mapping.get(speciality, speciality)

        def perform_search(name_input_text):

            name_input = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$txtProviderName")))
            name_input.clear()
            name_input.send_keys(name_input_text)
            print(f"Entered name: {name_input_text}")

            time.sleep(0.5)

            # Select the mapped specialty
            specialty_select = wait.until(EC.visibility_of_element_located((By.NAME, "ctl00$ContentPlaceHolder1$ddlSpecialty")))
            Select(specialty_select).select_by_visible_text(mapped_specialty)
            print(f"Selected specialty: {mapped_specialty}")

            # Click the search button
            search_button = wait.until(EC.element_to_be_clickable((By.NAME, "ctl00$ContentPlaceHolder1$btnSearch")))
            search_button.click()
            print("Search button clicked")

        # First attempt with Full Name
        full_name = f"{first_name} {last_name}"
        perform_search(full_name)

        time.sleep(0.5)
        # Check for No Records Found message
        no_record_elements = driver.find_elements(By.XPATH, "//p[@class=alert alert-danger']")
        if no_record_elements and no_record_elements[0].is_displayed():
            print("No records message detected with full name. Retrying with last name only")

            # Retry with last name
            perform_search(last_name)

            time.sleep(0.5)
