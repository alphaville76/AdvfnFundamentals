import pandas as pd
import requests
import json
import datetime

STOCKROW_DICT = {"mkt_cap": "3cf40801-c6e1-4655-9f3a-b18a24a7347a",
                 "ev": "9b66a081-b16f-4793-b0f5-3407467ee6ce"
                }


def load_stockrow_indicator(symbol, indicator):
    url = "https://stockrow.com/api/fundamentals.json?indicators[]=%s&tickers[]=%s"
    response = requests.post(url % (STOCKROW_DICT[indicator], symbol)).text
    response_json = json.loads(response)

    df = pd.DataFrame(response_json['series'][0]['data'])
    df.columns=['date', indicator]
    df['date']=df['date'].apply(lambda posix_time: datetime.datetime.fromtimestamp(posix_time/1000).date())
    df.set_index('date', inplace=True)
    return df


if __name__ == "__main__":
    symbol = 'IBM'
    print(load_stockrow_indicator(symbol, "mkt_cap").tail())
    print(load_stockrow_indicator(symbol, "ev").tail())