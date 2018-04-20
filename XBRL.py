import requests
import os
from lxml import etree


XBRL_US_API_KEY = os.environ.get('XBRL_US_API_KEY')


def lookup_cik(symbol):
    url = "https://csuite.xbrl.us/php/dispatch.php?Task=xbrlCIKLookup&Ticker=%s" % symbol
    response = requests.post(url).content
    doc = etree.fromstring(response)
    return doc.xpath("/dataRequest/tickerLookup/cik")[0].text