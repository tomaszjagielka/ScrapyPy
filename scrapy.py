#!/usr/bin/env python3
"""ScrapyPy - Backpack.tf & Scrap.tf trading bot.
Fetches data from backpack.tf and scrapy.tf and trades with their bots if profitable.

First it initializes APIs it uses and get items. Optionally creates alerts for them.
Because of the alerts, it can fetch unread notifications and mark them as read.
From alerts, it gets needed data, like item's name or price.
Then it calculates profit, which the bot uses to check if it should trade.
It updates key price and item data every UPDATE_INTERVAL.
"""

import json
import os
import time
import requests

import dotenv
from bs4 import BeautifulSoup

import prices_api
import backpack_api
import currency

# Load environment variables.
dotenv.load_dotenv()
BACKPACK_CLIENT_ID = os.getenv("BACKPACK_CLIENT_ID")
BACKPACK_CLIENT_SECRET = os.getenv("BACKPACK_CLIENT_SECRET")
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL"))
CREATE_ALERTS = os.getenv("CREATE_ALERTS") == "TRUE"


def get_items(key_price):
    """Scrapes items from scrap.tf.

    Gets items and puts them in a dict.
    Fetches price of the items and converts it to half-scrap currency.
    It also saves their limits (min & max amount of allowed items) on scrap.tf website.

    Args:
        key_price: Price of one key in half-scraps.

    Returns:
        A dict mapping scrap.tf item names to their corresponding data.
        Example data:

        {'Non-Craftable Tough Break Key':
        {'price_to_buy': 1518, 'price_to_sell': 1494, 'limit_bottom': 3, 'limit_up': 25}}
    """

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:47.0) Gecko/20100101 Firefox/47.0'
    }
    response = requests.get("https://scrap.tf/items", headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")
    items_data = soup.select("#itembanking-list > tbody > tr")
    with open("data/item_names.json", encoding="utf-8") as file:
        backpack_items_data = json.load(file)
    items = {}

    for item_data in items_data:
        # item = Item()

        # item.quality = item_data.get("data-quality")
        # name = int(item_data.get("data-name"))

        price_to_buy = currency.scraptf_item_price_to_half_scrap(
            next(item_data.contents[5].stripped_strings), key_price)
        price_to_sell = currency.scraptf_item_price_to_half_scrap(
            next(item_data.contents[7].stripped_strings), key_price)

        limit_bottom = int(item_data.contents[9].select_one(
            "div > div > div:nth-child(1)").get_text())
        limit_up = int(item_data.contents[9].select_one(
            "div > div > div:nth-child(2)").get_text())

        item_name = item_data.contents[3].get_text().strip()
        backpack_item_names = backpack_items_data.get(item_name)

        if backpack_item_names:
            for backpack_item_name in backpack_item_names:
                items[backpack_item_name] = {
                    "price_to_buy": price_to_buy,
                    "price_to_sell": price_to_sell,
                    "limit_bottom": limit_bottom,
                    "limit_up": limit_up,
                }

    return items


def update_key_price(client):
    """Updates key price for later use.

    It uses prices.tf API to update key price.
    It's needed to correctly calculate profit value.

    Args:
        client:
          prices.tf API client. You can get it by initializing object of prices_api.py class.

    Returns:
        Price of a key in half-scraps.
    """

    key_price = None

    while not key_price:
        key_price = client.get_key_price()

        # if not key_price:
        #     print(
        #         f"[ERROR] Could not update key price. Retrying in 30 seconds..."
        #     )
        #     time.sleep(30)

    return key_price


def create_alerts(client, items):
    """Creates alerts on backpack.tf.

    Creates buy & sell alert for every item in data/item_names.json.

    Args:
        client:
          backpack.tf API client. You can get it by initializing object of backpack_api.py class.
        items:
          Dictionary of items for which alerts will be created.
    """

    for item_name in items:
        client.create_alert(item_name, "buy")
        client.create_alert(item_name, "sell")


def main():
    """Entry point of the Scrapy bot."""

    backpack_client = backpack_api.Client(BACKPACK_CLIENT_ID,
                                          BACKPACK_CLIENT_SECRET)
    prices_client = prices_api.Client()
    key_price = update_key_price(prices_client)
    items = get_items(key_price)
    next_update = time.time() + UPDATE_INTERVAL

    if CREATE_ALERTS:
        create_alerts(backpack_client, items)

    while True:
        unread_notifications = backpack_client.get_unread_notifications_and_mark_as_read(
        )

        for unread_notification in unread_notifications:
            # trade_url = unread_notification.get("targetUser").get("tradeOfferUrl")
            url = unread_notification.get("contents").get("url")
            listing = unread_notification.get("bundle").get("listing")
            currencies = listing.get("currencies")
            name = listing.get("item").get("name")

            if name in items:
                keys_in_scrap = currency.keys_to_half_scrap(
                    currencies.get("keys"), key_price)
                refined_in_scrap = currency.refined_to_half_scrap(
                    currencies.get("metal"))
                price = keys_in_scrap + refined_in_scrap

                intent = listing.get("intent")
                if intent == "sell":
                    if items[name].get("limit_bottom") >= items[name].get(
                            "limit_up"):
                        continue

                    profit = items[name].get("price_to_sell") - price
                    if profit > 0:
                        # print(name + " profit: " + str(profit) + " intent: " +
                        #       intent + " price_to_buy: " + str(price) +
                        #       " price_to_sell: " +
                        #       str(items[name].get("price_to_sell")))
                        print("profit: " + str(profit) + " intent: " + intent +
                              " name: " + name + " url: https://backpack.tf" +
                              url)
                else:
                    if items[name].get("limit_bottom") == 0:
                        continue

                    profit = price - items[name].get("price_to_buy")
                    if profit > 0:
                        print("profit: " + str(profit) + " intent: " + intent +
                              " name: " + name + " url: https://backpack.tf" +
                              url)
            # else:
                # print(f"[WARNING] {name} not in the item_names.json!")
                # print(items)

        current_time = time.time()
        if current_time >= next_update:
            key_price = update_key_price(prices_client)
            items = get_items(key_price)
            next_update = current_time + UPDATE_INTERVAL

        # Throttle to avoid backpack.tf Too Many Requests error.
        time.sleep(0.7)


if __name__ == "__main__":
    main()
