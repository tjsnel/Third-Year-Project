from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from unicodedata import normalize
import pandas as pd

class ReviewScrape():

    def __init__(self, df, platform, header_tag, header_class, body_tag, body_class, score_tag, score_class):

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
        self.score_tag = score_tag
        self.score_class = score_class

    def get_data(self):

        content = []
        scores = []

        for url in self.urls:

            try:
                self.driver.get(url)
            except:
                print("URL:", url, "has failed.")
                break

            content = self.driver.page_source
            soup = BeautifulSoup(content, features="html.parser")

            content += [" ".join([self.get_headers(soup), self.get_body(soup)])]
            scores += self.get_score(soup)

        self.records = pd.DataFrame({"Platform": [self.platform for x in range(len(self.urls))],
                                     "Album": self.albums,
                                     "Artist": self.artists,
                                     "Content": content,
                                     "Scores": scores,
                                     "Url": self.urls})

        self.close_connection()

    def get_headers(self, soup):

        headers = soup.find_all(self.header_tag, self.header_class)
        headers = self.format_headers(headers)

        return headers

    def get_body(self, soup):

        bodies = soup.find_all(self.body_tag, self.body_class)
        bodies = self.format_bodies(bodies)

        return bodies

    def get_score(self, soup):

        score = soup.find_all(self.score_tag, self.score_class)
        score = self.format_score(score)

        return [score]

    def format_headers(self, headers):

        return " ".join([header.text for header in headers])

    def format_bodies(self, bodies):

        return " ".join([body.text for body in bodies])

    def format_score(self, score):

        return score[0].text

    def get_records(self):

        return self.records

    def write_records(self):

        self.records.to_csv(
            "C:\\Users\\tommy\\OneDrive\\Third Year Project\\Platform Album Data\\{}Reviews.csv".format(
                self.platform
            ))

    def close_connection(self):

        self.driver.close()


class GenreReviewScrape(ReviewScrape):

    def __init__(self, df, platform, header_tag, header_class, body_tag, body_class, score_tag, score_class, genre_tag,
                 genre_class):
        super().__init__(df, platform, header_tag, header_class, body_tag, body_class, score_tag, score_class)

        self.genre_tag = genre_tag
        self.genre_class = genre_class

    def get_data(self):

        content = []
        scores = []
        genres = []

        for url in self.urls:

            try:
                self.driver.get(url)
            except:
                print("URL:", url, "has failed.")
                break

            content = self.driver.page_source
            soup = BeautifulSoup(content, features="html.parser")

            content += [" ".join([self.get_headers(soup), self.get_body(soup)])]
            scores += self.get_score(soup)
            genres += [", ".join(self.get_genres(soup))]

        self.records = pd.DataFrame({"Platform": [self.platform for x in range(len(self.urls))],
                                     "Album": self.albums,
                                     "Artist": self.artists,
                                     "Content": content,
                                     "Scores": scores,
                                     "Genres": genres,
                                     "Url": self.urls})

        self.close_connection()

    def get_genres(self, soup):

        genres = soup.find_all(self.genre_tag, self.genre_class)
        genres = self.format_genres(genres)

        return genres

    def format_genres(self, genres):

        return [genre.text for genre in genres]


class GuardianReviewScrape(GenreReviewScrape):

    def __init__(self, df, platform, header_tag, header_class, body_tag, body_class, score_tag, score_class,
                 genre_tag, genre_class):
        super().__init__(df, platform, header_tag, header_class, body_tag, body_class, score_tag, score_class,
                         genre_tag, genre_class)

    def format_score(self, score):

        return len(score)

    def format_genres(self, genres):

        urls = []

        for url in genres:

            url = url.find("a").get("href")
            urls.append(url[url.find("music/") + 6:])

        return urls
