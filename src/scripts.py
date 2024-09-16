import logging

from .entities import YoutubeLink
from .api_query import ApiQuery
from .converter.converter import Converter
from .downloader import Downloader
from .filter import Filter
from .utils import extract_type_and_id
from .validator import validate_settings


logger = logging.getLogger()


def download_audio(link: str):
    """
    Скачивает аудио или все аудио из плейлиста, в соответствии с
    настройками в конфигурации.

    :param link: Ссылка на видео или плейлист.
    :return: None
    """
    try:
        if not validate_settings():
            return

        link, link_id = extract_type_and_id(link)

        query = ApiQuery()
        _filter = Filter()
        convertor = Converter()
        DL = Downloader(convertor=convertor)

        if link == YoutubeLink.VIDEO:
            # Скрипт для скачивания аудио из ссылки на видео.
            snippets = query.get_video_details(link_id)
            filtered_snippets, len_snippets = _filter.apply_filters(
                snippets,
                filter_date=False
            )
            DL.download_links(filtered_snippets)

        elif link == YoutubeLink.PLAYLIST:
            # Скрипт для скачивания аудио из ссылки на плейлист.
            playlist_name = query.get_playlist_title(link_id)
            snippets = query.get_playlist_videos_details(link_id)
            filtered_snippets, len_snippets = _filter.apply_filters(
                snippets,
                playlist_name=playlist_name
            )
            DL.download_links(
                urls=filtered_snippets,
                playlist_name=playlist_name,
                playlist_length=len_snippets
            )

        else:
            logger.warning(f"Bad link: {link}")

    except KeyboardInterrupt:
        logger.info("Download was interrupted by the user.")
