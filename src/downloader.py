import os
from typing import Dict, Any, List
import logging

from yt_dlp import YoutubeDL

from src.config.app_config import get_config
from src.convertor import Convertor


class Downloader:
    _quality_codes = {
        "ogg": "251",
        "m4a": "140",
        "mp3": "251"
    }

    def __init__(self, convertor: Convertor):
        self._config = get_config()
        self._convertor = convertor
        self._logger = logging.getLogger()

        self._write_thumbnail = self._config.settings.write_thumbnail
        self._write_metadata = self._config.settings.write_metadata
        self._download_directory = self._config.settings.download_directory
        self._audio_ext = self._config.settings.audio_ext
        self._useragent = self._config.settings.useragent
        self._filename_format = self._config.settings.filename_format

    def _get_ydl_options(self, save_path: str) -> Dict[str, Any]:
        """
        Генерирует словарь с опциями для скачивания.

        :param save_path: Путь для сохранения скачанных файлов.
        :return: Словарь с опциями.
        """
        return {
            'format': Downloader._quality_codes[self._audio_ext],
            'outtmpl': os.path.join(save_path, self._filename_format),
            'writethumbnail': self._write_thumbnail,  # Загружаем миниатюры
            'writemetadata': self._write_metadata,  # Загружаем метаданные
            'headers': {'User-Agent': self._filename_format},
        }

    def _create_ydl(self, save_path: str) -> YoutubeDL:
        _tmp = os.path.join(save_path, "tmp")
        ydl_options = self._get_ydl_options(save_path)
        return YoutubeDL(ydl_options)

    def download_links(self, urls: List[str], save_path: str, counter: int = 0) -> None:
        """
        Скачивает аудио по списку из urls и сохраняет в каталоге save_path.

        :param urls: (List[str]) Список ссылок по которым нужно скачать аудио.
        :param save_path: (str) Конечный каталог для сохранения.
        :param counter: (int) Число с которого начнется счетчик загрузок,
            нужен для логов.
        :return: None
        """
        ydl = self._create_ydl(save_path)
        n = counter + len(urls)

        for url in urls:
            try:
                counter += 1
                self._logger.info(f"Loading... [{counter}/{n}]")
                ydl.download([url])
            except Exception as e:
                self._logger.warning(f"Error loading {url}: {e}")

    def list_formats(self, video_url: str) -> None:
        """
        Выводит список всех доступных форматов, но не скачивает видео.

        :param video_url: (str) Ссылка на видео.
        :return: None
        """
        ydl_opts = {'listformats': True}

        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=False)


if __name__ == '__main__':
    URLS = [
        "https://www.youtube.com/watch?v=U-xw6e-62fw"
    ]
    SAVE_DIR = "/home/blxnk/Downloads/YouTube"

    conv = Convertor()
    DL = Downloader(convertor=conv)
    DL.download_links(URLS, SAVE_DIR)
