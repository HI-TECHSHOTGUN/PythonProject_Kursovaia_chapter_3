import os
from datetime import datetime

import requests

ABS_PATH = os.path.abspath(os.path.join(os.getcwd(), ".."))


def main():
    # date_str = "2025-02-11"
    # date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    # day_of_week = date_obj.weekday()
    # return day_of_week
    url = 'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol=TSLA&interval=1min&apikey=9DLPPUH2V1AMH91C'
    r = requests.get(url)
    data = r.json()

    print(data)


if __name__ == '__main__':
    print(main())
    # print(type(main()))