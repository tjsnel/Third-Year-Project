import re

from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd


def pitchfork_scraper(url):

    service = Service(executable_path=ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service)

    driver.get(url)

    content = driver.page_source

    soup = BeautifulSoup(content, features="html.parser")

    content = soup.find_all("div", {"class": "body__inner-container"})

    review_paragraphs = []

    for match in content:

        for paragraph in match:

            review_paragraphs.append(paragraph.text)

    score = soup.find("div", {"class": re.compile("ScoreCircle-cIQIJH.*")})
    try:
        score = score.text
    except:
        print("Score not found")

    excerpt = soup.find("div", {"class": re.compile("BaseWrap-sc-UABmB BaseText-fETRLB SplitScreenContentHeaderDekDown"
                                                    "-fkdeqx hkSZSE FFNqX hrWveo")})
    excerpt = excerpt.text

    print(review_paragraphs, score, excerpt)


pitchfork_scraper("https://pitchfork.com/reviews/albums/20390-to-pimp-a-butterfly/")

# "https://pitchfork.com/reviews/albums/little-simz-sometimes-i-might-be-introvert/"
