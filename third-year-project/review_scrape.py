from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from unicodedata import normalize
import pandas as pd

class ReviewScrape():

    def __init__(self, df, platform, header_tag, header_class, body_tag, body_class):

        self.urls = df.loc[:, "Url"]
        self.artists = df.loc[:, "Artist"]
        self.albums = df.loc[:, "Album"]
        self.header_tag = header_tag
        self.header_class = header_class
        self.body_tag = body_tag
        self.body_class = body_class
        self.platform = platform
        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.records = pd.DataFrame()

    def get_data(self):

        content = []

        for url in self.urls:

            try:
                self.driver.get(url)
            except:
                print("URL:", url, "has failed.")
                break

            content = self.driver.page_source
            soup = BeautifulSoup(content, features="html.parser")

            content += " ".join([self.get_headers(soup), self.get_body(soup)])

        self.records = pd.DataFrame({"Platform": [self.platform for x in range(len(self.urls))],
                                     "Album": self.albums,
                                     "Artist": self.artists,
                                     "Content": content,
                                     "Url": self.urls})

    def get_headers(self, soup):

        headers = soup.find_all(self.header_tag, self.header_class)
        headers = self.format_headers(headers)

        return headers

    def get_body(self, soup):

        bodies = soup.find_all()
        bodies = self.format_bodies(bodies)

        return bodies

    def format_headers(self, headers):

        return " ".join([header.text for header in headers])

    def format_bodies(self, bodies):

        return " ".join([body.text for body in bodies])

    def get_records(self):

        return self.records

    def write_records(self):

        self.records.to_csv(
            "C:\\Users\\tommy\\OneDrive\\Third Year Project\\Platform Album Data\\{}reviews.csv".format(
                self.platform
            ))

        self.close_connection()

    def close_connection(self):

        self.driver.close()