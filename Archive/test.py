from generics import setup_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup
import pickle
import time
from extract import STARTING_URL


def test_robinbreed_com(driver):
    driver.get('https://robinbreed.com')

    wait = WebDriverWait(driver=driver, timeout=5)

    titles = wait.until(EC.presence_of_all_elements_located((
        By.CSS_SELECTOR, "#c1l5gqutqz > h1 > span > strong")))

    for title in titles:
        print(title.text)

    link = wait.until(EC.presence_of_element_located((
        By.CSS_SELECTOR, "#cls3ehrod > a"))).get_attribute('href')

    driver.get(link)

    header = wait.until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, "#cls3cxz8p > h1")))

    print(header.text)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    all_text = soup.get_text(separator='\n')
    print(all_text)

    # time.sleep(120)


def test_website_text(driver, url):
    driver.get(url)

    # Get the HTML content of the page
    page_content = driver.page_source

    # Parse with BeautifulSoup
    product_soup = BeautifulSoup(page_content, 'html.parser')

    # Extract and print all text from the webpage
    # Extract all text, separated by newlines
    all_text = product_soup.get_text(separator='\n')
    print(all_text)

    # Optionally, you can write the text to a file
    with open('text_content.txt', 'w', encoding='utf-8') as text_file:
        text_file.write(all_text)

    time.sleep(100)
    return


def save_cookies(driver, url):
    test_website_text(driver, url)
    cookies = driver.get_cookies()
    pickle.dump(cookies, open("cookies.pkl", "wb"))
    driver.quit()


def load_cookies(driver, url):
    cookies = pickle.load(open("cookies.pkl", "rb"))

    for cookie in cookies:
        cookie['domain'] = f".indeed.com"

        try:
            driver.add_cookie(cookie)
        except Exception as e:
            print(e)

    test_website_text(driver, url)
    driver.quit()


robinbreed = "https://robinbreed.com"
pixelscan = "https://pixelscan.net/"


driver = setup_driver()

# save_cookies(driver, STARTING_URL)
# load_cookies(driver, STARTING_URL)

# test_robinbreed_com(driver)
test_website_text(driver, pixelscan)
