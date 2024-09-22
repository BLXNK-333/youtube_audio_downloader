import unittest
from src.utils import normalize_string


class TestNormalizeString(unittest.TestCase):

    def test_replacements(self):
        # Проверяем замену специальных символов
        self.assertEqual(normalize_string('｜｜DILIP｜｜ x Tibe - Ventilate'),
                         '??DILIP?? x Tibe - Ventilate')
        self.assertEqual(normalize_string('DILIP - *laughing emoji*'),
                         'DILIP - ?laughing emoji?')
        self.assertEqual(normalize_string('DILIP - ＊laughing emoji＊'),
                         'DILIP - ?laughing emoji?')
        self.assertEqual(normalize_string('DEIRYN - E t e r n a l / L u c i d'),
                         'DEIRYN - E t e r n a l ? L u c i d')

    def test_multiple_spaces(self):
        # Проверяем замену пробелов
        self.assertEqual(normalize_string('DILIP    -  *laughing emoji*'),
                         'DILIP - ?laughing emoji?')
        self.assertEqual(normalize_string('DILIP    -  ＊laughing emoji＊'),
                         'DILIP - ?laughing emoji?')

    def test_combined_cases(self):
        # Проверяем комбинированные случаи
        self.assertEqual(normalize_string('｜｜DILIP｜｜ x Tibe - *laughing emoji*'),
                         '??DILIP?? x Tibe - ?laughing emoji?')
        self.assertEqual(normalize_string('DILIP - ||laughing emoji||'),
                         'DILIP - ??laughing emoji??')

    def test_empty_string(self):
        # Проверяем пустую строку
        self.assertEqual(normalize_string(''), '')

    def test_only_special_characters(self):
        # Проверяем строку только со специальными символами
        self.assertEqual(normalize_string('｜｜/⧸*＊☆★•⁕•'), '???????????')


if __name__ == '__main__':
    unittest.main()
