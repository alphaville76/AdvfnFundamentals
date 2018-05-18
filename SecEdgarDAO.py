import feedparser
import requests
import zipfile
import io
from lxml import etree
import pandas as pd
from LogUtil import create_logger
import socket
import calendar
import datetime

from LogUtil import create_logger

log = create_logger('SecEdgarDAO')

socket.setdefaulttimeout(10) # 10 seconds


class SecEdgarDAO(object):

    def __init__(self):
        self.url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=%s&type=%s&owner=exclude&start=0&count=%d&output=atom"

    def _normalise_date(self, date):
        last_day_of_month = calendar.monthrange(date.year, date.month)[1]
        if last_day_of_month != date.day:
            if date.day <= 15:
                new_month = date.month - 1 if date.month > 1 else 12
                new_day = calendar.monthrange(date.year, new_month)[1]
                new_year = date.year if new_month != 12 else date.year - 1
                date = datetime.date(new_year, new_month, new_day)
            else:
                date = datetime.date(date.year, date.month, last_day_of_month)
        return date


    def _load_filings_single(self, cik, ignore_amended=False):
        full_url = self.url % (cik, "10-", 20)
        feed = feedparser.parse(full_url)
        if len(feed.entries) == 0:
            raise ValueError("No filing '10-Q' or '10-K' found")

        date_dict = {}
        for entry in feed.entries:
            filing_type = entry['filing-type'].upper()
            # skip amended
            if ignore_amended and filing_type not in ['10-Q', '10-K']:
                continue
            href = entry['filing-href']
            filing_date = entry['filing-date']
            folder = href[0:href.rfind('/')]
            summary = folder + '/FilingSummary.xml'

            doc = etree.fromstring(requests.get(summary, stream=True, timeout=10).content)
            try:
                xbrl_file = doc.xpath("/FilingSummary/MyReports/Report")[0].attrib['instance']
            except IndexError as e:
                # FilingSummary.xml not available
                continue
            except KeyError as e:
                url = folder + '/index.xml'
                response = requests.get(url, stream=True, timeout=10)
                doc = etree.fromstring(response.content)
                for elem in doc.iter('name'):
                    name = elem.text
                    if name.endswith('.xsd'):
                        xbrl_file = name.replace('.xsd', '.xml')
                        break

            xbrl_file = xbrl_file.replace('.htm', '_htm.xml')

            tree = etree.fromstring(requests.get(folder + '/' + xbrl_file, stream=True, timeout=10).content)

            ns_xbrli = {'xbrli': 'http://www.xbrl.org/2003/instance'}

            shares_outstanding_node = tree.find("dei:EntityCommonStockSharesOutstanding", tree.nsmap)
            shares_outstanding_value = shares_outstanding_node.text
            context_ref_id = shares_outstanding_node.attrib['contextRef']
            instant = tree.find(
                "xbrli:context[@id = '%s']/xbrli:period/xbrli:instant" % context_ref_id, ns_xbrli)
            end_period = tree.find("dei:DocumentPeriodEndDate", tree.nsmap).text
            end_period_date = pd.to_datetime(end_period).date()
            norm_end_period_date = self._normalise_date(end_period_date)
            date_dict[norm_end_period_date] = {'xbrl_file': xbrl_file,
                                               'filing_type': filing_type,
                                               'filing_date': filing_date,
                                               'end_period': end_period,
                                               'shares_outstanding': shares_outstanding_value,
                                               'shares_outstanding_date': instant.text}

        return date_dict


    def _load_filings(self, ciks, ignore_amended=False):
        if isinstance(ciks, str):
            return self._load_filings_single(ciks, ignore_amended)

        date_dict = {}
        for cik in ciks:
            try:
                date_dict.update(self._load_filings_single(cik, ignore_amended))
            except:
                continue

        if len(date_dict) == 0:
            raise ValueError("No filing '10-Q' or '10-K' found")

        return date_dict


    def get_filings_dates(self, ciks, period_dates=None, ignore_amended=True):
        date_dict = self._load_filings(ciks, ignore_amended=ignore_amended)
        if period_dates is None:
            period_dates = date_dict.keys()

        try:
            return [date_dict[x]['filing_date'] for x in period_dates]
        except KeyError as e:
            raise KeyError("Not all %s in %s" % (period_dates, date_dict.keys()))

    def get_shares_outstanding(self, ciks):
        date_dict = self._load_filings(ciks)
        return {date_dict[end_period]['shares_outstanding_date']: date_dict[end_period]['shares_outstanding'] for
                end_period in date_dict.keys()}


if __name__ == "__main__":
    dao = SecEdgarDAO()
    #cik = '0001593195' # TRNC
    #cik = '0001341439'  # AAPL
    cik = '0001143513' #GLAD
    #ciks = ['0001672326', '0000081318', '0001524071'] #YUMA
    #print(dao.get_filings_dates(cik))

    print(dao._load_filings(cik))
