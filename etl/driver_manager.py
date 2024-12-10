import platform
import os
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from webdriver_manager.chrome import ChromeDriverManager

# Import undetected_chromedriver only if the system is Windows
if platform.system() == "Windows":
    import undetected_chromedriver as uc
    from undetected_chromedriver import Chrome


class DriverManager:
    def __init__(self):
        """
        Initializes the DriverManager with no active driver.
        """
        self.driver = None
        self.initialize_driver()

    def _setup_windows_driver(self) -> Chrome:
        """Initializes the Chrome WebDriver instance for Windows."""
        chrome_options = uc.ChromeOptions()
        try:
            driver = uc.Chrome(options=chrome_options,
                               service=Service(ChromeDriverManager().install()))
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            return None
        return driver

    def _setup_scrape_browser(self) -> WebDriver:
        """Initializes the Chrome WebDriver instance through ChromiumRemoteConnection."""
        SBR_WEBDRIVER = os.getenv("SCRAPING_BROWSER_URI")
        print('Connecting to Scraping Browser...')
        sbr_connection = ChromiumRemoteConnection(
            SBR_WEBDRIVER, 'goog', 'chrome')
        chrome_options = ChromeOptions()
        chrome_options.add_argument('--blink-settings=imagesEnabled=false')
        return Remote(sbr_connection, options=chrome_options)

    def initialize_driver(self) -> None:
        """
        Sets up a new WebDriver instance based on the operating system.

        This method initializes the driver as an instance variable.
        """
        if platform.system() == "Windows":
            print("Initializing WebDriver for Windows...")
            self.driver = self._setup_windows_driver()
        else:
            print("Initializing WebDriver for non-Windows system...")
            self.driver = self._setup_scrape_browser()
        self.driver.maximize_window()

    def reset_driver(self, url: str) -> WebDriver:
        """
        Resets the current WebDriver instance, navigating it back to the specified URL.

        Args:
            url (str): The URL to open after resetting the driver.

        Returns:
            WebDriver: The new WebDriver instance.
        """
        print("Resetting the WebDriver...")
        if self.driver:
            # Ensure the previous driver is properly closed.
            self.quit_driver()
        self.initialize_driver()
        self.driver.get(url)
        print(f"Driver navigated to: {url}")
        return self.driver

    def quit_driver(self) -> None:
        """
        Safely quits and cleans up the WebDriver instance.
        """
        if self.driver:
            print("Quitting the WebDriver...")
            self.driver.quit()
            self.driver = None
        else:
            print("No WebDriver instance to quit.")

    def add_cookies(self, cookies):
        """Add cookies to the current session."""
        # Ensure the driver is on the correct domain before adding cookies
        if not self.driver.current_url.startswith('https://www.linkedin.com'):
            raise ValueError(
                "Driver is not on the correct domain. Please navigate to the appropriate page first.")

        for name, value in cookies.items():
            print('Adding cookie')
            self.driver.add_cookie({"name": name, "value": value})
            print('Cookie added')
