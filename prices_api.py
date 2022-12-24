"""Prices.tf API wrapper.

It allows you to get current SELL price of a key.
"""

import requests

ACCESS_TOKEN_URL = "https://backpack.tf/oauth/access_token"


class Client:
    """A Prices.tf API wrapper."""

    def __init__(self):
        self._token = None
        self.fetch_token()

    def fetch_token(self):
        """Fetches Prices.tf API token."""

        try:
            request = requests.post("https://api2.prices.tf/auth/access")

            if request.status_code != 200:
                print(
                    f"[ERROR] Could not fetch Scrap.tf token (status code: {request.status_code})"
                )
                return

            self._token = request.json()['accessToken']
        except requests.exceptions.ConnectionError:
            print("[ERROR] Could not fetch Scrap.tf token (reason: ConnectionError)")

    def get_key_price(self):
        """Fetches current SELL price of a key."""

        if self._token:
            headers = {"authorization": "Bearer " + self._token}
            url = "https://api2.prices.tf/prices/5021%3B6"

            try:
                request = requests.get(url, headers=headers)

                if request.status_code == 401:
                    self.fetch_token()
                    headers = {"authorization": "Bearer " + self._token}
                    request = requests.get(url, headers=headers)

                if request.status_code != 200:
                    print(
                        f"[ERROR] Could not get key's sell price (status code: {request.status_code})"
                    )
                    return None

                return request.json().get("sellHalfScrap")
            except requests.exceptions.ConnectionError:
                print("[ERROR] Could not get key's sell price (reason: ConnectionError)")

                return None

        return None
