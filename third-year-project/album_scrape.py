from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from unicodedata import normalize


class AlbumScrape:

    def __init__(self, url, album_tag, album_class, artist_tag, artist_class, page_arr=None, extra_urls=None):

        service = Service(executable_path=ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service)
        self.url = url
        self.urls = []
        self.page_arr = page_arr
        self.album_tag = album_tag
        self.album_class = album_class
        self.artist_tag = artist_tag
        self.artist_class = artist_class
        self.records = []
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
                break

            content = self.driver.page_source

            soup = BeautifulSoup(content, features="html.parser")

            albums_soup, artists_soup = self.get_artist_album(soup)

            artists += artists_soup
            albums += albums_soup

        self.records += [[album, artist] for album, artist in zip(albums, artists)]

    def get_artist_album(self, soup):

        artists_soup = soup.find_all(self.artist_tag, self.artist_class)
        albums_soup = soup.find_all(self.album_tag, self.album_class)

        return [album.text for album in albums_soup], [artist.text for artist in artists_soup]

    def get_records(self):

        return self.records


class SingleClassAlbumScrape(AlbumScrape):

    def __init__(self, url, album_tag, album_class, page_arr=None, extra_urls=None, sep=None):
        super().__init__(url, album_tag, album_class, artist_tag=None, artist_class=None,
                         page_arr=page_arr, extra_urls=extra_urls)

        self.sep = sep

    def get_artist_album(self, soup):

        artists_albums_soup = soup.find_all(self.album_tag, self.album_class)
        artists_albums_soup = [artist_album.a.get_text().split(self.sep, 1) for artist_album in
                               artists_albums_soup]

        artist_soup = []
        album_soup = []

        for i in range(0, len(artists_albums_soup)):
            if len(artists_albums_soup[i]) >= 2:

                artist_soup += [artists_albums_soup[i][0]]
                album_soup += [artists_albums_soup[i][1]]

        return album_soup, artist_soup


class LAQAlbumScrape(SingleClassAlbumScrape):

    def __init__(self, url, album_tag, album_class, page_arr=None, extra_urls=None):
        super().__init__(url, album_tag, album_class, page_arr, extra_urls)

    def get_artist_album(self, soup):
        artists_albums_soup = soup.find_all(self.artist_tag, self.artist_class)
        artists_albums_soup = [artist_album.a.get_text(strip=True, separator='\n').splitlines() for artist_album in
                               artists_albums_soup]

        artist_soup = [artists_albums_soup[i][0] for i in range(0, len(artists_albums_soup))]
        album_soup = [artists_albums_soup[i][1] for i in range(0, len(artists_albums_soup))]

        return album_soup, artist_soup


class SkinnyAlbumScrape(SingleClassAlbumScrape):

    def __init__(self, url, album_tag, album_class, page_arr=None, extra_urls=None):
        super().__init__(url, album_tag, album_class, page_arr, extra_urls)

    def get_artist_album(self, soup):
        artists_albums_soup = soup.find_all(self.artist_tag, self.artist_class)
        artists_albums_soup = [artist_album.text.strip().split(" – ", 1) for artist_album in artists_albums_soup]

        album_soup = [artists_albums_soup[i][1] for i in range(0, len(artists_albums_soup))]
        artist_soup = [artists_albums_soup[i][0] for i in range(0, len(artists_albums_soup))]

        return album_soup, artist_soup


class NMEAlbumScrape(SingleClassAlbumScrape):

    def __init__(self, url, album_tag, album_class, page_arr=None, extra_urls=None):
        super().__init__(url, album_tag, album_class, page_arr, extra_urls)

    def get_artist_album(self, soup):
        artists_albums_soup = soup.find_all(self.artist_tag, self.artist_class)
        artists_albums_soup = [normalize("NFKD", artist_album.a.get_text(strip=True)).split(" review")[0].split(" – ", 1)
                               for artist_album in artists_albums_soup]

        album_soup = [artists_albums_soup[i][1].replace("'", "") for i in range(0, len(artists_albums_soup))]
        artist_soup = [artists_albums_soup[i][0] for i in range(0, len(artists_albums_soup))]

        return album_soup, artist_soup


class OHMAlbumScrape(AlbumScrape):

    def __init__(self, url, header_tag, header_class, main_tag, main_class, page_arr=None, extra_urls=None):
        super().__init__(url, album_tag=None, album_class=None, artist_tag=None,
                         artist_class=None, page_arr=page_arr, extra_urls=extra_urls)

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

        album_soup = [main_soup[i][1] for i in range(0, len(main_soup))] + \
                     [headers_soup[i][1] for i in range(0, len(headers_soup))]

        artist_soup = [main_soup[i][0] for i in range(0, len(main_soup))] + \
                      [headers_soup[i][0] for i in range(0, len(headers_soup))]

        return album_soup, artist_soup



