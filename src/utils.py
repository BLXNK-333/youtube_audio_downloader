import os
import sys
import time
import re
from typing import Tuple

from .entities import YoutubeLink


def extract_type_and_id(url: str) -> Tuple[str, str]:
    """
    Находит id видео или плейлиста и возвращает его.

    :param url: (str) Url, который передал пользователь.
    :return: Возвращает кортеж (паттерн: str, id: str)
    """

    video_pattern = r"(?:v=|\/)([0-9A-Za-z_-]{11})"
    playlist_pattern = r"(?:list=)([0-9A-Za-z_-]{13,})"
    channel_pattern = r"@[\S]+"

    video_match = re.search(video_pattern, url)
    playlist_match = re.search(playlist_pattern, url)
    channel_match = re.search(channel_pattern, url)

    if video_match:
        return YoutubeLink.VIDEO, video_match.group(1)
    elif playlist_match:
        return YoutubeLink.PLAYLIST, playlist_match.group(1)
    elif channel_match:
        return YoutubeLink.CHANNEL, channel_match.group(0)
    else:
        return YoutubeLink.BAD_LINK, ""


def remove_empty_files(directory: str) -> None:
    """
    Удаляет все файлы размером 0 байт в указанном каталоге и его подкаталогах.

    :param directory: (str) Путь к каталогу, в котором нужно удалить пустые файлы.
    """

    for root, dirs, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            if os.path.getsize(file_path) == 0:
                os.remove(file_path)


def countdown_timer(delay: float) -> None:
    """
    Displays a countdown timer in stdout, updating in the same line.

    :param delay: Waiting time in seconds.
    :return: None
    """
    try:
        interval = 0.1  # Update interval in seconds
        steps = int(delay / interval)

        for remaining in range(steps, 0, -1):
            time_left = remaining * interval
            sys.stdout.write(f"\rNext download in {time_left:.1f} seconds...")
            sys.stdout.flush()
            time.sleep(interval)

    finally:
        # Clear the timer after completion
        sys.stdout.write("\r" + " " * 50 + "\r")
        sys.stdout.flush()


def read_user_agents(filepath="user_agents.txt"):
    try:
        with open(filepath, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File '{filepath}' not found.")
        return []
