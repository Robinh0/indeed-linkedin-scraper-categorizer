import os
from bs4 import BeautifulSoup
from constants import STARTING_URL
from generics import setup_driver, get_filename, setup_scrape_browser, sleep_random
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import Chrome
import pandas as pd
import time
import boto3
from datetime import datetime


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
            driver.execute_script("arguments[0].scrollIntoView();", element)
            title_link = element.find_element(By.XPATH, ".//h2/a")
            title_link.click()
            sleep_random(200)
            title = element.find_element(By.XPATH, ".//h2/a/span").text
            company_name = element.find_element(
                By.XPATH, ".//span[@data-testid='company-name']").text
            location = element.find_element(
                By.XPATH, ".//div[@data-testid='text-location']").text
            link = element.find_element(
                By.XPATH, './/h2/a').get_attribute("href")
            description = wait.until(EC.presence_of_element_located(
                (By.XPATH, ".//div[@id='jobDescriptionText']")))
            description_text = description.text
            description_html_content = description.get_attribute('innerHTML')

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
                description: {description_text}\n\n
                description_html_content: {description_html_content}\n\n
                """)

            data.append(
                {
                    "title": title,
                    "url": link,
                    "company_name": company_name,
                    "location": location,
                    "salary": salary,
                    "description": description_text,
                    "html_content": description_html_content,
                }
            )
        try:
            # Only scraping the first page for this demo.
            pass
            # driver.execute_script(
            #     "window.scrollTo(0, document.body.scrollHeight)")
            # next_button = wait.until(EC.presence_of_element_located(
            #     (By.XPATH, "//nav//li/a[@aria-label='Next Page']")))
            # print("Next page button found! Clicking it.")
            # next_button.click()
        except:
            print(
                "Next button not found. Setting continue_loop to False and ending the scrape.")
            continue_loop = False
            pass
        continue_loop = False

    df = pd.DataFrame(data)
    df.to_csv(f"results/{get_filename('descriptions')}", index=False)
    return df


def extract():
    s3_client = boto3.client('s3')
    """Main function to orchestrate the ETL extract phase."""
    try:
        # driver = setup_driver()
        driver = setup_scrape_browser()
        scrape_search_results(driver, STARTING_URL)

        local_file = f"results/{get_filename('descriptions')}"
        bucket_name = 'indeed-scraper-2'
        s3_file_name = f"test"
        s3_client.upload_file(local_file, bucket_name, s3_file_name)
    except Exception as e:
        print(
            f"An error occured in the extract process: {e}")
    finally:
        # os.remove(f"results/{get_filename('links')}")
        driver.quit()


if __name__ == "__main__":
    extract()
