from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from unicodedata import normalize
import pandas as pd


class URLScrape:

    def __init__(self, url, album_tag, album_class, artist_tag, artist_class, url_tag, url_class,
                 platform, page_arr=None, extra_urls=None):

        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.url = url
        self.urls = []
        self.platform = platform
        self.page_arr = page_arr
        self.album_tag = album_tag
        self.album_class = album_class
        self.artist_tag = artist_tag
        self.artist_class = artist_class
        self.records = pd.DataFrame()
        self.extra_urls = extra_urls
        self.url_tag = url_tag
        self.url_class = url_class

    def get_page_urls(self):

        if self.page_arr is None:
            self.page_arr = [x for x in range(1, 10001)]

        if self.url is not None:
            for x in self.page_arr:
                self.urls += [self.url.format(x)]

        if self.extra_urls is not None:
            self.urls += [self.extra_urls]

    def get_data(self):

        artists = []
        albums = []
        urls = []

        self.get_page_urls()

        for url in self.urls:

            try:
                self.driver.get(url)
            except:
                print("URL:", url, "has failed.")
                break

            content = self.driver.page_source

            soup = BeautifulSoup(content, features="html.parser")

            albums_soup, artists_soup, urls_soup = self.get_artist_album(soup)

            for i in range(len(artists_soup) - 1, -1, -1):
                if artists_soup[i] == "err":

                    artists_soup.pop(i)
                    albums_soup.pop(i)
                    urls_soup.pop(i)

            artists += artists_soup
            albums += albums_soup
            urls += urls_soup

            if len(artists) <= 1:
                print(f"Page {url} has no data")
                print("Terminating Process...")
                break

        self.records = pd.DataFrame({"Platform": [self.platform for x in range(len(artists))],
                                     "Artist": artists,
                                     "Album": albums,
                                     "Url": urls})

    def get_artist_album(self, soup):

        artists_soup = soup.find_all(self.artist_tag, self.artist_class)
        albums_soup = soup.find_all(self.album_tag, self.album_class)
        url_soup = soup.find_all(self.url_tag, self.url_class)

        artists = self.format_artists(artists_soup)
        albums = self.format_albums(albums_soup)
        urls = self.format_urls(url_soup)

        return artists, albums, urls

    def format_artists(self, soup):

        return [artist.text for artist in soup]

    def format_albums(self, soup):

        return [album.text for album in soup]

    def format_urls(self, soup):

        return [url.find("a").get("href") for url in soup]

    def get_records(self):

        return self.records

    def write_records(self):

        self.records.to_csv(
            "C:\\Users\\tommy\\OneDrive\\Third Year Project\\Platform Album Data\\{}urls.csv".format(
                self.platform
            ))

        self.close_connection()

    def close_connection(self):

        self.driver.close()


class SingleURLScrape(URLScrape):

    def __init__(self, url, album_tag, album_class, url_tag, url_class, platform, page_arr=None, extra_urls=None,
                 sep=None):
        super().__init__(url=url, album_tag=album_tag, album_class=album_class,
                         artist_tag=None, artist_class=None, url_tag=url_tag, url_class=url_class,
                         page_arr=page_arr, extra_urls=extra_urls, platform=platform)

        self.sep = sep

    def get_artist_album(self, soup):

        artist_album_soup = soup.find_all(self.album_tag, self.album_class)
        url_soup = soup.find_all(self.url_tag, self.url_class)

        urls = self.format_urls(url_soup)
        artists, albums = self.format_artist_album(artist_album_soup)

        return artists, albums, urls

    def format_artist_album(self, soup):

        soup = [chunk.a.get_text().split(self.sep, 1) for chunk in soup]

        return self.format_soup(soup)

    def format_soup(self, soup):

        artists = []
        albums = []

        for i in range(len(soup)):
            if len(soup[i]) >= 2:
                artists += [soup[i][0]]
                albums += [soup[i][1]]
            else:
                artists += ["err"]
                albums += ["err"]

        return artists, albums


class NMEURLScrape(SingleURLScrape):

    def __init__(self, url, album_tag, album_class, url_tag, url_class, platform, page_arr, extra_urls=None, sep=None):
        super().__init__(url, album_tag, album_class, url_tag, url_class, platform, page_arr, extra_urls, sep)

    def format_artist_album(self, soup):
        soup = [normalize("NFKD", artist_album.a.get_text(strip=True).replace("'", "")).split(" review")[0].split(" – ", 1)
                for artist_album in soup]

        return self.format_soup(soup)


class GuardianURLScrape(SingleURLScrape):

    def __init__(self, url, album_tag, album_class, url_tag, url_class, platform, page_arr=None, extra_urls=None,
                 sep=None):
        super().__init__(url, album_tag, album_class, url_tag, url_class, platform, page_arr, extra_urls, sep)

    def format_artist_album(self, soup):

        artists_albums_return = []

        for artist_album in soup:

            artist_album = artist_album.a.get_text()
            artist_album = artist_album[artist_album.find("  ") + 1:]
            artist_album = artist_album[: artist_album.find(" review")].strip().split(": ", 1)

            artists_albums_return += [artist_album]

        return self.format_soup(artists_albums_return)

