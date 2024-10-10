from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd

DRIVER_PATH = "C:/Users/robin/Documents/App files/chromedriver-win64/chromedriver-win64/chromedriver.exe"

chrome_options = Options()

service = Service(DRIVER_PATH)
driver = webdriver.Chrome(service=service, options=chrome_options)

# starting_url = """
# https://nl.indeed.com/jobs?q=%22python%22+-senior+-lead+-manager&l=Randstad&vjk=af544b12289183ad
# """
starting_url = """
https://nl.indeed.com/jobs?q=full+stack+-senior+-lead+-manager&l=Randstad&vjk=5545059d83bddb71
"""

AMOUNT_OF_LINKS = 150

data = []
previous_first_link_on_page = None


def scrape_search_results(url):
    # Navigate to the Indeed jobs page
    driver.get(url)

    # # Find all elements with the class 'resultContent'
    # elements = driver.find_elements(By.CLASS_NAME, "resultContent")

    # Set up an explicit wait
    wait = WebDriverWait(driver, 10)  # 10 seconds timeout

    # Wait until elements with the class "resultContent" are present
    elements = wait.until(EC.presence_of_all_elements_located(
        (By.CLASS_NAME, "resultContent")))

    # Iterate through each element
    for element in elements:
        # Find the <span> with the title attribute
        title_span = element.find_element(By.CSS_SELECTOR, "span[title]")
        # Get the text if the span exists
        title_text = title_span.text if title_span else "No title found"

        # Find all <a> tags within the current element
        links = element.find_elements(By.TAG_NAME, "a")
        for link in links:
            href = link.get_attribute("href")  # Get the href attribute
            if href:  # Print only if href is not None
                print(f'Title: {title_text}, URL: {href}')
                data.append({"Title": title_text, "URL": href})

    # Create a DataFrame from the data list
    df = pd.DataFrame(data)

    # Export the DataFrame to a CSV file
    # Saves to output.csv in the current directory
    df.to_csv(f"output.csv", index=False)
    first_link_on_page = df['URL'][1]
    print(first_link_on_page)
    return df, first_link_on_page


df_all, first_link_on_page = scrape_search_results(
    starting_url)
previous_first_link_on_page = first_link_on_page
continue_scrape = True
counter = 10
while continue_scrape:
    url = f"{starting_url}&start={counter}"
    df_selection, first_link_on_page = scrape_search_results(
        url)

    if (counter == AMOUNT_OF_LINKS):
        continue_scrape = False
    counter = counter + 10
    print(df_selection)
    print(f"Length df: {len(df_selection)}")

    df_all = pd.concat([df_selection, df_all])
    df_all.to_csv(f"output_combined.csv", index=False)

# time.sleep(1000)
driver.quit()
