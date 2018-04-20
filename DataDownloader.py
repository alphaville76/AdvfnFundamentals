import pandas as pd
import numpy as np
import requests
import os
import html
from LogUtil import create_logger

console_log = create_logger()
log = create_logger('AdvfnFundamentals')

ALPHAVANTAGE_API_KEY=os.environ.get('ALPHAVANTAGE_API_KEY')
OUTPUTSIZE_MAP = {'5y': 5 * 252, '2y': 2 * 252, '1y': 252, '6m': 6 * 21, '3m': 3 * 21, '1m': 21}

TIINGO_API_KEY=os.environ.get('TIINGO_API_KEY')
OFFSET_MAP = {'5y': pd.DateOffset(years=5), '2y': pd.DateOffset(years=2), '1y': pd.DateOffset(years=1),
              '6m': pd.DateOffset(months=6), '3m': pd.DateOffset(months=3), '1m': pd.DateOffset(months=1)}

def load_fundamentals(symbol):
    """

    :param symbol:
    :return:

    :raises ValueError: When no data of less than 5 quarters of data are found
    """
    url = "https://ih.advfn.com/p.php?pid=financials&btn=quarterly_reports&symbol=%s" % symbol
    try:
        df = pd.read_html(requests.get(url, headers={'User-agent': 'Mozilla/5.0'}).text,
                      attrs={'style': 'width:705px; text-align:left; background-color: #ffffff;'},
                      index_col=0)[0]
    except ValueError as e:
        raise ValueError("No tables found at " + url)

    df.rename(columns=df.loc['date preliminary data loaded'], inplace=True)
    df.drop(['date preliminary data loaded'], inplace=True)
    df.index.name = 'datekey'


    # drop all calculations
    df = df.iloc[:df.index.get_loc('RATIOS CALCULATIONS')]


    df.dropna(inplace=True)

    if len(df) == 0:
        raise ValueError("Less than 5 quarters of data found for " + symbol)

    df.index = df.index.str.title()

    df.loc['price_datekey'] = prices(symbol, df.columns)['close'].values

    return df


def _normalise_ticker(ticker):
    t = str(ticker).strip()
    t = t.upper()

    index_of = t.find('^')
    if index_of > 0:
        t = t[:-index_of]
    return t


def load_companies(stock_exchange):
    tickers_host = "https://www.nasdaq.com/screening/companies-by-name.aspx?letter=0&render=download&exchange=%s"
    df = pd.read_csv(tickers_host % stock_exchange.upper(), index_col=0)
    df.drop(columns=["LastSale","MarketCap","IPOyear","Summary Quote", "Unnamed: 8"], inplace=True)


    # Remove whitespaces from index
    df.index = df.index.map(_normalise_ticker)


    df.columns = df.columns.str.title()

    # only primary common stocks have Sector and Industry
    df.dropna(inplace=True)

    df['Name'] = df['Name'].apply(lambda name: html.unescape(name.strip()))
    # drop duplicate name, usually class B stocks
    df.sort_index(inplace=True)
    df.drop_duplicates(subset=['Name'], inplace=True)


    df['Sector'] = df['Sector'].apply(lambda s: str(s).strip().title())
    df['Industry'] = df['Industry'].apply(lambda s: str(s).strip().title())

    df.drop(df[df['Sector'] == 'Finance'].index, inplace=True)
    df.drop(df[df['Industry'].str.startswith('Real Estate')].index, inplace=True)

    df.to_csv('data/%s.csv' % (stock_exchange.upper()))
    return df


def history_iex(symbol, frequency='2y'):
    """
    Close price adjusted for both dividends and splits.
    frequency: allowed values: 5y, 2y, 1y, ytd, 6m, 3m, 1m
    """
    if frequency not in ['5y', '2y', '1y', 'ytd', '6m', '3m', '1m']:
        raise ValueError("Allowed frequency values: 5y, 2y, 1y, ytd, 6m, 3m, 1m.")
    df = pd.read_json('https://api.iextrading.com/1.0/stock/%s/chart/%s' % (symbol, frequency))
    df.set_index('date', inplace=True)
    df.drop(columns=['changeOverTime', 'label', 'unadjustedVolume'], inplace=True)
    return df


