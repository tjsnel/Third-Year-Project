from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from unicodedata import normalize
import pandas as pd


class AlbumScrape:

    def __init__(self, url, album_tag, album_class, artist_tag, artist_class, platform, page_arr=None, extra_urls=None):

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
        self.artists = []
        self.albums = []

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

        self.get_page_urls()

        for url in self.urls:

            try:
                self.driver.get(url)
            except:
                print("URL:", url, "has failed.")
                break

            content = self.driver.page_source

            soup = BeautifulSoup(content, features="html.parser")

            albums_soup, artists_soup = self.get_artist_album(soup)

            artists += artists_soup
            albums += albums_soup

            if len(artists) == 0:

                break

        self.records = pd.DataFrame({"Platform": [self.platform for x in range(len(artists))],
                                     "Artist": artists,
                                     "Album": albums})

    def get_artist_album(self, soup):

        artists_soup = soup.find_all(self.artist_tag, self.artist_class)
        albums_soup = soup.find_all(self.album_tag, self.album_class)

        return [album.text for album in albums_soup], [artist.text for artist in artists_soup]

    def get_records(self):

        return self.records

    def write_records(self):

        self.records.to_csv(
            "C:\\Users\\tommy\\OneDrive\\Third Year Project\\Platform Album Data\\{}.csv".format(
                self.platform
            ))

        self.close_connection()

    def close_connection(self):

        self.driver.close()


class SingleClassAlbumScrape(AlbumScrape):

    def __init__(self, url, album_tag, album_class, platform, page_arr=None, extra_urls=None, sep=None):
        super().__init__(url, album_tag, album_class, platform=platform, artist_tag=None, artist_class=None,
                         page_arr=page_arr, extra_urls=extra_urls)

        self.sep = sep

    def get_artist_album(self, soup):

        artists_albums_soup = soup.find_all(self.album_tag, self.album_class)
        artists_albums_soup = [artist_album.a.get_text().split(self.sep, 1) for artist_album in
                               artists_albums_soup]

        return self.format_soups(artists_albums_soup)

    def format_soups(self, artists_albums_soup):

        artist_soup = []
        album_soup = []

        for i in range(0, len(artists_albums_soup)):
            if len(artists_albums_soup[i]) >= 2:

                artist_soup += [artists_albums_soup[i][0]]
                album_soup += [artists_albums_soup[i][1]]

        return album_soup, artist_soup

class LAQAlbumScrape(SingleClassAlbumScrape):

    def __init__(self, url, album_tag, album_class, platform, page_arr=None, extra_urls=None):
        super().__init__(url=url, album_tag=album_tag, album_class=album_class,
                         page_arr=page_arr, extra_urls=extra_urls, platform=platform)

    def get_artist_album(self, soup):
        artists_albums_soup = soup.find_all(self.album_tag, self.album_class)
        artists_albums_soup = [artist_album.get_text(strip=True, separator='\n').splitlines() for artist_album in
                               artists_albums_soup]

        return self.format_soups(artists_albums_soup)


class SkinnyAlbumScrape(SingleClassAlbumScrape):

    def __init__(self, url, album_tag, album_class, platform, page_arr=None, extra_urls=None):
        super().__init__(url=url, album_tag=album_tag, album_class=album_class, page_arr=page_arr,
                         extra_urls=extra_urls, platform=platform)

    def get_artist_album(self, soup):
        artists_albums_soup = soup.find_all(self.album_tag, self.album_class)
        artists_albums_soup = [artist_album.text.strip().split(" – ", 1) for artist_album in artists_albums_soup]

        return self.format_soups(artists_albums_soup)


class NMEAlbumScrape(SingleClassAlbumScrape):

    def __init__(self, url, album_tag, album_class, platform, page_arr=None, extra_urls=None):
        super().__init__(url=url, album_tag=album_tag, album_class=album_class, page_arr=page_arr,
                         extra_urls=extra_urls, platform=platform)

    def get_artist_album(self, soup):
        artists_albums_soup = soup.find_all(self.album_tag, self.album_class)
        artists_albums_soup = [normalize("NFKD", artist_album.a.get_text(strip=True)).split(" review")[0].split(" – ", 1)
                               for artist_album in artists_albums_soup]

        album_soup = []
        artist_soup = []

        for i in range(len(artists_albums_soup)):
            if len(artists_albums_soup[i]) >= 2:
                album_soup += [artists_albums_soup[i][1].replace("'", "")]
                artist_soup += [artists_albums_soup[i][0]]

        return album_soup, artist_soup


