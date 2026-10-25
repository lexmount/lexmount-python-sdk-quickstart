import os
import unittest
from unittest.mock import patch

from demo import target_site


class DemoTests(unittest.TestCase):
    def test_target_site_matches_the_configured_api_environment(self):
        with patch.dict(os.environ, {"LEXMOUNT_BASE_URL": "https://api.lexmount.com"}):
            self.assertEqual(target_site(), "https://browser.lexmount.com/")
        with patch.dict(os.environ, {"LEXMOUNT_BASE_URL": "https://api.lexmount.cn/"}):
            self.assertEqual(target_site(), "https://browser.lexmount.cn/")


if __name__ == "__main__":
    unittest.main()
