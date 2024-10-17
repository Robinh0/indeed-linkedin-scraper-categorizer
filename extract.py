import os
from bs4 import BeautifulSoup
from constants import STARTING_URL
from generics import setup_driver, setup_scrape_browser, create_results_filename
from langdetect import detect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import Chrome
import nltk
import pandas as pd
import time

filename = create_results_filename(STARTING_URL)

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Constants
# OUTPUT_CSV = "results/output_combined.csv"
# RESULTS_CSV = f"results/{SEARCH_TERM}_extraction.csv"


def scrape_search_results(driver: Chrome, url_to_scrape):
    """
    Scrapes job titles and links from the provided Indeed search results URL.

    Args:
        driver: The Selenium WebDriver instance.
        url (str): The URL to scrape.

    Returns:
        pd.DataFrame: A DataFrame containing job titles and URLs.
        str: The first job link found on the page.
    """
    driver.get(url_to_scrape)
    continue_loop = True
    cookie_button_clicked = False
    popup_button_clicked = False
    data = []
    while continue_loop:
        wait = WebDriverWait(driver, 5)  # 10 seconds timeout
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class, 'job_seen_beacon')]")))

        if not cookie_button_clicked:
            try:
                cookie_button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//button[@id='onetrust-reject-all-handler']")))
                cookie_button.click()
                cookie_button_clicked = True
                print('Cookie button closed!')
            except:
                print('No cookies found.')
                with open('html_contents', 'w') as file:
                    file.write(driver.page_source)

        if not popup_button_clicked:
            try:
                button = wait.until(EC.presence_of_element_located(
                    (By.XPATH, "//div[@id='mosaic-desktopserpjapopup']//button")))
                button.click()
                popup_button_clicked = True
                print('Popup closed!')
            except:
                print("No popup found.")
                pass

        # Iterate through each element to extract job titles and links
        for element in elements:
            title = element.find_element(
                By.XPATH, ".//h2/a/span").text
            company_name = element.find_element(
                By.XPATH, ".//span[@data-testid='company-name']").text
            location = element.find_element(
                By.XPATH, ".//div[@data-testid='text-location']").text
            link = element.find_element(
                By.XPATH, './/h2/a').get_attribute("href")
            salary = "-"

            try:
                salary_element = element.find_element(
                    By.XPATH, ".//div[contains(@class, 'salary-snippet-container')]")
                salary = salary_element.text if salary_element else "-"
            except:
                pass

            print(
                f"""Title: {title}\n
                URL: {link}\n
                company_name: {company_name}\n
                location: {location}\n
                salary: {salary}\n\n
                """)

            data.append(
                {
                    "title": title,
                    "url": link,
                    "company_name": company_name,
                    "location": location,
                    "salary": salary
                }
            )
        try:
            driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight)")
            next_button = wait.until(EC.presence_of_element_located(
                (By.XPATH, "//nav//li/a[@aria-label='Next Page']")))
            print("Next page button found! Clicking it.")
            next_button.click()
        except:
            print(
                "Next button not found. Setting continue_loop to False and ending the scrape.")
            continue_loop = False
            pass
        continue_loop = False

    df = pd.DataFrame(data)
    df.to_csv(f'results/{filename}_links.csv', index=False)
    return df


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


def scrape_job_info(driver, url):
    """
    Scrapes job title and description from the given job listing URL.

    Args:
        driver: The Selenium WebDriver instance.
        url (str): The URL of the job listing.

    Returns:
        tuple: A tuple containing the job title (str) and the cleaned job description (str).
    """
    success = False
    while not success:
        try:
            driver.get(url)
            wait = WebDriverWait(driver, 10)  # 10 seconds timeout

            # Wait for the job description elements
            text_elements = wait.until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "jobsearch-JobComponent-description")))
            success = True  # If no exception is raised, set success to True

        except TimeoutException:
            print(f"Title not found for URL: {url}. Retrying...")
            driver.quit()  # Quit the current driver instance
            time.sleep(2)
            driver = setup_driver()  # Reinitialize the driver
        except WebDriverException as e:
            print(f"WebDriver error for URL: {url}: {e}")
            return None, None  # Return None values if a WebDriver error occurs

    # Extract and clean text
    cleaned_descriptions = []
    for element in text_elements:
        html_content = element.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, "html.parser")
        cleaned_text = soup.get_text(separator=' ', strip=True)
        cleaned_descriptions.append(cleaned_text)

    combined_text = ' '.join(cleaned_descriptions)
    cleaned_text = remove_stopwords(combined_text)

    return cleaned_text


def extract():
    """Main function to orchestrate the ETL extract phase."""
    # Step 1: Scrape job links
    try:
        driver = setup_driver()
        # driver = setup_scrape_browser()
        df = scrape_search_results(driver, STARTING_URL)
        # Step 2: Scrape job information from links
        df['description'] = None

        for index, row in df.iterrows():
            url = row['url']
            print(f"Scraping job information from title: {row['title']}")
            cleaned_description = scrape_job_info(driver, url)

            if cleaned_description:  # Check if scraping was successful
                print(f"description: {cleaned_description}")
                df.loc[index, 'description'] = cleaned_description
            else:
                print(f"Failed to scrape job information for URL: {url}")

            # Save intermediate results to CSV
            df.to_csv(f'results/{filename}_descriptions.csv', index=False)

    except Exception as e:
        print(
            f"An error occured in the extract process: {e}")
    finally:
        os.remove(f"results/{filename}_links.csv")
        driver.quit()


def extract_scraping_browser():
    with setup_scrape_browser() as driver:
        scrape_search_results(
            driver, STARTING_URL)


if __name__ == "__main__":
    extract()
    # extract_scraping_browser()
