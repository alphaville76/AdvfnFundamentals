import pandas as pd
from XBRL import lookup_cik_by_name
from SecEdgarDAO import SecEdgarDAO
import requests
import io
import time
from LogUtil import create_logger

log = create_logger('MorningstarDAO')
MS_EXCHANGE = {'NASDAQ': 'XNAS', 'NYSE': 'XNYS', 'AMEX': 'XASE'}

class MorningstarDAO(object):

    def __init__(self):

        self.url = "http://financials.morningstar.com/ajax/ReportProcess4CSV.html?t=%s&reportType=%s&period=%d&dataType=A&order=asc&columnYear=5&number=%d"

        # reportType: is = Income Statement, cf = Cash Flow, bs = Balance Sheet
        self.reportType = {'bs': 'Balance Sheet', 'is': 'Income Statement', 'cf': 'Cash Flow'}

        # period: 12 for annual reporting, 3 for quarterly reporting
        self.period = 3

        # number: The units of the response data. 1 = None 2 = Thousands 3 = Millions 4 = Billions
        self.number = 2

    def load_fundamentals(self, symbol, exchange=None):
        f = pd.DataFrame()
        for report in self.reportType.keys():
            if exchange is None:
                full_url = self.url % (symbol, report, self.period, self.number)
            else:
                t = "%s%%3A%s" % (MS_EXCHANGE[exchange], symbol)
                full_url = self.url % (t, report, self.period, self.number)

            for i in range(1, 11):
                csv = requests.get(full_url, timeout=10).content.decode('utf-8')
                if (len(csv) > 0):
                    break
                log.warn("%s - retry #%d in 3s" % (full_url, i))
                time.sleep(3)

            df = pd.read_csv(io.StringIO(csv), header=1, index_col=0)
            df.index.name = ''
            if report == 'bs':
                df.index = df.index.where(~df.index.duplicated(keep='first'), 'Non-current ' + df.index)
                df.rename(index={'Deferred revenues': 'Current Deferred revenues'}, inplace=True)
                df.drop("Assets", axis=0, inplace=True, errors='ignore')
                df.drop("Current assets", axis=0, inplace=True, errors='ignore')
                df.drop("Cash", axis=0, inplace=True, errors='ignore')
                df.drop("Non-current assets", axis=0, inplace=True, errors='ignore')
                df.drop("Property, plant and equipment", axis=0, inplace=True, errors='ignore')
                df.drop("Liabilities and stockholders' equity", axis=0, inplace=True, errors='ignore')
                df.drop("Liabilities", axis=0, inplace=True, errors='ignore')
                df.drop("Current liabilities", axis=0, inplace=True, errors='ignore')
                df.drop("Non-current liabilities", axis=0, inplace=True, errors='ignore')
                df.drop("Stockholders' equity", axis=0, inplace=True, errors='ignore')
            if report == 'is':
                df.drop('TTM', axis=1, inplace=True, errors='ignore')
                df.index = df.index.where(~df.index.duplicated(keep='first'),
                                          'Weighted average shares outstanding ' + df.index)
                df.rename(index={'Basic': 'Earnings per share Basic', 'Diluted': 'Earnings per share Diluted'},
                          inplace=True)
                df.drop("Operating expenses", axis=0, inplace=True, errors='ignore')
                df.drop("Earnings per share", axis=0, inplace=True, errors='ignore')
                df.drop("Weighted average shares outstanding", axis=0, inplace=True, errors='ignore')
            if report == 'cf':
                df.drop('TTM', axis=1, inplace=True, errors='ignore')
                df.drop('Net income', axis=0, inplace=True, errors='ignore')
                df.drop("Cash Flows From Operating Activities", axis=0, inplace=True, errors='ignore')
                df.drop("Cash Flows From Investing Activities", axis=0, inplace=True, errors='ignore')
                df.drop("Cash Flows From Financing Activities", axis=0, inplace=True, errors='ignore')
                df.drop("Free Cash Flow", axis=0, inplace=True, errors='ignore')

            f = f.append(df)

        f.index = f.index.str.title()
        period_dates = (pd.to_datetime(f.columns) + pd.offsets.MonthEnd(0)).date

        # Filing date
        edgar = SecEdgarDAO()
        cik = self.lookup_cik(symbol)

        filing_dates = edgar.get_filings_dates(cik, period_dates)

        f.columns = filing_dates
        f.loc['Report Period'] = period_dates

        return f


    def lookup_cik(self, symbol):
        url = 'http://financials.morningstar.com/cmpind/company-profile/component.action?component=OperationDetails&t=%s'
        full_url = url % symbol

        df = pd.read_html(requests.get(full_url, timeout=10).text, index_col=0)[0]
        return '%010d' % df.loc['CIK']

if __name__ == "__main__":
    #symbol = 'AAPL'
    #symbol = 'TRNC'
    #symbol = 'ADXS'
    #symbol = 'YUMA'
    symbol = 'ABAC'
    dao = MorningstarDAO()
    print(dao.load_fundamentals(symbol))