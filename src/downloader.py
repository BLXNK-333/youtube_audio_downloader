import time
from typing import Dict, Any, List, Tuple, Optional
import os
import shutil
import logging

from yt_dlp import YoutubeDL

from src.config.app_config import get_config
from src.convertor import Convertor
from src.utils import remove_empty_files


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
        self._yt_dlp_logger = logging.getLogger('yt-dlp')

        self._write_thumbnail = self._config.download.write_thumbnail
        self._write_metadata = self._config.download.write_metadata
        self._audio_ext = self._config.download.audio_ext
        self._useragent = self._config.download.useragent
        self._download_directory = self._config.download.download_directory
        self._filename_format = self._config.download.filename_format

        self._hook_callback: Tuple[Optional[str], Optional[str]] = (None, None)

    def _get_ydl_options(self, save_path: str) -> Dict[str, Any]:
        """
        Генерирует словарь с опциями для скачивания.

        :param save_path: Путь для сохранения скачанных файлов.
        :return: Словарь с опциями.
        """
        return {
            'format': Downloader._quality_codes[self._audio_ext],
            'outtmpl': os.path.join(save_path, 'tmp', self._filename_format),
            'writethumbnail': self._write_thumbnail,  # Загружаем миниатюры
            'writemetadata': self._write_metadata,  # Загружаем метаданные
            'progress_hooks': [self._download_complete_hook],  # Хук для обработки
            'headers': {'User-Agent': self._useragent},
            'logger': self._yt_dlp_logger
        }

    def _download_complete_hook(self, d) -> None:
        """
        Хук, который выполняется с какой-то периодичностью во время
        скачивания файла.
        """
        if d['status'] == 'finished':
            audio_path = d['filename']
            thumbnail_path = None

            # Получаем информацию о миниатюре
            if self._write_thumbnail:
                thumbnail_info = d['info_dict'].get('thumbnails', [])
                if thumbnail_info:
                    thumbnail_path = d['info_dict']['thumbnails'][-1].get('filepath')

            self._hook_callback = audio_path, thumbnail_path

    def _create_ydl(self, save_path: str) -> YoutubeDL:
        ydl_options = self._get_ydl_options(save_path)
        return YoutubeDL(ydl_options)

    def download_links(
        self,
        urls: List[str],
        playlist_name: Optional[str] = None,
        playlist_length: int = 1
    ) -> None:
        """
        Скачивает аудио по списку из urls и сохраняет в каталоге save_path.

        :param urls: (List[str]) Список ссылок для скачивания аудио.
        :param playlist_name: (Optional[str]) Название плейлиста, если скачивается
            плейлист.
        :param playlist_length: (int) Количество элементов в плейлисте (возможно
            после фильтра), параметр нужен для логирования.
        :return: None
        """
        counter = playlist_length - len(urls)
        save_path = self._download_directory
        if playlist_name:
            save_path = os.path.join(save_path, playlist_name)

        try:
            with self._create_ydl(save_path) as ydl:
                for url in urls:
                    print()  # Так надо
                    try:
                        counter += 1
                        self._logger.info(f"Loading... [{counter}/{playlist_length}]")
                        for attempt in range(3):
                            try:
                                ydl.download([url])
                                audio_path, thumbnail_path = self._hook_callback
                                self._convertor.convert(audio_path, thumbnail_path)

                                if audio_path:
                                    os.remove(audio_path)
                                if thumbnail_path:
                                    os.remove(thumbnail_path)
                                break
                            except Exception as e:
                                self._yt_dlp_logger.warning(
                                    f"Attempt {attempt + 1}/3 failed for {url}: {e}")
                                time.sleep(1)
                                if attempt == 2:
                                    raise e
                            finally:
                                time.sleep(1)

                    except Exception as e:
                        counter -= 1
                        self._logger.warning(f"Error loading {url}: {e}")
        except KeyboardInterrupt:
            self._logger.info("Download was interrupted by the user.")
        finally:
            tmp_path = os.path.join(save_path, "tmp")
            if os.path.exists(tmp_path):
                shutil.rmtree(tmp_path)
            remove_empty_files(save_path)

    def list_available_formats(self, video_url: str) -> None:
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

    conv = Convertor()
    DL = Downloader(convertor=conv)
    DL.list_available_formats("https://www.youtube.com/watch?v=3pHjAlpLmB4")
    # DL.download_links(URLS)

    # Todo:
    #  Не для всех файлов доступно 2 формата аудио 140, 251. Иногда доступен только 1
    #  формат. Очевидно что в логику должен передаваться что то вроде {'format': 'best/bestaudio'},
    #  чтобы он сам выбирал лучший формат. Соответственно остальную логику, надо написать,
    #  как обрабатывать эти случаи. Тут по сути 2 пути: 1. Оставлять в таком же формате.
    #  2. Переконвертировать в нужный формат. Изменения затронут 2 модуля, этот и
    #  convertor.py. Нужно написать эту логику и потестить.
    #  Примеры таких видео:
    #  [
    #     "https://www.youtube.com/watch?v=3pHjAlpLmB4",
    #     "https://www.youtube.com/watch?v=yovw3SkIcjc",
    #     "https://www.youtube.com/watch?v=TsDf4sNVY9c"
    #  ]