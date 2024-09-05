import unittest
from src.utils import what_entity, Entity


class TestWhatEntity(unittest.TestCase):

    def test_video_url(self):
        url = "https://www.youtube.com/watch?v=abcdefghijk"
        result = what_entity(url)
        self.assertEqual(result, Entity.VIDEO)

    def test_shared_video_url(self):
        url = "https://youtu.be/ILpS4Fq3lmw?feature=shared"
        result = what_entity(url)
        self.assertEqual(result, Entity.VIDEO)

    def test_playlist_url(self):
        url = "https://www.youtube.com/playlist?list=PL1234567890abcdef"
        result = what_entity(url)
        self.assertEqual(result, Entity.PLAYLIST)

    def test_invalid_url(self):
        url = "https://www.example.com/somepage"
        result = what_entity(url)
        self.assertEqual(result, Entity.BAD_LINK)


if __name__ == "__main__":
    unittest.main()
