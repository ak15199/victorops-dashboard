import requests
from time import sleep

import logfactory


logger = logfactory.create(__name__)


class Http(object):

    def __init__(self, secrets):
        self.headers = {
                    "Accept": "application/json",
                    "X-VO-Api-Id": secrets.get("apiid"),
                    "X-VO-Api-Key": secrets.get("apikey"),
                }

    def get(self, url, field, params={}):
        return requests.get(url, headers=self.headers, params=params).json()[field]

    def paged_get(self, url, field, params={}):
        response = []

        offset = 0
        params["limit"] = 90

        while True:
            params["offset"] = offset

            while True:
                reply = requests.get(url, headers=self.headers, params=params)
                if reply.status_code == 403:
                    print("Rate limited: pause and retry")
                    sleep(5)
                    continue

                break

            json = reply.json()
            response = response + json[field]
            if json["total"] == len(response):
                return response

            offset += params["limit"]
