import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
from threading import Thread
from queue import Queue

load_dotenv(".env")
search_url = os.getenv("CARDS_SEARCH")
session = requests.Session()

os.chdir("original")


def getpage(page_n, queue):
    pointeur = page_n * 30
    response = session.get(f"{search_url}{pointeur}")
    soup = BeautifulSoup(response.content, "html.parser")
    queue.put(soup)


def saveimg(soup, img_index):
    title = soup.select(f"#r_main{img_index} .Card16")[0].text
    img_url = f'http://www.mtgpics.com{soup.select(f"#r_main{img_index} a img")[0].attrs["src"]}'
    img_url = img_url.replace("reg", "big")

    img_content = session.get(img_url).content

    with open(f"{title}.jpg", "wb") as image:
        image.write(img_content)


total_pages = 300
pages = Queue()
threads = [None for i in range(4)]

# get pages

for p in range(3, total_pages + 1, 4):
    print(p)
    for i in range(4):
        page = p - i
        t = Thread(target=getpage, args=(page, pages))
        t.start()
        threads[i - 1] = t
    for t in threads:
        t.join()

# save images

threads.append(None)

while not pages.empty():
    page = pages.get()
    print(pages.qsize())
    for c in range(5, 31, 5):
        for i in range(5):
            card_index = c - i
            t = Thread(target=saveimg, args=(page, card_index))
            t.start()
            threads[i - 1] = t
        for t in threads:
            t.join()

session.close()