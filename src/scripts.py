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
    entity, entity_id = extract_type_and_id(link)

    if not validate_audio_format(config.settings.audio_ext):
        return

    if not validate_date_filter(config.settings.filter_date):
        return

    query = ApiQuery()
    _filter = Filter()
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
