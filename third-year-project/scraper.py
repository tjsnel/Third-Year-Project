from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup


class Scraper:

    def __init__(self, url, score_tag="", score_class="", content_tag="", content_class="", excerpt_tag="",
                 excerpt_class=""):

        self.url = url
        self.score_tag = score_tag
        self.score_class = score_class
        self.content_tag = content_tag
        self.content_class = content_class
        self.excerpt_tag = excerpt_tag
        self.excerpt_class = excerpt_class
        self.soup = self.cook_soup()

    def cook_soup(self):

        service = Service(executable_path=ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service)
        driver.get(self.url)
        content = driver.page_source
        soup = BeautifulSoup(content, features="html.parser")

        return soup

    def get_all(self):

        try:
            paragraphs = [paragraph.text for match in self.get_content() for paragraph in match]
        except AttributeError:
            print("Paragraphs not found")

        try:
            excerpt = self.get_excerpt().text
        except AttributeError:
            print("Excerpt not found")

        try:
            score = self.get_score().text
        except AttributeError:
            print("Score not found")

    def get_score(self):

        return self.soup.find(self.score_tag, self.score_class)

    def get_content(self):

        return self.soup.find_all(self.content_tag, self.content_class)

    def get_excerpt(self):

        return self.soup.find(self.excerpt_tag, self.excerpt_class)
