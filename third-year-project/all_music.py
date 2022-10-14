from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from album_scrape import AlbumScrape
from album_scrape import LAQAlbumScrape

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

i = 0
artists = []
albums = []

# pitchfork_scrape = AlbumScrape("https://pitchfork.com/reviews/albums/?page={}", "h2", {"class": "review__title-album"},
#                                "ul", {"class": "artist-list review__title-artist"}, [x for x in range(1, 6)])
#
# pitchfork_scrape.get_data()
# print(pitchfork_scrape.get_records())

# Need to work out how to split on <br>

# laq_scrape = LAQAlbumScrape(url="https://www.loudandquiet.com/reviews/page/{}/", album_tag="div",
#                             album_class={"class": "loudandquiet-listblock"}, artist_tag="div",
#                             artist_class={"class": "loudandquiet-listblock"}, page_arr=[2],
#                             extra_urls=["https://www.loudandquiet.com/reviews/"])
#
# laq_scrape.get_data()
# laq_scrape.get_records()


