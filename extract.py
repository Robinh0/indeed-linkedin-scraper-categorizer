from bs4 import BeautifulSoup
from generics import setup_driver
from langdetect import detect
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import nltk
import pandas as pd

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Constants
SEARCH_TERM = '"python" -senior -lead -manager'.replace(
    '-', 'N').replace(" ", "").replace('"', '')
STARTING_URL = "https://nl.indeed.com/jobs?q=full+stack+-senior+-lead+-manager&l=Randstad"
AMOUNT_OF_LINKS = 10
OUTPUT_CSV = "results/output_combined.csv"
RESULTS_CSV = f"results/{SEARCH_TERM}_extraction.csv"


def scrape_search_results(driver, url):
    """
    Scrapes job titles and links from the provided Indeed search results URL.

    Args:
        driver: The Selenium WebDriver instance.
        url (str): The URL to scrape.

    Returns:
        pd.DataFrame: A DataFrame containing job titles and URLs.
        str: The first job link found on the page.
    """
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)  # 10 seconds timeout

        # Wait until elements with the class "resultContent" are present
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.CLASS_NAME, "resultContent")))

        data = []
        # Iterate through each element to extract job titles and links
        for element in elements:
            title_span = element.find_element(By.CSS_SELECTOR, "span[title]")
            title_text = title_span.text if title_span else "No title found"
            links = element.find_elements(By.TAG_NAME, "a")

            for link in links:
                href = link.get_attribute("href")
                if href:  # Only store if href is not None
                    print(f'Title: {title_text}, URL: {href}')
                    data.append({"Title": title_text, "URL": href})

        # Create a DataFrame from the data list
        df = pd.DataFrame(data)

        # Export the DataFrame to a CSV file
        # df.to_csv(OUTPUT_CSV, index=False)

        # Return the DataFrame and the first link found
        if not df.empty:
            first_link_on_page = df['URL'].iloc[0]
        else:
            first_link_on_page = None

        return df, first_link_on_page

    except Exception as e:
        print(f"Error while scraping search results: {e}")
        return pd.DataFrame(), None  # Return empty DataFrame and None


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

            # Wait for the title element
            title = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "h1 > span"))).text

            # Wait for the job description elements
            text_elements = wait.until(EC.presence_of_all_elements_located(
                (By.CLASS_NAME, "jobsearch-JobComponent-description")))
            success = True  # If no exception is raised, set success to True

        except TimeoutException:
            print(f"Title not found for URL: {url}. Retrying...")
            driver.quit()  # Quit the current driver instance
            driver = setup_driver()  # Reinitialize the driver
        except WebDriverException as e:
            print(f"WebDriver error for URL: {url}: {e}")
            return None, None  # Return None values if a WebDriver error occurs

    # Extract and clean text
    cleaned_descriptions = [title]
    for element in text_elements:
        html_content = element.get_attribute('innerHTML')
        soup = BeautifulSoup(html_content, "html.parser")
        cleaned_text = soup.get_text(separator=' ', strip=True)
        cleaned_descriptions.append(cleaned_text)

    combined_text = ' '.join(cleaned_descriptions)
    cleaned_text = remove_stopwords(combined_text)

    return title, cleaned_text


def extract():
    """Main function to orchestrate the ETL extract phase."""
    driver = setup_driver()
    try:
        # Step 1: Scrape job links
        df_all = pd.DataFrame()
        # previous_first_link_on_page = None
        counter = 0

        while counter < AMOUNT_OF_LINKS:
            url = f"{STARTING_URL}&start={counter}"
            df_selection, first_link_on_page = scrape_search_results(
                driver, url)

            # if first_link_on_page == previous_first_link_on_page:
            #     print("No new results found. Stopping the scraper.")
            #     break

            df_all = pd.concat([df_all, df_selection], ignore_index=True)
            # df_all.to_csv(OUTPUT_CSV, index=False)

            # previous_first_link_on_page = first_link_on_page
            counter += 10

        # Step 2: Scrape job information from links
        df_all['Title'] = None
        df_all['Description'] = None

        for index, row in df_all.iterrows():
            url = row['URL']
            print(f"Scraping job information from URL: {url}")
            title, cleaned_description = scrape_job_info(driver, url)

            if title and cleaned_description:  # Check if scraping was successful
                print(f"Title: {title}")
                print(f"Description: {cleaned_description}")
                df_all.loc[index, 'Title'] = title
                df_all.loc[index, 'Description'] = cleaned_description
            else:
                print(f"Failed to scrape job information for URL: {url}")

            # Save intermediate results to CSV
            df_all.to_csv(RESULTS_CSV, index=False)

    except Exception as e:
        print(f"An error occurred in the main process: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    extract()
