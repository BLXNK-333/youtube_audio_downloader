import unittest

from src.entities import YoutubeLink
from src.utils import extract_type_and_id


class TestExtractIdAndType(unittest.TestCase):

    def test_video_id_extraction(self):
        url = "https://www.youtube.com/watch?v=YYwmlS8wkW0"
        expected_entity = YoutubeLink.VIDEO
        expected_id = "YYwmlS8wkW0"
        self.assertEqual(extract_type_and_id(url), (expected_entity, expected_id))

    def test_video_id_extraction_short_url(self):
        url = "https://youtu.be/YYwmlS8wkW0"
        expected_entity = YoutubeLink.VIDEO
        expected_id = "YYwmlS8wkW0"
        self.assertEqual(extract_type_and_id(url), (expected_entity, expected_id))

    def test_playlist_id_extraction(self):
        url = "https://youtube.com/playlist?list=PL-adxGZ1y-OXzOAXG5gB0pF5g5Pw7jBEG"
        expected_entity = YoutubeLink.PLAYLIST
        expected_id = "PL-adxGZ1y-OXzOAXG5gB0pF5g5Pw7jBEG"
        self.assertEqual(extract_type_and_id(url), (expected_entity, expected_id))

    def test_video_and_playlist_extraction(self):
        url = "https://www.youtube.com/watch?v=GIGJS6TJ1mY&list=PL-adxGZ1y-OXzOAXG5gB0pF5g5Pw7jBEG"
        expected_entity = YoutubeLink.VIDEO
        expected_id = "GIGJS6TJ1mY"
        self.assertEqual(extract_type_and_id(url), (expected_entity, expected_id))

    def test_bad_link(self):
        url = "https://www.youtube.com/watch?x=badlink"
        expected_entity = YoutubeLink.BAD_LINK
        expected_id = ""
        self.assertEqual(extract_type_and_id(url), (expected_entity, expected_id))


if __name__ == '__main__':
    unittest.main()
