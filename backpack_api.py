"""Backpack.tf API wrapper.

It allows you to create alerts and get unread notifications and mark them as read.

  Typical usage example:

  client = Client()
  client.create_alert("Mann Co. Supply Crate Key", "buy")
  unread_notifications = client.get_unread_notifications_and_mark_as_read()
"""

import urllib
import requests

import requests_oauthlib
import oauthlib.oauth2

ACCESS_TOKEN_URL = "https://backpack.tf/oauth/access_token"


class Client:
    """A Backpack.tf API wrapper."""

    def __init__(self, client_id, client_secret):
        self._token = None
        self._client_id = client_id
        self._client_secret = client_secret

        client = oauthlib.oauth2.BackendApplicationClient(
            client_id=self._client_id)
        self._oauth = requests_oauthlib.OAuth2Session(client=client)
        self.fetch_token()

    def fetch_token(self):
        """Fetches Backpack.tf API token using oauth."""

        self._token = self._oauth.fetch_token(
            token_url=ACCESS_TOKEN_URL,
            client_id=self._client_id,
            client_secret=self._client_secret
        )

    def create_alert(self, item_name, intent):
        """Creates alert for item with 'buy' or 'sell' intent specified by user.

        The alert causes notifications of item's new buy or sale offers to appear.

        Args:
            item_name:
              Name of the item for which the alert will be created.
            intent:
              Intent of the item alert.

              'buy': Returns all notifications for item's buy offers.
              'sell': Returns all notifications for item's sell offers.
        """

        payload = {"item_name": item_name, "intent": intent, "blanket": 1}
        encoded_payload = urllib.parse.urlencode(payload)

        # Helper function, so we don't duplicate code.
        def create_alert():
            client = requests_oauthlib.OAuth2Session(self._client_id,
                                                     token=self._token)
            request = client.post(
                "https://backpack.tf/api/1.0/classifieds/alerts?" +
                encoded_payload)

            if request.status_code != 200:
                print(
                    f"[ERROR] Could not create {item_name} {intent} alert"
                    f" (reason: {request.reason})"
                )
                return

            print(
                f"[INFO] Created {item_name} {intent} alert with ID: {request.json()['id']}"
            )

        try:
            create_alert()
        except oauthlib.oauth2.TokenExpiredError:
            self.fetch_token()
            create_alert()
        except requests.exceptions.ConnectionError:
            print(
                f"[ERROR] Could not create {item_name} alert (reason: ConnectionError)"
            )

    def get_unread_notifications_and_mark_as_read(self):
        """Gets Backpack.tf notifications and marks them as read.

        Returns:
            A list of notifications.
            Each notification has data formatted in json.
            Go to https://backpack.tf/api/index.html#/notifications/c17e601700791645c8426f3583062748
            if you want to see an example of a notification given its id.
            The json data of it is too big to put it here.
        """

        # See create_alert() comment.
        def get_unread_notifications_and_mark_as_read():
            client = requests_oauthlib.OAuth2Session(self._client_id,
                                                     token=self._token)

            # TODO: Handle connection error.
            request = client.post(
                "https://backpack.tf/api/1.0/notifications/unread")

            if request.status_code != 200:
                print(
                    "[ERROR] Could not get unread notifications and mark them as read"
                    f" (reason: {request.reason})"
                )
                return {}

            return request.json()

        try:
            return get_unread_notifications_and_mark_as_read()
        except oauthlib.oauth2.TokenExpiredError:
            self.fetch_token()
            return get_unread_notifications_and_mark_as_read()
        except requests.exceptions.ConnectionError:
            print(
                "Could not get unread notifications and mark them as read (reason: ConnectionError)"
            )
            return []
