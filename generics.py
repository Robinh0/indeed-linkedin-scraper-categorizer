import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

DRIVER_PATH = "C:/Users/robin/Documents/App files/chromedriver-win64/chromedriver-win64/chromedriver.exe"


def setup_driver():
    """Sets up the Chrome WebDriver with specified options."""
    chrome_options = Options()
    service = Service(DRIVER_PATH)
    # driver = webdriver.Chrome(service=service, options=chrome_options)
    # Using the undetectable chromedriver here.
    driver = uc.Chrome(
        options=chrome_options, service=service
    )
    return driver
