import unittest
import json
import os
from datetime import datetime, timedelta
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from jquants_mcp_server.server import (
    search_company,
    get_daily_quotes,
    get_financial_statements,
    get_topix_prices,
    get_trades_spec
)


class TestJQuantsServer(unittest.TestCase):
    """
    Unit tests for J-Quants MCP server tools.
    Tests normal operation cases using real API calls.

    Prerequisites:
    - Either JQUANTS_REFRESH_TOKEN or both JQUANTS_MAIL_ADDRESS and JQUANTS_PASSWORD must be set
    """

    @classmethod
    def setUpClass(cls):
        """Check if authentication credentials are available"""
        refresh_token = os.environ.get('JQUANTS_REFRESH_TOKEN')
        mail_address = os.environ.get('JQUANTS_MAIL_ADDRESS')
        password = os.environ.get('JQUANTS_PASSWORD')

        if not (refresh_token or (mail_address and password)):
            raise unittest.SkipTest(
                "Either JQUANTS_REFRESH_TOKEN or both JQUANTS_MAIL_ADDRESS "
                "and JQUANTS_PASSWORD environment variables are required"
            )

    def test_search_company_toyota(self):
        """Test company search with Toyota"""
        result = search_company("トヨタ", limit=5)

        # Parse JSON response
        data = json.loads(result)

        # Should not contain error
        self.assertNotIn('error', data)

        # Should contain info array
        self.assertIn('info', data)
        self.assertIsInstance(data['info'], list)

        # Should have at least one result
        self.assertGreater(len(data['info']), 0)

        # Check if Toyota is in results
        found_toyota = any('トヨタ' in item.get('CompanyName', '') for item in data['info'])
        self.assertTrue(found_toyota, "Toyota should be found in search results")

        print(f"✅ search_company test passed: Found {len(data['info'])} companies")

    def test_get_daily_quotes_toyota(self):
        """Test daily quotes for Toyota (7203)"""
        # Use a date range that should have data (from about 3 months ago to 2 months ago)
        from_yyyymmdd = "20241001"
        to_yyyymmdd = "20241031"

        result = get_daily_quotes("72030", from_yyyymmdd, to_yyyymmdd, limit=5)

        # Parse JSON response
        data = json.loads(result)

        # Should not contain error
        self.assertNotIn('error', data)

        # Should contain daily_quotes array
        self.assertIn('daily_quotes', data)
        self.assertIsInstance(data['daily_quotes'], list)

        # Should have at least one result
        self.assertGreater(len(data['daily_quotes']), 0)

        # Check first quote has expected fields
        if data['daily_quotes']:
            quote = data['daily_quotes'][0]
            self.assertIn('Code', quote)
            self.assertEqual(quote['Code'], '72030')

        print(f"✅ get_daily_quotes test passed: Found {len(data['daily_quotes'])} quotes")

    def test_get_financial_statements_toyota(self):
        """Test financial statements for Toyota (7203)"""
        result = get_financial_statements("72030", limit=3)

        # Parse JSON response
        data = json.loads(result)

        # Should not contain error
        self.assertNotIn('error', data)

        # Should contain statements array
        self.assertIn('statements', data)
        self.assertIsInstance(data['statements'], list)

        # Should have at least one result
        self.assertGreater(len(data['statements']), 0)

        # Check first statement has expected fields
        if data['statements']:
            statement = data['statements'][0]
            self.assertIn('DisclosedDate', statement)

        print(f"✅ get_financial_statements test passed: Found {len(data['statements'])} statements")

    def test_get_topix_prices(self):
        """Test TOPIX prices retrieval"""
        # Use a date range that should have data
        from_yyyymmdd = "20241001"
        to_yyyymmdd = "20241031"

        result = get_topix_prices(from_yyyymmdd, to_yyyymmdd, limit=5)

        # Parse JSON response
        data = json.loads(result)

        # Should not contain error (unless plan restriction)
        if 'error' in data:
            # If this is a plan restriction, skip the test
            if 'plan' in data.get('status', '').lower():
                self.skipTest("TOPIX data requires higher plan level")
            else:
                self.fail(f"Unexpected error: {data['error']}")

        # Should contain topix array
        self.assertIn('topix', data)
        self.assertIsInstance(data['topix'], list)

        # Should have at least one result
        self.assertGreater(len(data['topix']), 0)

        # Check first entry has expected fields
        if data['topix']:
            topix = data['topix'][0]
            self.assertIn('Date', topix)

        print(f"✅ get_topix_prices test passed: Found {len(data['topix'])} TOPIX entries")

    def test_get_trades_spec_by_section(self):
        """Test trading by type of investors with section parameter"""
        # Test with TSEPrime section and date range
        from_yyyymmdd = "20241001"
        to_yyyymmdd = "20241031"

        result = get_trades_spec(section="TSEPrime", from_yyyymmdd=from_yyyymmdd, to_yyyymmdd=to_yyyymmdd, limit=5)

        # Parse JSON response
        data = json.loads(result)

        # Should not contain error (unless plan restriction or API unavailable)
        if 'error' in data:
            # Check for various error types that should be skipped
            error_msg = data.get('error', '').lower()
            status_code = data.get('status', '')

            if ('plan' in status_code.lower() or 
                'ステータスコード: 400' in data.get('error', '') or
                'ステータスコード: 403' in data.get('error', '')):
                self.skipTest("Trading by type of investors data may require higher plan level or is currently unavailable")
            else:
                self.fail(f"Unexpected error: {data['error']}")

        # Should contain trades_spec array
        self.assertIn('trades_spec', data)
        self.assertIsInstance(data['trades_spec'], list)

        # Should have at least one result
        self.assertGreater(len(data['trades_spec']), 0)

        # Check first entry has expected fields
        if data['trades_spec']:
            trades = data['trades_spec'][0]
            self.assertIn('Section', trades)
            self.assertIn('StartDate', trades)
            self.assertIn('EndDate', trades)

        print(f"✅ get_trades_spec test passed: Found {len(data['trades_spec'])} trading records")


if __name__ == '__main__':
    unittest.main(verbosity=2)
