from typing import Optional, List, Dict
import os

from src.config.app_config import get_config
from src.entities import Snippet


class Filter:
    def __init__(self):
        self._config = get_config()
        self._download_directory = self._config.settings.download_directory

    @staticmethod
    def _convert_dict_to_obj(video_snippets: List[Dict[str, str]]) -> List[Snippet]:
        return [Snippet(
            title=item["title"],
            url=item["url"],
            published=item["published"]
        )
            for item in video_snippets
        ]

    @staticmethod
    def _convert_obj_to_list_urls(snippets_objs: List[Snippet]) -> List[str]:
        return [snippet.url for snippet in snippets_objs]

    @staticmethod
    def _filter_already_downloaded(snipped_objs: List[Snippet], directory: str):
        downloaded_names = {os.path.splitext(f)[0] for f in os.listdir(directory)
                            if os.path.isfile(os.path.join(directory, f))}
        return [sn for sn in snipped_objs if sn.title not in downloaded_names]

    def apply_filters(
            self,
            video_snippets: List[Dict[str, str]],
            playlist_name: Optional[str] = None
    ) -> List[str]:
        directory = self._download_directory
        if playlist_name:
            directory = os.path.join(directory, playlist_name)

        snipped_objs = self._convert_dict_to_obj(video_snippets)
        filtered_snippets = self._filter_already_downloaded(snipped_objs, directory)

        return self._convert_obj_to_list_urls(filtered_snippets)
