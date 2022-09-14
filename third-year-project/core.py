from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

driver.get("https://pitchfork.com/reviews/albums/little-simz-sometimes-i-might-be-introvert/")

content = driver.page_source

soup = BeautifulSoup(content, features="html.parser")

content = soup.find_all("div", {"class": "body__inner-container"})

for match in content:

    for paragraph in match:

        print(paragraph.text)