from unittest import TestCase
from SecEdgarDAO import SecEdgarDAO
import datetime
from XBRL import lookup_cik
from MorningstarDAO import MorningstarDAO


class SecEdgarDAOTest(TestCase):

    def __init__(self, methodName='runTest'):
        super().__init__(methodName)
        self.dao = SecEdgarDAO()

    def test_get_filings_dates(self):
        cik = '0000051143' # IBM
        results = self.dao.get_filings_dates(cik)

        print(results)
        self.assertEqual(10, len(results))

    def test_get_filings_dates2(self):
        cik = '0000051143'  # IBM
        period_dates = [datetime.date(2017, 3, 31),
        datetime.date(2017, 6, 30),
        datetime.date(2017, 9, 30),
        datetime.date(2017, 12, 31),
        datetime.date(2018, 3, 31)]
        results = self.dao.get_filings_dates(cik, period_dates)

        print(results)
        self.assertEqual(5, len(results))


    def test_get_shares_outstanding(self):
        cik = '0001593195' # TRNC
        results = self.dao.get_shares_outstanding(cik)

        print(results)
        self.assertEqual(10, len(results))
