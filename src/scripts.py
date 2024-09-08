import logging
from pprint import pprint

from .entities import YoutubeLink
from .utils import extract_type_and_id, validate_audio_format
from .api_query import ApiQuery
from .convertor import Convertor
from .downloader import Downloader
from .config.app_config import get_config


logger = logging.getLogger()


def download_audio(link: str):
    """
    Скачивает аудио или все аудио из плейлиста, в соответствии с
    настройками в конфигурации.

    :param link: Ссылка на видео или плейлист.
    :return: None
    """
    config = get_config()
    entity, entity_id = extract_type_and_id(link)

    if not validate_audio_format(config.settings.audio_ext):
        return

    query = ApiQuery()
    convertor = Convertor()
    DL = Downloader(convertor=convertor)

    if entity == YoutubeLink.VIDEO:
        # DL.download_links()
        pass

    elif entity == YoutubeLink.PLAYLIST:
        # videos = AQ.get_all_playlist_videos(entity_id)
        # pprint(videos)
        pass

    else:
        logger.warning(f"Bad link: {link}")
