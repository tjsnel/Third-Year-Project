from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from unicodedata import normalize
import pandas as pd


class ReviewScrape():

    def __init__(self, df, platform, body_tag, body_class, score_tag, score_class,
                 header_tag=None, header_class=None):

        self.urls = df.loc[:, f"{platform}_url"]
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

        text = []
        scores = []

        for url in self.urls:

            try:
                self.driver.get(url)
            except:
                print("URL:", url, "has failed.")
                break

            content = self.driver.page_source
            soup = BeautifulSoup(content, features="html.parser")

            if self.header_tag is not None:
                text += [" ".join([self.get_headers(soup), self.get_body(soup)])]
            else:
                text += [self.get_body(soup)]

            scores += self.get_score(soup)

        self.records = pd.DataFrame({"Platform": [self.platform for x in range(len(self.urls))],
                                     "Album": self.albums,
                                     "Artist": self.artists,
                                     "Text": text,
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

        return score

    def format_headers(self, headers):

        return " ".join([header.text for header in headers])

    def format_bodies(self, bodies):

        return " ".join([body.text for body in bodies])

    def format_score(self, score):

        if len(score) > 0:
            score = score[0].text
        else:
            score = -1

        return [score]

    def get_records(self):

        return self.records

    def write_records(self):

        self.records.to_hdf(
            "C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album Data\\review_data.h5",
            key=self.platform,
            mode="a"
            )

    def close_connection(self):

        self.driver.close()


class GenreReviewScrape(ReviewScrape):

    def __init__(self, df, platform, header_tag, header_class, body_tag, body_class, score_tag, score_class, genre_tag,
                 genre_class):
        super().__init__(df=df, platform=platform, header_tag=header_tag, header_class=header_class,
                         body_tag=body_tag, body_class=body_class, score_tag=score_tag,
                         score_class=score_class)

        self.genre_tag = genre_tag
        self.genre_class = genre_class

    def get_data(self):

        text = []
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

            text += [" ".join([self.get_headers(soup), self.get_body(soup)])]
            scores += self.get_score(soup)
            genres += [[", ".join(self.get_genres(soup))]]

        self.records = pd.DataFrame({"Platform": [self.platform for x in range(len(self.urls))],
                                     "Album": self.albums,
                                     "Artist": self.artists,
                                     "Text": text,
                                     "Scores": scores,
                                     "Genres": genres,
                                     "Url": self.urls})

        self.close_connection()

    def get_genres(self, soup):

        genres = soup.find_all(self.genre_tag, self.genre_class)
        genres = self.format_genres(genres)

        return genres

    def format_genres(self, genres):

        if len(genres) == 0:
            genres = ["NA"]

        else:
            genres = [genre.text for genre in genres]

        return genres


class GuardianReviewScrape(GenreReviewScrape):

    def __init__(self, df, platform, header_tag, header_class, body_tag, body_class, score_tag, score_class,
                 genre_tag, genre_class):
        super().__init__(df=df, platform=platform, header_tag=header_tag, header_class=header_class,
                         body_tag=body_tag, body_class=body_class, score_tag=score_tag, score_class=score_class,
                         genre_tag=genre_tag, genre_class=genre_class)

    def format_score(self, score):
        return [5 - len(score)]

    def get_body(self, soup):

        bodies = []

        for tag, body_class in zip(self.body_tag, self.body_class):

            bodies += soup.find_all(tag, body_class)

        bodies = self.format_bodies(bodies)

        return bodies

    def format_bodies(self, bodies):

        try:
            return bodies[0].text + ". " + bodies[1].text + " ".join([body.text for body in bodies[2:]])

        except IndexError:
            return " ".join([body.text for body in bodies])

class PitchforkReviewScrape(GenreReviewScrape):

    def __init__(self, df, platform, header_tag, header_class, body_tag, body_class, score_tag, score_class1,
                 score_class2, genre_tag, genre_class):
        super().__init__(df=df, platform=platform, header_tag=header_tag, header_class=header_class,
                         body_tag=body_tag, body_class=body_class, score_tag=score_tag,
                         score_class=score_class1, genre_tag=genre_tag, genre_class=genre_class)

        self.score_class2 = score_class2

    def get_score(self, soup):
        score = soup.find_all(self.score_tag, self.score_class)

        if len(score) == 0:
            score = soup.find_all(self.score_tag, self.score_class2)

        score = self.format_score(score)

        return score


class NMEReviewScrape(ReviewScrape):

    def __init__(self, df, platform, body_tag, body_class, score_tag, score_class, header_tag, header_class):
        super().__init__(df=df, platform=platform, body_tag=body_tag, body_class=body_class,
                         score_tag=score_tag, score_class=score_class, header_tag=header_tag,
                         header_class=header_class)

    def format_score(self, score):
        return [len(score)]
