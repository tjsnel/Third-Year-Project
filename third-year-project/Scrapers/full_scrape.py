from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from unicodedata import normalize
import pandas as pd


class FullScrape():

    def __init__(self, df, platform, score_tag, score_class, base_url):

        self.urls = base_url + df.loc[:, "Url"]
        self.artists = df.loc[:, "Artist"]
        self.albums = df.loc[:, "Album"]
        self.platform = platform
        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.records = pd.DataFrame()
        self.score_tag = score_tag
        self.score_class = score_class

    def get_data(self):

        scores = []

        for url in self.urls:

            try:
                self.driver.get(url)
            except:
                print("URL:", url, "has failed.")
                break

            content = self.driver.page_source
            soup = BeautifulSoup(content, features="html.parser")

            scores += self.get_score(soup)

        self.records = pd.DataFrame({"Platform": [self.platform for x in range(len(self.urls))],
                                     "Album": self.albums,
                                     "Artist": self.artists,
                                     "Scores": scores,
                                     "Url": self.urls})

        self.close_connection()

    def get_score(self, soup):

        score = soup.find_all(self.score_tag, self.score_class)
        score = self.format_score(score)

        return score

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
            "C:\\Users\\tommy\\OneDrive\\University\\Year 3\\Third Year Project\\Platform Album Data\\entire_data.h5",
            key=self.platform,
            mode="a"
            )

    def close_connection(self):

        self.driver.close()


class GenreFullScrape(FullScrape):

    def __init__(self, df, platform, score_tag, score_class, base_url, genre_tag,
                 genre_class):
        super().__init__(df=df, platform=platform, score_tag=score_tag,
                         score_class=score_class, base_url=base_url)

        self.genre_tag = genre_tag
        self.genre_class = genre_class

    def get_data(self):

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

            scores += self.get_score(soup)
            genres += [[", ".join(self.get_genres(soup))]]

        self.records = pd.DataFrame({"Platform": [self.platform for x in range(len(self.urls))],
                                     "Album": self.albums,
                                     "Artist": self.artists,
                                     "Scores": scores,
                                     "Genres": genres,
                                     "Url": self.urls})

        self.close_connection()

    def get_genres(self, soup):

        genres = []

        for genre_tag in self.genre_tag:
            unformatted_genres = soup.find_all(genre_tag, self.genre_class)
            genres += self.format_genres(unformatted_genres)

        return genres

    def format_genres(self, genres):

        if len(genres) == 0:

            genres = ["NA"]

        else:

            genres = [genre.text for genre in genres]

        return genres


class GuardianFullScrape(GenreFullScrape):

    def __init__(self, df, platform, score_tag, score_class, base_url,
                 genre_tag, genre_class):
        super().__init__(df=df, platform=platform, score_tag=score_tag, score_class=score_class,
                         genre_tag=genre_tag, genre_class=genre_class, base_url=base_url)

    def format_score(self, score):
        return [5 - len(score)]

    def format_genres(self, genres):
        urls = []

        for url in genres:
            url = url.find("a").get("href")
            urls.append(url[url.find("music/") + 6:])

        return urls


class PitchforkFullScrape(GenreFullScrape):

    def __init__(self, df, platform, score_tag, score_class1, base_url,
                 score_class2, genre_tag, genre_class):
        super().__init__(df=df, platform=platform, score_tag=score_tag, base_url=base_url,
                         score_class=score_class1, genre_tag=genre_tag, genre_class=genre_class)

        self.score_class2 = score_class2

    def get_score(self, soup):
        score = soup.find_all(self.score_tag, self.score_class)

        if len(score) == 0:
            score = soup.find_all(self.score_tag, self.score_class2)

        score = self.format_score(score)

        return score


class NMEFullScrape(FullScrape):

    def __init__(self, df, platform, score_tag, score_class, base_url):
        super().__init__(df=df, platform=platform, score_tag=score_tag, score_class=score_class, base_url=base_url)

    def format_score(self, score):
        return [len(score)]