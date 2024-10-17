from requests_html import HTMLSession
from extract import STARTING_URL  # STARTING_URL should be a valid URL
from bs4 import BeautifulSoup

# Create an HTML session
session = HTMLSession()

# Send a GET request to the URL
response = session.get(STARTING_URL)

# Render JavaScript (optional, only if the page requires it)
response.html.render()

# Parse the HTML content with BeautifulSoup
soup = BeautifulSoup(response.html.html, 'html.parser')

# Extract and print all the text content of the page
print(soup.get_text())
