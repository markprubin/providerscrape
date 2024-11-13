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

