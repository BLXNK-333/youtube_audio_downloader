import logging
from pprint import pprint

from .utils import Entity, extract_type_and_id
from .api_query import ApiQuery
PLAYLIST_ID = 'PL-adxGZ1y-OXzOAXG5gB0pF5g5Pw7jBEG'


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

    if entity == Entity.VIDEO:
        pass

    elif entity == Entity.PLAYLIST:
        videos = AQ.get_all_playlist_videos("PL-adxGZ1y-OXzOAXG5gB0pF5g5Pw7jBEG")
        pprint(videos)
        pass

    else:
        logger.warning(f"Bad link: {link}")
