import time
import hashlib
from datetime import datetime
import xml.etree.ElementTree as ET
from model.news import News

import urllib.request
import urllib.parse

import requests
from bs4 import BeautifulSoup

from googlenewsdecoder import gnewsdecoder 

import json

class GoogleNews():
    #url = "https://news.google.com/rss/topics/CAAqKAgKIiJDQkFTRXdvTkwyY3ZNVEZtYUd0alpHaHJNaElDWlc0b0FBUAE?hl=en-US&gl=US&ceid=US:en"
    #url = "https://news.google.com/rss/search?q=%22jo+yu-ri%22+OR+%22jo+yuri%22+OR+%22joyuri%22+OR+%22%EC%A1%B0%EC%9C%A0%EB%A6%AC%22&hl=en-US&gl=US&ceid=US:en"
    url = "https://news.google.com/rss/search?q=%22jo+yu-ri%22&hl=en-US&gl=US&ceid=US:en"

    def __init__(self, db):
        self.news = News(db)

    def start(self):
        items = self.fetchNews()
        for item in items:
            ttl = int(time.time()) + 48 * 60 * 60 * 7
            self.news.post_handler(item, "System", ttl)

    def fetchNews(self):
        articles = []

        req = requests.get(self.url)
        tree = ET.fromstring(req.text)

        for item in tree[0]:
            article = {}

            if item.tag == 'item':
                durl = gnewsdecoder(item[1].text, interval=1)["decoded_url"]

                if durl:
                    source = requests.get(durl).text
                    soup = BeautifulSoup(source, features="html.parser")
                    title = soup.find("meta", attrs={'property': 'og:title'})
                    image = soup.find("meta", attrs={'property': 'og:image'})

                if title and image is not None:
                    article["alt"] = item[0].text
                    article["src"] = image["content"]

                #article["id"] = int(hashlib.sha256(item[2].text.encode("utf-8")).hexdigest(), 16) % (10 ** 16)
                article["id"] = datetime.strptime(item[3].text, "%a, %d %b %Y %H:%M:%S GMT").isoformat() + "Z"
                article["title"] = (item[0].text.split(" - "))[0]
                article["href"] = item[1].text.replace("/rss", "")
                #article["href"] = durl
                article["date"] = item[3].text[5:16]
                article["origin"] = item[5].text

                articles.append(article)

        return articles
        