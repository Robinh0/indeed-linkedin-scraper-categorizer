import os
import undetected_chromedriver as uc
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from selenium.webdriver import Remote, ChromeOptions
from langdetect import detect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from constants import STARTING_URL


# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')


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


def get_filename(ending: str, url: str = STARTING_URL):
    """
    Generates a formatted filename based on the provided URL and a specified ending.

    This function takes a URL string, extracts the `q` (query) and `l` (location) parameters,
    formats them by replacing spaces (`+`) with underscores (`_`) and converting the result to lowercase.
    The resulting filename is a combination of these values, with a specified ending.

    Parameters:
    ----------
    url : str
        The URL containing query (`q`) and location (`l`) parameters.
    ending : str
        The suffix for the filename. Must be one of the following values:
        - 'links'
        - 'descriptions'
        - 'results'

    Returns:
    -------
    str
        A formatted string representing the filename, with the format: `<query>_<location>_<ending>`.

    Raises:
    ------
    ValueError:
        If the `ending` is not one of the allowed values: 'links', 'descriptions', or 'results'.

    Example:
    --------
    >>> create_results_filename("https://example.com?q=python+developer&l=San+Francisco", 'links')
    'python_developer_san_francisco_links'
    """
    print(url)
    title = url.split('q=')[1].split('&')[0].replace('+', '_').lower()
    area = url.split('l=')[1].split('&')[0].replace('+', '_').lower()
    return f'{title}_{area}_{ending}.csv'


def remove_stopwords(text):
    """
    Removes stopwords from the given text based on the detected language.

    Args:
        text (str): The input text to clean.

    Returns:
        str: The cleaned text without stopwords.
    """
    lang = detect(text)
    stop_words = set()

    if lang == 'en':
        stop_words = set(stopwords.words('english'))
    elif lang == 'nl':
        stop_words = set(stopwords.words('dutch'))
    else:
        print(
            f"Unsupported language detected: {lang}. No stopwords will be removed.")
        return text

    words = word_tokenize(text)
    filtered_text = [word for word in words if word.lower() not in stop_words]
    return ' '.join(filtered_text)
