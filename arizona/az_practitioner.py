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

            # Check again for no records message
            no_record_elements = driver.find_elements(By.XPATH, "//p[@class=alert alert-danger']")
            if no_record_elements and no_record_elements[0].is_displayed():
                print("No records message detected with full name. Retrying with last name only")
                return "N - Perform manual check"

        # Format expected bane and speciality
        expected_first = first_name.strip().upper()
        expected_last = last_name.strip().upper()
        expected_specialty = mapped_specialty.strip().upper()

        # Set ellipsis link to false for later utilization
        clicked_ellipsis = False

        # Loop to handle pagination when necessary
        while True:
            # Check rows if Results Found in either case
            provider_table = wait.until(EC.presence_of_element_located((By.XPATH, "//html/body/form/div[3]/div[2]/div/div/div/div/div/table/tbody")))
            provider_rows = provider_table.find_elements(By.XPATH, ".//tr")

            # Check each row for a match (skip first row as it is a header row)
            for row in provider_rows[1:]:
                try:
                    provider_name = row.find_element(By.XPATH, ".//td[1]/a").text.strip().upper()
                    provider_specialty = row.find_element(By.XPATH, ".//td[2]").text.strip().upper()

                    print(f"Checking: {provider_name} - {provider_specialty}")

                    # Match on first and last name or last name alone, and exact specialty match
                    if expected_first in provider_name and expected_last in provider_name and expected_specialty == provider_specialty:
                        print(f"Match found: {provider_name} - {provider_specialty}")
                        return "Y"

                except NoSuchElementException as e:
                    print(f"Element not found in row: {e}")

            # Check for presence of a numbered pagination link
            try:
                pagination_row = driver.find_element(By.XPATH, "//tr[@class='pagination-ys']")
                page_links = pagination_row.find_elements(By.XPATH, ".//td/a[contains(@href, 'Page$')]")
                current_page = pagination_row.find_element(By.XPATH, ".//td/span").text.strip()

                next_page_clicked = False

                for link in page_links:
                    page_number = link.text.strip()
                    if page_number == "..." and not clicked_ellipsis:
                        link.click()
                        print("Next set of pages link clicked")
                        time.sleep(1)
                        next_page_clicked = True
                        clicked_ellipsis = True
                        break
                    elif page_number.isdigit() and int(page_number) > int(current_page):
                        link.click()
                        print(f"Page {page_number} clicked")
                        time.sleep(1)
                        next_page_clicked = True
                        break

                if not next_page_clicked:
                    break

            except NoSuchElementException:
                break

        print(f"No match found for {expected_first} {expected_last} with speciality {expected_specialty}")
        return "N"

    except Exception as e:
        print(f"An error occured: {e}")
        return "N"