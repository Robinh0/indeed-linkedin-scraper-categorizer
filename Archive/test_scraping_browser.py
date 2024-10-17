from dotenv import load_dotenv
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver.common.by import By
from extract import STARTING_URL
import time
import os

# Load environment variables
load_dotenv()

SBR_WEBDRIVER = os.getenv("SCRAPING_BROWSER_URI")


def main():
    print('Connecting to Scraping Browser...')
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    with Remote(sbr_connection, options=ChromeOptions()) as driver:
        print('Connected! Navigating...')
        # use this, or replace with URL of your choice
        driver.get(STARTING_URL)
        time.sleep(10)
        print('Taking page screenshot to file page.png')
        driver.get_screenshot_as_file('./page.png')
        print('Navigated! Scraping page content...')
        html = driver.page_source
        print(html)


if __name__ == '__main__':
    main()
