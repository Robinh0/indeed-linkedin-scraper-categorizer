import os
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from constants import DRIVER_PATH
import platform
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver import Remote, ChromeOptions

# Only import pyvirtualdisplay if you're on a Linux system
# if platform.system() != 'Windows':
#     from pyvirtualdisplay import Display


def setup_scrape_browser():
    SBR_WEBDRIVER = os.getenv("SCRAPING_BROWSER_URI")
    print('Connecting to Scraping Browser...')
    sbr_connection = ChromiumRemoteConnection(SBR_WEBDRIVER, 'goog', 'chrome')
    chrome_options = ChromeOptions()
    chrome_options.add_argument('--blink-settings=imagesEnabled=false')
    return Remote(sbr_connection, options=chrome_options)


def setup_driver():
    """Initializes the Chrome WebDriver instance."""
    chrome_options = uc.ChromeOptions()
    try:
        driver = uc.Chrome(options=chrome_options,
                           service=Service(ChromeDriverManager().install()))
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        return None
    return driver


def create_results_filename(url):
    print(url)
    title = url.split('q=')[1].split('&')[0].replace('+', '_').lower()
    area = url.split('l=')[1].split('&')[0].replace('+', '_').lower()
    return f'{title}_{area}'