class OHMAlbumScrape(AlbumScrape):

    def __init__(self, url, header_tag, header_class, main_tag, main_class, platform, page_arr=None,
                 extra_urls=None):
        super().__init__(url, album_tag=None, album_class=None, artist_tag=None,
                         artist_class=None, page_arr=page_arr, extra_urls=extra_urls, platform=platform)

        self.header_tag = header_tag
        self.header_class = header_class
        self.main_tag = main_tag
        self.main_class = main_class

    def get_artist_album(self, soup):

        headers_soup = soup.find_all(self.header_tag, self.header_class)
        main_soup = soup.find_all(self.main_tag, self.main_class)
        headers_soup = [normalize("NFKD", artist_album.a.get_text(strip=True)).split(" – ", 1)
                        for artist_album in headers_soup]
        main_soup = [normalize("NFKD", artist_album.h5.a.get_text(strip=True)).split(" – ", 1)
                     for artist_album in main_soup]

        artist_soup = []
        album_soup = []

        for i in range(len(main_soup)):
            if len(main_soup[i]) >= 2:
                album_soup += [main_soup[i][1]]
                artist_soup += [main_soup[i][0]]

        for i in range(len(headers_soup)):
            if len(headers_soup[i]) >= 2:
                album_soup += [headers_soup[i][1]]
                artist_soup += [headers_soup[i][0]]

        return album_soup, artist_soup


class GuardianAlbumScrape(SingleClassAlbumScrape):

    def __init__(self, url, album_tag, album_class, platform, page_arr=None, extra_urls=None):
        super().__init__(url=url, album_tag=album_tag, album_class=album_class, page_arr=page_arr,
                         extra_urls=extra_urls, platform=platform)

    def get_artist_album(self, soup):

        artists_albums_soup = soup.find_all(self.album_tag, self.album_class)
        artists_albums_return = []

        for artist_album in artists_albums_soup:

            artist_album = artist_album.a.get_text()
            artist_album = artist_album[artist_album.find("  ") + 1:]
            artist_album = artist_album[: artist_album.find(" review")].strip().split(": ", 1)

            artists_albums_return += [artist_album]

        return self.format_soups(artists_albums_return)


class GigwiseAlbumScrape(SingleClassAlbumScrape):

    def __init__(self, url, album_tag, album_class, platform, page_arr=None, extra_urls=None, sep=None):
        super().__init__(url=url, album_tag=album_tag, album_class=album_class,
                         page_arr=page_arr, extra_urls=extra_urls, sep=sep, platform=platform)

    def get_artist_album(self, soup):

        artists_albums_soup = soup.find_all(self.album_tag, self.album_class)
        artists_albums_return = []

        for artist_album in artists_albums_soup:

            artist_album = artist_album.get_text()
            artist_album = artist_album[artist_album.find(": ") + 1:]
            artist_album = artist_album.strip().split(" - ", 1)

            artists_albums_return += [artist_album]

        return self.format_soups(artists_albums_return)


class UTRAlbumScrape(AlbumScrape):

    def __init__(self, url, album_tag, album_class, artist_tag, artist_class,
                 platform, page_arr=None, extra_urls=None):
        super().__init__(url=url, album_tag=album_tag, album_class=album_class,
                         artist_tag=artist_tag, artist_class=artist_class, page_arr=page_arr,
                         extra_urls=extra_urls, platform=platform)

    def get_artist_album(self, soup):

        artists_albums_soup = soup.find_all(self.artist_tag, self.artist_class)
        artist_soup = [artist_album.h3.get_text() for artist_album in artists_albums_soup]
        album_soup = [artist_album.h4.get_text() for artist_album in artists_albums_soup]

        artists_albums_soup = [[artist_soup[x], album_soup[x]] for x in range(len(artist_soup))]

        artist_soup = []
        album_soup = []

        for i in range(0, len(artists_albums_soup)):

            if len(artists_albums_soup[i]) >= 2:
                artist_soup += [artists_albums_soup[i][0]]
                album_soup += [artists_albums_soup[i][1]]

        return album_soup, artist_soup

