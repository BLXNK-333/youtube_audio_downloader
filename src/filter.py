from typing import Optional, List, Dict
import re
import os
import logging
from datetime import datetime

from src.config.app_config import get_config
from src.entities import Snippet


class Filter:
    def __init__(self):
        self._config = get_config()
        self._logger = logging.getLogger()
        self._filter_date = self._config.settings.filter_date
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

    def _filter_by_download_date(self, snippet_objs: List[Snippet]) -> List[Snippet]:
        filter_date = re.sub(r"[\[\]\s]", "", self._filter_date).lower()

        def filter_func(snippet: Snippet) -> bool:
            try:
                # Преобразуем дату публикации в год
                publication_year = datetime.strptime(snippet.published,
                                                     "%Y-%m-%dT%H:%M:%SZ").year
                # Формируем условие фильтрации и оцениваем его
                return eval(filter_date.replace("x", str(publication_year)))
            except (ValueError, SyntaxError) as e:
                self._logger.debug(
                    f"An error occurred when trying to apply a date filter "
                    f"to an expression:\n {e}"
                    f"\n title: {snippet.title}"
                    f"\n published: {snippet.published}"
                )
                return False

        return [sn for sn in snippet_objs if filter_func(sn)]

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
        filtered_snippets = self._filter_by_download_date(filtered_snippets)

        return self._convert_obj_to_list_urls(filtered_snippets)
