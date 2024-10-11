import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from constants import DRIVER_PATH
import platform

# Only import pyvirtualdisplay if you're on a Linux system
if platform.system() != 'Windows':
    from pyvirtualdisplay import Display


def setup_driver():
    """Sets up the Chrome WebDriver with specified options."""

    if platform.system() != 'Windows':
        # Set visible to 1 for GUI
        display = Display(visible=False, size=(800, 600))
        display.start()  # Start the virtual display

    driver = initialize_chrome_driver()

    # # Testing an HTTP request
    # driver.get("http://www.example.com")
    # print(driver.page_source)

    # # Testing an HTTPS request
    # driver.get("https://www.example.com")
    # print(driver.page_source)

    return driver


def initialize_chrome_driver():
    """Initializes the Chrome WebDriver instance."""
    chrome_options = uc.ChromeOptions()
    # PROXY = "178.128.199.145:80"
    # chrome_options.add_argument(f'--proxy-server={PROXY}')
    service = Service(DRIVER_PATH)

    # Create the undetected Chrome WebDriver instance
    try:
        driver = uc.Chrome(options=chrome_options,
                           service=service, headless=False)
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        return None

    return driver
