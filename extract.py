from generics import setup_scrape_browser, sleep_random
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import os
import pandas as pd
import platform

if platform.system() == "Windows":
    from generics import setup_driver
    from undetected_chromedriver import Chrome


def scrape_search_results(url, driver):
    """
    Scrapes job titles and links from the provided Indeed search results URL.

    Args:
        driver: The Selenium WebDriver instance.
        url (str): The URL to scrape.

    Returns:
        pd.DataFrame: A DataFrame containing job titles and URLs.
        str: The first job link found on the page.
    """
    def close_cookies(driver):
        short_wait = WebDriverWait(driver, 2)
        try:
            cookie_button = short_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[@id='onetrust-reject-all-handler']")))
            cookie_button.click()
            # cookie_button_clicked = True
            print('Cookie button closed!')
            return True
        except:
            print('No cookies found.')
            return False

    def close_popup(driver):
        short_wait = WebDriverWait(driver, 2)
        try:
            button = short_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@id='mosaic-desktopserpjapopup']//button")))
            button.click()
            print('Popup closed!')
            return True
        except:
            print("No popup found.")
            return False

    def click_next_button():
        driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight)")
        next_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//nav//li/a[@aria-label='Next Page']")))
        print("Next page button found! Clicking it.")
        next_button.click()

    def reset_driver(driver, url_to_scrape):
        print("Resetting the driver")
        driver.quit()
        driver = setup_driver()
        driver.get(url=url_to_scrape)
        close_popup(driver)
        close_cookies(driver)
        print("Driver reset")
        return driver

    # sleep_random(200)
    continue_loop = True
    cookie_button_clicked = False
    popup_button_clicked = False
    data = []
    counter = 0
    max_pages_to_scrape = int(os.getenv("MAX_PAGES_TO_SCRAPE"))
    nr_items_per_page = int(os.getenv('NR_ITEMS_PER_PAGE'))
    url_to_scrape = url
    driver.get(url_to_scrape)
    while continue_loop:
        url_to_scrape = driver.current_url
        wait = WebDriverWait(driver, 5)  # 10 seconds timeout
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class, 'job_seen_beacon')]")))

        if not cookie_button_clicked:
            cookie_button_clicked = close_cookies(driver)

        if not popup_button_clicked:
            popup_button_clicked = close_popup(driver)

        # Iterate through each element to extract job titles and links
        element_counter = 0
        try:
            for element in elements:
                print(f"Scraping element nr {element_counter}")
                sleep_random(200)
                # try:
                driver.execute_script(
                    "arguments[0].scrollIntoView();", element)
                sleep_random(200)
                title_link = element.find_element(By.XPATH, ".//h2/a")
                title_link.click()
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
                description_html_content = description.get_attribute(
                    'innerHTML')

                # Extracting the salary if noted on page.
                salary = "-"
                try:
                    salary_element = element.find_element(
                        By.XPATH, ".//div[contains(@class, 'salary-snippet-container')]")
                    salary = salary_element.text if salary_element else "-"
                except:
                    pass

                print(
                    f"title: {title}\ncompany_name: {company_name}\nlocation: {location}\n")

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
                if element_counter >= nr_items_per_page-1:
                    break
                else:
                    element_counter += 1
        except:
            driver = reset_driver(driver, url_to_scrape)
            continue

        # if not cookie_button_clicked:
        #     cookie_button_clicked = close_cookies(driver)

        if counter < max_pages_to_scrape-1:
            print("Clicking the next button and scraping another page.")
            try:
                click_next_button()
                counter += 1
            except:
                continue_loop = False
        else:
            print("All pages scaped. continue_loop is set to false.")
            continue_loop = False
    df = pd.DataFrame(data)
    # df.to_csv(f"results/{get_filename('descriptions')}", index=False)
    return df


def extract():
    """Main function to orchestrate the ETL extract phase."""
    try:
        url = str(os.getenv('INDEED_URL'))
        if platform.system() == "Windows":
            driver = setup_driver()
        else:
            driver = setup_scrape_browser()
        df = scrape_search_results(url, driver)
    except Exception as e:
        print(
            f"An error occured in the extract process: {e}")
    finally:
        # os.remove(f"results/{get_filename('links')}")
        driver.quit()
    return df
