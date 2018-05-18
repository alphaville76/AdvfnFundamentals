from unittest import TestCase
from XBRL import lookup_cik
from XBRL import lookup_cik_by_name

class XBRLTest(TestCase):


    def test_lookup_cik(self):
        self.assertEqual('0000051143', lookup_cik('IBM'))

    def test_lookup_cik_by_name(self):
        self.assertEqual(['0001672326', '0000081318', '0001524071'], lookup_cik_by_name('Yuma Energy, Inc.'))
        self.assertEqual(['0000822411'], lookup_cik_by_name('ImmunoCellular Therapeutics, Ltd.'))

