<br><h1 align="center">ScrapyPy</h1>

<p align="center">
Backpack.tf & Scrap.tf trading bot written in Python.<br>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/%20-Python-%233776AB?logo=python&logoColor=white" alt="Python"></a>
</p><br>

## How it works?
It fetches data from Backpack.tf and Scrapy.tf, compares their buy and sell prices of items and finally trades with their bots if profitable.

1. First it initializes APIs it uses and gets items. Optionally creates Backpack.tf alerts for them.
2. Because of the alerts, it can fetch unread notifications and mark them as read.
3. From alerts, it gets needed data, such as the name of the item or price.
4. Then it calculates profit, that the bot uses to check if it should trade the item by comparing prices between the two websites.
5. It updates key (currency) price and item data every `UPDATE_INTERVAL`.

## Installation
1. Clone the repository.
```sh
git clone https://github.com/tomaszjagielka/ScrapyPy.git
```
2. Install Python packages.
```sh
pip install -r requirements.txt
 ```
 
 ## Usage
 1. Configure your bot by editing the `template.env` file.
 2. Rename the `template.env` file to `.env`
 3. Enter your Steam Guard credentials into the `template.steam_guard.txt` file in the `data` directory.
 4. Rename the `template.steam_guard.txt` file to `steam_guard.txt`
 5. Run the bot using `py scrapy.py`