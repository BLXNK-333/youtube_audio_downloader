import logging
from pprint import pprint

from .utils import Entity, what_entity
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
    entity = what_entity(link)
    print(entity)
    if entity == Entity.VIDEO:
        pass

    elif entity == Entity.PLAYLIST:
        # videos = AQ.get_all_playlist_videos(link)
        # pprint(videos)
        pass

    else:
        logger.warning(f"Bad link: {link}")
