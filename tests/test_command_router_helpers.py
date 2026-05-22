import unittest

from friday.core.command_router import _clean_local_media_query, _youtube_result_index


class CommandRouterHelperTests(unittest.TestCase):
    def test_youtube_result_index_understands_ordinals(self) -> None:
        self.assertEqual(_youtube_result_index("play first"), 0)
        self.assertEqual(_youtube_result_index("play the second result"), 1)
        self.assertEqual(_youtube_result_index("play video number 3"), 2)

    def test_youtube_result_index_understands_next(self) -> None:
        self.assertEqual(_youtube_result_index("play next video"), 1)

    def test_local_media_query_removes_command_words(self) -> None:
        self.assertEqual(
            _clean_local_media_query("play the movie inception from my pc"),
            "inception",
        )


if __name__ == "__main__":
    unittest.main()
