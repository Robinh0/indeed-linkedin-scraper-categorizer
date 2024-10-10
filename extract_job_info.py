from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from bs4 import BeautifulSoup
from langdetect import detect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk
from selenium.common.exceptions import TimeoutException  # Import TimeoutException


nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')


def remove_stopwords(text):
    # Detect the language
    lang = detect(text)

    # Choose stopwords based on detected language
    if lang == 'en':
        stop_words = set(stopwords.words('english'))
    elif lang == 'nl':
        stop_words = set(stopwords.words('dutch'))
    else:
        print(
            f"Unsupported language detected: {lang}. No stopwords will be removed.")
        return text  # Return original text if language is not supported

    # Tokenize the text
    words = word_tokenize(text)

    # Remove stopwords
    filtered_text = [word for word in words if word.lower()
                     not in stop_words]

    # Join the filtered words back into a string
    cleaned_text = ' '.join(filtered_text)

    return cleaned_text


DRIVER_PATH = "C:/Users/robin/Documents/App files/chromedriver-win64/chromedriver-win64/chromedriver.exe"

chrome_options = Options()

service = Service(DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# df = pd.read_csv('df_with_description.csv')
df = pd.read_csv('output_combined.csv')
df.drop_duplicates(inplace=True)
df['Description'] = None

print(df)

for index, row in df.iterrows():
    url = df.loc[index, 'URL']
    print(url)

    driver.get(url)

    # # Find all elements with the class 'resultContent'
    # elements = driver.find_elements(By.CLASS_NAME, "resultContent")

    # Set up an explicit wait

    # Wait until elements with the class "resultContent" are present
    success = False  # Flag to keep track of whether the current index passes
    while not success:
        try:
            wait = WebDriverWait(driver, 2)  # 10 seconds timeout
            driver.get(url)

            # Set up an explicit wait
            wait = WebDriverWait(driver, 2)  # 2 seconds timeout

            # Wait for the title element
            title = wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, "h1 > span")))[0].text

            # Wait for the job description elements
            text_elements = wait.until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "jobsearch-JobComponent-description")))

            success = True  # If no exception is raised, set success to True
        except TimeoutException:
            driver.quit()
            print(f"Title not found for URL: {url}")
            # time.sleep(5)
            driver = webdriver.Chrome(service=service, options=chrome_options)
            # continue  # Skip to the next URL if the title is not found

    # Extract and clean text
    cleaned_descriptions = []
    cleaned_descriptions.append(title)
    for element in text_elements:
        # Get the HTML content
        html_content = element.get_attribute('innerHTML')

        # Use BeautifulSoup to clean the HTML
        soup = BeautifulSoup(html_content, "html.parser")
        # Clean and format the text
        cleaned_text = soup.get_text(separator=' ', strip=True)

        cleaned_descriptions.append(cleaned_text)

    # Combine the list into a single string
    combined_text = ' '.join(cleaned_descriptions)
    cleaned_text = remove_stopwords(text=combined_text)

    print(f"Title: {title}")
    print(f"Description: {cleaned_text}")
    df.loc[index, 'Title'] = title
    df.loc[index, 'Description'] = cleaned_text
    df.to_csv("df_with_description.csv")
