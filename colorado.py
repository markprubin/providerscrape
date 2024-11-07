from selenium import webdriver
from selenium.webdriver.chrome.service import Service

import time
import pandas as pd


load_dotenv()

chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')
# Set up the Chrome service
service = Service(chrome_driver_path)
# Initialize the Chrome WebDriver
driver = webdriver.Chrome(service=service)