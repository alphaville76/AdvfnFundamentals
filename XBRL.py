import requests
import os
from lxml import etree
import feedparser
from requests.utils import quote

XBRL_US_API_KEY = os.environ.get('XBRL_US_API_KEY')


def lookup_cik(symbol):
    url = "https://csuite.xbrl.us/php/dispatch.php?Task=xbrlCIKLookup&Ticker=%s" % symbol
    response = requests.post(url, timeout=10).content
    doc = etree.fromstring(response)
    return doc.xpath("/dataRequest/tickerLookup/cik")[0].text


def lookup_cik_by_name(name):
    url = 'https://www.sec.gov/cgi-bin/browse-edgar?company=%s&match=contains&owner=exclude&action=getcompany&output=atom'
    name = name.replace(',','')
    name = name.replace('.', '')
    full_url = url % quote(name)

    atom = feedparser.parse(full_url)
    if 'cik' in atom.feed:
        return [atom.feed.cik]

    results = [entry['cik'] for entry in atom.entries]
    results.reverse()
    return results

if __name__ == "__main__":
    name = 'Yuma Energy, Inc.'
    print(lookup_cik_by_name(name))