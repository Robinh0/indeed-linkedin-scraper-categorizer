from langdetect import detect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from random import randint
from selenium.webdriver import Remote, ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.remote_connection import ChromiumRemoteConnection
from webdriver_manager.chrome import ChromeDriverManager
import os
import time
import platform

# Download NLTK resources
# nltk.download('punkt')
# nltk.download('stopwords')
# nltk.download('punkt_tab')


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


def sleep_random(max_sleep_in_ms: int):
    time_to_sleep = randint(100, max_sleep_in_ms) / 1000
    time.sleep(time_to_sleep)
    return
