from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

i = 0
artists = []
albums = []

while True:

    i += 1

    try:
        driver.get("https://pitchfork.com/reviews/albums/?page={}".format(i))
    except:
        break

    content = driver.page_source

    soup = BeautifulSoup(content, features="html.parser")

    artists_soup = soup.find_all("ul", {"class": "artist-list review__title-artist"})
    albums_soup = soup.find_all("h2", {"class": "review__title-album"})

    artists += [artist.text for artist in artists_soup]
    albums += [album.text for album in albums_soup]

records = [[album, artist] for album, artist in zip(albums, artists)]
print(records)