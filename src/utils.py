import re
from typing import Tuple
import logging

from .entities import YoutubeLink, AudioExt


logger = logging.getLogger()


def extract_type_and_id(url: str) -> Tuple[str, str]:
    """
    Находит id видео или плейлиста и возвращает его.

    :param url: (str) Url, который передал пользователь.
    :return: Возвращает кортеж (паттерн: str, id: str)
    """

    video_pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    playlist_pattern = r"(?:list=)([0-9A-Za-z_-]{13,})"

    video_match = re.search(video_pattern, url)
    playlist_match = re.search(playlist_pattern, url)

    if video_match:
        return YoutubeLink.VIDEO, video_match.group(1)
    elif playlist_match:
        return YoutubeLink.PLAYLIST, playlist_match.group(1)
    else:
        return YoutubeLink.BAD_LINK, ""


def validate_audio_format(output_format: str):
    supported_formats = {AudioExt.OGG, AudioExt.M4A, AudioExt.MP3}
    if output_format not in supported_formats:
        logger.error(
            f"\n End audio container not supported: {output_format}\n"
            f" Use AUDIO_EXT=[{'|'.join(supported_formats)}] in settings")
        return False
    return True
