import time
import os
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from generics.generics import sleep_random
from .driver_manager import DriverManager
from selenium.webdriver.chrome.webdriver import WebDriver
from undetected_chromedriver import Chrome
from linkedin.scrape_linkedin import get_linkedin_descriptions


class Extractor:
    def __init__(self):
        self.max_pages_to_scrape = int(os.getenv("MAX_PAGES_TO_SCRAPE"))
        self.items_per_page = int(os.getenv('NR_ITEMS_PER_PAGE'))
        self.url = os.environ['URL']
        self.current_url = None
        self.driver_manager: Chrome = DriverManager()

        # Initial state for scraping loop
        self.continue_loop = True
        self.cookie_button_clicked = False
        self.popup_button_clicked = False
        self.data = []
        self.data_final = []
        self.counter = 0


class IndeedExtractor(Extractor):
    def _close_cookies(self):
        """Closes the cookie consent pop-up if present."""
        short_wait = WebDriverWait(self.driver_manager.driver, 2)
        try:
            cookie_button = short_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//button[@id='onetrust-reject-all-handler']")))
            cookie_button.click()
            print('Cookie button closed!')
            return True
        except:
            print('No cookies found.')
            return False

    def _close_popup(self):
        """Closes a pop-up window if present."""
        short_wait = WebDriverWait(self.driver_manager.driver, 2)
        try:
            button = short_wait.until(EC.presence_of_element_located(
                (By.XPATH, "//div[@id='mosaic-desktopserpjapopup']//button")))
            button.click()
            print('Popup closed!')
            return True
        except:
            print("No popup found.")
            return False

    def _click_next_button(self):
        """Clicks the 'Next' button to navigate to the next page."""
        wait = WebDriverWait(self.driver_manager.driver, 5)
        self.driver_manager.driver.execute_script(
            "window.scrollTo(0, document.body.scrollHeight)")
        next_button = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//nav//li/a[@aria-label='Next Page']")))
        print("Next page button found! Clicking it.")
        next_button.click()

    def _get_description(self, job_id):
        wait = WebDriverWait(self.driver_manager.driver, 5)
        self.driver_manager.driver.get(f"{self.url}&vjk={job_id}")
        description = wait.until(EC.presence_of_element_located(
            (By.XPATH, ".//div[@id='jobDescriptionText']")))
        description_text = description.text
        description_html_content = description.get_attribute('innerHTML')
        return description_text, description_html_content

    def _scrape_page(self):
        """Scrapes job listings from the current page."""
        wait = WebDriverWait(self.driver_manager.driver, 5)
        elements = wait.until(EC.presence_of_all_elements_located(
            (By.XPATH, "//div[contains(@class, 'job_seen_beacon')]")))

        if not self.cookie_button_clicked:
            self.cookie_button_clicked = self._close_cookies()

        if not self.popup_button_clicked:
            self.popup_button_clicked = self._close_popup()

        # Loop to iterate over the elements and extract the job information.
        for element_counter, element in enumerate(elements):
            try:
                if element_counter >= self.items_per_page:
                    break

                self.driver_manager.driver.execute_script(
                    "arguments[0].scrollIntoView();", element)

                job_id = element.find_element(
                    By.XPATH, ".//a[(starts-with(@id, 'sj_') or starts-with(@id, 'job_'))]"
                ).get_attribute('id').split("_")[-1]

                print(f"Job id: {job_id}")
                print(f"Scraping element nr {element_counter}")
                sleep_random(200)

                wait = WebDriverWait(self.driver_manager.driver, 5)

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
                    f"title: {title}\ncompany_name: {company_name}\nlocation: {location}\n")
                self.data.append({
                    'job_id': job_id,
                    'data': {
                        "title": title,
                        "url": link,
                        "company_name": company_name,
                        "location": location,
                        "salary": salary,
                        "description": "",
                        "html_content": "",
                    }
                }
                )
            except:
                continue
        # Loop to visit each unique url and scrape the description.
        for element in self.data:
            try:
                job_id = element.get('job_id')
                description_text, description_html_content = self._get_description(
                    job_id=job_id)
                element['data']['description'] = description_text
                element['data']['html_content'] = description_html_content
            except:
                continue

    def run_scraper(self):
        """Runs the main scraping loop until all pages are processed."""
        self.driver_manager.driver.get(self.url)

        while self.continue_loop:
            self.current_url = self.driver_manager.driver.current_url
            self._scrape_page()

            if self.counter < self.max_pages_to_scrape - 1:
                print("Clicking the next button and scraping another page.")
                try:
                    self._click_next_button()
                    self.counter += 1
                except:
                    self.continue_loop = False
            else:
                print("All pages scraped. Ending the loop.")
                self.continue_loop = False

        dict_for_df = [
            {
                "job_id": job["job_id"],
                **job["data"]
            }
            for job in self.data
        ]
        df = pd.DataFrame(dict_for_df)
        return df


class LinkedInExtractor(Extractor):
    # def __init__(self):
    #     super().__init__()
    #     self.cookies = {
    #         "JSESSIONID": os.getenv('JSESSIONID'),
    #         "li_at": os.getenv('li_at')
    #     }

    def run_scraper(self):
        # Getting the url and adding cookies
        # cookies = {
        #     "JSESSIONID": os.getenv('JSESSIONID'),
        #     "li_at": os.getenv('LI_AT')
        # }
        # self.driver_manager.driver.get(self.url)
        # time.sleep(5)
        # self.driver_manager.add_cookies(cookies)
        # self.driver_manager.driver.get(self.url)
        # self.driver_manager.driver.manage().add_cookie(self.cookies)
        return get_linkedin_descriptions()
