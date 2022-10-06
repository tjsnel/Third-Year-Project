from webdriver_manager.chrome import ChromeDriverManager
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup

service = Service(executable_path=ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

i = 0
artists = []
albums = []

urls = ["https://www.metacritic.com/browse/albums/release-date/available/date?"] + \
    ["https://www.metacritic.com/browse/albums/release-date/available/date?page={}".format(x) for x in range(1, 4)]

for url in urls:

    try:
        driver.get(url)
    except:
        break

    content = driver.page_source

    soup = BeautifulSoup(content, features="html.parser")

    artists_soup = soup.find_all("div", {"class": "artist"})
    albums_soup = soup.find_all("a", {"class": "title"})

    artists += [artist.text.replace("by", "").strip() for artist in artists_soup]
    albums += [album.text for album in albums_soup]

records = [[album, artist] for album, artist in zip(albums, artists)]
print(records)