import unittest
import logging

from src.validator import validate_date_filter

logger = logging.getLogger()
logger.disabled = True


class TestValidateDateFilter(unittest.TestCase):

    def test_valid_filters(self):
        self.assertTrue(validate_date_filter("2017 < x <= 2024"))
        self.assertTrue(validate_date_filter("x == 2020"))
        self.assertTrue(validate_date_filter("x in {2017, 2019, 2023}"))
        self.assertTrue(validate_date_filter(""))
        self.assertTrue(validate_date_filter("(2017 < x) or (x == 2020)"))

    def test_invalid_characters(self):
        self.assertFalse(validate_date_filter("2017 < y <= 2024"))  # недопустимый символ 'y'
        self.assertFalse(validate_date_filter("2017 < x < 2024#"))  # недопустимый символ '#'
        self.assertFalse(validate_date_filter("2017 < x < 2024$"))  # недопустимый символ '$'

    def test_invalid_syntax(self):
        self.assertFalse(validate_date_filter("2017 < x <="))       # неполное выражение
        self.assertFalse(validate_date_filter("x =="))              # неполное выражение
        self.assertFalse(validate_date_filter("in {2017, 2019}"))   # неполное выражение

    def test_filter_too_long(self):
        long_filter = "x == 2020" + " and x == 2020" * 20
        self.assertFalse(validate_date_filter(long_filter))

    def test_case_insensitivity(self):
        self.assertTrue(validate_date_filter("x In {2017, 2019, 2023}"))
        self.assertTrue(validate_date_filter("(2017 < x) OR (x == 2020)"))


if __name__ == '__main__':
    unittest.main()
