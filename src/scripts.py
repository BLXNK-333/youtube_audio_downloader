import logging
from pprint import pprint

from .entities import YoutubeLink
from .utils import extract_type_and_id
from .api_query import ApiQuery


logger = logging.getLogger()


def download_audio(link: str):
    """
    Скачивает аудио или все аудио из плейлиста, в соответствии с
    настройками в конфигурации.

    :param link: Ссылка на видео или плейлист.
    :return: None
    """
    AQ = ApiQuery()
    entity, entity_id = extract_type_and_id(link)

    if entity == YoutubeLink.VIDEO:
        pass

    elif entity == YoutubeLink.PLAYLIST:
        videos = AQ.get_all_playlist_videos(entity_id)
        pprint(videos)
        pass

    else:
        logger.warning(f"Bad link: {link}")
