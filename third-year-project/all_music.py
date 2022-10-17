from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from album_scrape import AlbumScrape, LAQAlbumScrape, SkinnyAlbumScrape, NMEAlbumScrape, OHMAlbumScrape, \
    SingleClassAlbumScrape, GuardianAlbumScrape, GigwiseAlbumScrape, UTRAlbumScrape

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

# skinny_scrape = SkinnyAlbumScrape(url="https://www.theskinny.co.uk/music/reviews/albums?page={}",
#                                   album_tag="h2", album_class={"class": "item-title"},
#                                   artist_tag="h2", artist_class={"class": "item-title"},
#                                   page_arr=[x for x in range(1, 382)])
#
# skinny_scrape.get_data()
# print(skinny_scrape.get_records())

# nme_scrape = NMEAlbumScrape(url="https://www.nme.com/reviews/album/page/{}",
#                             album_tag="h3", album_class={"class": "entry-title td-module-title"},
#                             artist_tag="h3", artist_class={"class": "entry-title td-module-title"},
#                             page_arr=[x for x in range(1, 959)])
#
# nme_scrape.get_data()
# print(nme_scrape.get_records())

# ohm_scrape = OHMAlbumScrape(url="https://www.musicomh.com/reviews/albums/page/{}",
#                             header_tag="h2", header_class={"class": "title"},
#                             main_tag="div", main_class={"class": "images_hz"},
#                             page_arr=[x for x in range(1, 486)])
#
# ohm_scrape.get_data()
# print(ohm_scrape.get_records())

# diy_scrape = SingleClassAlbumScrape(url="https://diymag.com/reviews/album/p{}",
#                                     album_tag="h3", album_class={"class": "h-headline"},
#                                     page_arr=[x for x in range(2, 10001),
#                                     extra_urls=["https://diymag.com/reviews/album/"],
#                                     sep="- ")
#
# diy_scrape.get_data()
# print(diy_scrape.get_records())

# uncut_scrape = SingleClassAlbumScrape(url="https://www.uncut.co.uk/reviews/page/{}/",
#                                       album_tag="h3",
#                                       album_class={"class": "entry-title td-module-title"},
#                                       page_arr=[x for x in range(1, 689)],
#                                       sep=" – ")
#
# uncut_scrape.get_data()
# print(uncut_scrape.get_records())

# spectrum_scrape = SingleClassAlbumScrape(url="https://spectrumculture.com/category/music/music-reviews/page/{}/",
#                                          album_tag="h2", album_class={"class": "entry-title"},
#                                          page_arr=[x for x in range(1, 796)],
#                                          sep=": ")
#
# spectrum_scrape.get_data()
# print(spectrum_scrape.get_records())

# guardian_scrape = GuardianAlbumScrape(url="https://www.theguardian.com/music+tone/albumreview?page={}",
#                                       album_tag="div",
#                                       album_class={"class": "fc-item__content fc-item__content--has-stars"})
#
# guardian_scrape.get_data()
# print(guardian_scrape.get_records())

# gigwise_scrape = GigwiseAlbumScrape(url="https://gigwise.com/reviews?page=albums&p={}",
#                                         album_tag="div",
#                                         album_class={"class": "title"})
#
# gigwise_scrape.get_data()
# print(gigwise_scrape.get_records())

# utr_scrape = UTRAlbumScrape(url="https://www.undertheradarmag.com/reviews/category/music/P{}0",
#                             artist_tag="div",
#                             artist_class={"class": "headline"},
#                             album_tag="div",
#                             album_class={"class": "headline"},
#                             page_arr=[x for x in range(1, 420)],
#                             extra_urls="https://www.undertheradarmag.com/reviews/category/music")
#
# utr_scrape.get_data()
# print(utr_scrape.get_records())