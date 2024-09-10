import logging

from .config.app_config import get_config
from .entities import YoutubeLink
from .api_query import ApiQuery
from .convertor import Convertor
from .downloader import Downloader
from .filter import Filter
from .utils import extract_type_and_id
from .validator import validate_audio_format, validate_date_filter


logger = logging.getLogger()


def download_audio(link: str):
    """
    Скачивает аудио или все аудио из плейлиста, в соответствии с
    настройками в конфигурации.

    :param link: Ссылка на видео или плейлист.
    :return: None
    """
    config = get_config()
    link, link_id = extract_type_and_id(link)

    if not validate_audio_format(config.settings.audio_ext):
        return

    if not validate_date_filter(config.settings.filter_date):
        return

    query = ApiQuery()
    _filter = Filter()
    convertor = Convertor()
    DL = Downloader(convertor=convertor)

    if link == YoutubeLink.VIDEO:
        snippets = query.get_video_details(link_id)
        filtered_snippets, len_snippets = _filter.apply_filters(
            snippets,
            filter_date=False
        )
        DL.download_links(filtered_snippets)

    elif link == YoutubeLink.PLAYLIST:
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
