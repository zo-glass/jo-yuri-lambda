import hashlib
import time
from model.video import Video

import requests

import json

import urllib3
import os

# ADD AWS-Parameters-and-Secrets-Lambda-Extension-Arm64 Layer

http = urllib3.PoolManager()

# Secret Manager cost2much
def getKey(name, ssm=True):
    url = ""
    headers = {"X-Aws-Parameters-Secrets-Token": os.environ.get('AWS_SESSION_TOKEN')}

    if ssm:
        url = f"http://localhost:2773/systemsmanager/parameters/get?name={name}&withDecryption=true"
    else:
        url = f"http://localhost:2773/secretsmanager/get?secretId={name}"

    try:
        res = http.request("GET", url, headers=headers, timeout=1)
        if res.status == 200:
            if ssm:
                response = json.loads(res.data.decode("utf-8"))
                return response['Parameter']['Value']
            else:
                data = json.loads(res.data.decode("utf-8"))
                return data.get('SecretString')
    except Exception as e:
        print(f"errorDescription: {e}")
    return None

class YouTube():
    url = "https://www.googleapis.com/youtube/v3/playlistItems"
    channelId = "UCSEVFgCkKem_c3nIBm7F37g"
    uploads = "UUSEVFgCkKem_c3nIBm7F37g"
    

    def __init__(self, db):
        self.video = Video(db)
        self.apiKey = getKey("jo-yuri-youtube-api-key")

    def start(self):
        items = self.fetchVideos()
        for item in items:
            item["ttl"] = int(time.time()) + 48 * 60 * 60
            self.video.post_handler(item, "System")

    def fetchVideos(self):
        videos = []
        pageToken = None

        while (True):
            params = {
                "part": "snippet",
                "playlistId": self.uploads,
                "maxResults": 50,
                "key": self.apiKey,
            }
            if pageToken:
                params["pageToken"] = pageToken

            response = requests.get(self.url, params=params).json()

            for item in response["items"]:
                video = {}
                video["id"] = int(hashlib.sha256(item["snippet"]["resourceId"]["videoId"].encode("utf-8")).hexdigest(), 16) % (10 ** 16)
                video["title"] = item["snippet"]["title"]
                video["imgAlt"] = item["snippet"]["title"]
                video["href"] = f"https://www.youtube.com/watch?v={item["snippet"]['resourceId']['videoId']}"
                video["imgSrc"] = f"https://img.youtube.com/vi/{item["snippet"]['resourceId']['videoId']}/maxresdefault.jpg"

                videos.append(video)

            if 'nextPageToken' in response:
                pageToken = response['nextPageToken']
            else:
                break

        return videos
