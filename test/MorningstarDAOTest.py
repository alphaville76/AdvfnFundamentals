from unittest import TestCase
from MorningstarDAO import MorningstarDAO


class MorningstarDAOTest(TestCase):

    def test_load_fundamentals(self):
        symbol = 'IBM'

        dao = MorningstarDAO()
        df = dao.load_fundamentals(symbol)

        EXPECTED = ['Cash And Cash Equivalents', 'Short-Term Investments', 'Total Cash',
                    'Receivables', 'Inventories', 'Prepaid Expenses',
                    'Other Current Assets', 'Total Current Assets',
                    'Gross Property, Plant And Equipment', 'Accumulated Depreciation',
                    'Net Property, Plant And Equipment', 'Equity And Other Investments',
                    'Goodwill', 'Intangible Assets', 'Deferred Income Taxes',
                    'Prepaid Pension Benefit', 'Other Long-Term Assets',
                    'Total Non-Current Assets', 'Total Assets', 'Short-Term Debt',
                    'Accounts Payable', 'Taxes Payable', 'Current Deferred Revenues',
                    'Other Current Liabilities', 'Total Current Liabilities',
                    'Long-Term Debt', 'Deferred Taxes Liabilities', 'Accrued Liabilities',
                    'Non-Current Deferred Revenues', 'Pensions And Other Benefits',
                    'Minority Interest', 'Other Long-Term Liabilities',
                    'Total Non-Current Liabilities', 'Total Liabilities', 'Common Stock',
                    'Retained Earnings', 'Treasury Stock',
                    'Accumulated Other Comprehensive Income', "Total Stockholders' Equity",
                    "Total Liabilities And Stockholders' Equity", 'Revenue',
                    'Cost Of Revenue', 'Gross Profit', 'Research And Development',
                    'Sales, General And Administrative', 'Other Operating Expenses',
                    'Total Operating Expenses', 'Operating Income', 'Interest Expense',
                    'Other Income (Expense)', 'Income Before Taxes',
                    'Provision For Income Taxes', 'Other Income',
                    'Net Income From Continuing Operations',
                    'Net Income From Discontinuing Ops', 'Other', 'Net Income',
                    'Net Income Available To Common Shareholders',
                    'Earnings Per Share Basic', 'Earnings Per Share Diluted',
                    'Weighted Average Shares Outstanding Basic',
                    'Weighted Average Shares Outstanding Diluted', 'Ebitda',
                    'Depreciation & Amortization', 'Stock Based Compensation',
                    'Change In Working Capital', 'Other Working Capital',
                    'Other Non-Cash Items', 'Net Cash Provided By Operating Activities',
                    'Investments In Property, Plant, And Equipment',
                    'Property, Plant, And Equipment Reductions', 'Acquisitions, Net',
                    'Purchases Of Investments', 'Sales/Maturities Of Investments',
                    'Purchases Of Intangibles', 'Other Investing Activities',
                    'Net Cash Used For Investing Activities', 'Debt Issued',
                    'Debt Repayment', 'Common Stock Repurchased', 'Dividend Paid',
                    'Other Financing Activities',
                    'Net Cash Provided By (Used For) Financing Activities',
                    'Effect Of Exchange Rate Changes', 'Net Change In Cash',
                    'Cash At Beginning Of Period', 'Cash At End Of Period',
                    'Operating Cash Flow', 'Capital Expenditure', 'Free Cash Flow', 'Report Period']

        self.assertListEqual(EXPECTED, list(df.index.values))