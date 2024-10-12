import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from constants import DRIVER_PATH
import platform
from webdriver_manager.chrome import ChromeDriverManager


# Only import pyvirtualdisplay if you're on a Linux system
if platform.system() != 'Windows':
    from pyvirtualdisplay import Display


def setup_driver():
    """Sets up the Chrome WebDriver with specified options."""

    if platform.system() != 'Windows':
        with Display(visible=False, size=(800, 600)) as display:
            driver = initialize_chrome_driver('Linux')
            print(f"Virtual display started: {display.is_alive()}")
    else:
        driver = initialize_chrome_driver('Windows')
    return driver


def initialize_chrome_driver(platform):
    """Initializes the Chrome WebDriver instance."""
    chrome_options = uc.ChromeOptions()

    # Create the undetected Chrome WebDriver instance
    try:
        if platform == 'Windows':
            driver = uc.Chrome(options=chrome_options,
                               service=Service(ChromeDriverManager().install()))
        else:
            chrome_options.add_argument(
                "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36"
            )
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-usage")
            driver = uc.Chrome(options=chrome_options,
                               service=Service(ChromeDriverManager().install()))

        driver.set_page_load_timeout(30)  # Set a reasonable timeout
        driver.implicitly_wait(10)  # Implicit wait for elements to load
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        return None

    return driver
