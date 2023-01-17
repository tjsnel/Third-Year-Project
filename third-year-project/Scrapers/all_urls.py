from url_scrape import SingleURLScrape, URLScrape, GuardianURLScrape, NMEURLScrape

# spectrum_scrape = SingleURLScrape(url="https://spectrumculture.com/category/music/music-reviews/page/{}/",
#                                   album_tag="h2", album_class={"class": "entry-title"},
#                                   url_tag="h2", url_class={"class": "entry-title"},
#                                   page_arr=[x for x in range(1, 809)],
#                                   sep=": ",
#                                   platform="Spectrum")
#
# spectrum_scrape.get_data()
# print(spectrum_scrape.get_records().loc[:, ["Artist", "Url"]])
# spectrum_scrape.write_records()

# guardian_scrape = GuardianURLScrape(url="https://www.theguardian.com/music+tone/albumreview?page={}",
#                                     album_tag="div",
#                                     album_class={"class": "fc-item__content fc-item__content--has-stars"},
#                                     url_tag="div",
#                                     url_class={"class": "fc-item__content fc-item__content--has-stars"},
#                                     platform="Guardian")
#
# guardian_scrape.get_data()
# print(guardian_scrape.get_records())
# guardian_scrape.write_records()

# nme_scrape = NMEURLScrape(url="https://www.nme.com/reviews/album/page/{}",
#                           album_tag="h3", album_class={"class": "entry-title td-module-title"},
#                           url_tag="h3", url_class={"class": "entry-title td-module-title"},
#                           page_arr=[x for x in range(1, 959)],
#                           platform="NME")
#
# nme_scrape.get_data()
# print(nme_scrape.get_records())
# nme_scrape.write_records()

# pitchfork_scrape = URLScrape(url="https://pitchfork.com/reviews/albums/?page={}",
#                              album_tag="h2",
#                              album_class={"class": "review__title-album"},
#                              artist_tag="ul",
#                              artist_class={"class": "artist-list review__title-artist"},
#                              url_tag="div",
#                              url_class={"class": "review"},
#                              page_arr=[x for x in range(1, 10001)],
#                              platform="Pitchfork")
#
# pitchfork_scrape.get_data()
# print(pitchfork_scrape.get_records())
# pitchfork_scrape.write_records()