def history_alphavantage(symbol, frequency='2y'):
    """
    Close price adjusted for both dividends and splits.
    frequency: allowed values: 5y, 2y, 1y, 6m, 3m, 1m
    """
    if frequency not in ['5y', '2y', '1y', '6m', '3m', '1m']:
        raise ValueError("Allowed frequency values: 5y, 2y, 1y, 6m, 3m, 1m.")

    df = pd.read_csv(
        'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_ADJUSTED&symbol=%s&outputsize=%s&apikey=%s&datatype=csv' %
        (symbol, 'full', ALPHAVANTAGE_API_KEY),
        index_col=0)
    df = df.iloc[:OUTPUTSIZE_MAP[frequency]]
    df.drop(columns=['adjusted_close'], inplace=True)
    df.sort_index(inplace=True)
    df.index.name = 'date'
    
    return df


def _query_prices(symbol, start_date, end_date):
    df = pd.read_json(
        'https://api.tiingo.com/tiingo/daily/%s/prices?startDate=%s&endDate=%s&token=%s' %
        (symbol, start_date, end_date, TIINGO_API_KEY))
    df.set_index('date', inplace=True)
    df.drop(columns=['adjClose', 'adjHigh', 'adjLow', 'adjOpen', 'adjVolume'], inplace=True)
    df = df[['open', 'high', 'low', 'close', 'volume', 'divCash', 'splitFactor']]
    df.columns = ['open', 'high', 'low', 'close', 'volume', 'dividend', 'split']
    return df


def history(symbol, frequency='2y'):
    """
    Close price adjusted for both dividends and splits.
    frequency: allowed values: 5y, 2y, 1y, 6m, 3m, 1m
    """
    if frequency not in ['5y', '2y', '1y', '6m', '3m', '1m']:
        raise ValueError("Allowed frequency values: 5y, 2y, 1y, 6m, 3m, 1m.")

    end_date = pd.Timestamp.today().date()
    start_date = end_date - OFFSET_MAP[frequency]
    df = _query_prices(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
    return df


def prices(symbol, dates=None, start=None, end=None):
    if start is not None:
        return _query_prices(symbol, start, end)

    d = pd.to_datetime(dates)

    df = history(symbol)
    new_index = pd.date_range(df.index[0], df.index[-1])
    df['date'] = df.index
    df = df.reindex(new_index)
    df.fillna(method='ffill', inplace=True)

    ret = df.loc[d]
    ret['query_date'] = ret.index
    ret.index = ret['date']
    ret.drop(columns=['date'], inplace=True)
    return ret


def download_all():
    stock_exchanges = ('NASDAQ', 'NYSE', 'AMEX')
    for exchange in stock_exchanges:
        target_dir = 'data/%s' % exchange
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
        companies = load_companies(exchange)
        for symbol in companies.index:
            console_log.info(symbol)
            try:
                df = load_fundamentals("%s%%3A%s" % (exchange, symbol))
                df.to_csv("%s/%s.csv" % (target_dir, symbol))
            except ValueError as e:
                log.warn("No data for '%s' %s\n\t%s" % (symbol, ', '.join(companies.loc[symbol]), e))



if __name__ == "__main__":
    #download_all()
    exchange = 'NYSE'
    symbol = 'IBM'
    #df = load_fundamentals(symbol)
    #target_dir = 'data/%s' % exchange
    #df.to_csv("%s/%s.csv" % (target_dir, symbol))
    #print(history('IBM'))
    #print(prices(symbol, start='2017-03-11', end='2018-03-03'))
    #print(prices(symbol, ['2017-03-11', '2017-04-29', '2017-07-29', '2017-11-04', '2018-03-03']))
    print(history(symbol, '1m'))



