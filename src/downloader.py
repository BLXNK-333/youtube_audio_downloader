import pprint
import time
from typing import Dict, Any, List, Tuple, Optional
import os
import shutil
import logging
import random

from yt_dlp import YoutubeDL

from .config.app_config import get_config
from .convertor import Convertor
from .entities import (
    AudioExt,
    Metadata
)
from .utils import (
    remove_empty_files,
    countdown_timer,
    read_user_agents
)


class Downloader:
    def __init__(self, convertor: Convertor):
        self._config = get_config()
        self._convertor = convertor
        self._logger = logging.getLogger()
        self._yt_dlp_logger = logging.getLogger('yt-dlp')

        self._write_thumbnail = self._config.download.write_thumbnail
        self._write_metadata = self._config.download.write_metadata
        self._download_directory = self._config.download.download_directory
        self._filename_format = self._config.download.filename_format

        self._delay_between_downloads = 13
        self._user_agents = read_user_agents()
        self._hook_callback: Tuple[Optional[str], Optional[str],
                            Optional[Metadata]] = (None, None, None)

    def _get_ydl_options(self, save_path: str, useragent: str) -> Dict[str, Any]:
        """
        Генерирует словарь с опциями для скачивания.

        :param save_path: Путь для сохранения скачанных файлов.
        :return: Словарь с опциями.
        """
        return {
            'format': AudioExt.BEST_,
            'outtmpl': os.path.join(save_path, 'tmp', self._filename_format),
            'writethumbnail': self._write_thumbnail,  # Загружаем миниатюры
            'writemetadata': self._write_metadata,  # Загружаем метаданные
            'progress_hooks': [self._download_complete_hook],  # Хук для обработки
            'headers': {'User-Agent': useragent},
        }

    def _download_complete_hook(self, d) -> None:
        """
        Хук, который выполняется с какой-то периодичностью во время
        скачивания файла.
        """
        if d['status'] == 'finished':
            audio_path = d['filename']
            thumbnail_path = None
            metadata = None

            # Получаем информацию о миниатюре
            if self._write_thumbnail:
                thumbnail_info = d['info_dict'].get('thumbnails', [])
                if thumbnail_info:
                    thumbnail_path = d['info_dict']['thumbnails'][-1].get('filepath')

            if self._write_metadata:
                info_dict = d['info_dict']

                # Формируем словарь с нужными метаданными
                metadata = Metadata(
                    title=info_dict.get('title'),
                    artist=info_dict.get('uploader'),  # Название канала как артист
                    album=info_dict.get('album', 'Unknown'),  # Альбом, если доступен
                    date=info_dict.get('release_year', 'Unknown'),  # Год, если доступен
                    comment=info_dict.get('webpage_url')  # Ссылка на видео
                )

            self._hook_callback = audio_path, thumbnail_path, metadata

    def _download_attempt(self, url: str, save_path: str) -> bool:
        user_agent = random.choice(self._user_agents)
        ydl_opts = self._get_ydl_options(save_path, user_agent)

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            audio_path, thumbnail_path, metadata = self._hook_callback
            self._convertor.convert(audio_path, thumbnail_path, metadata)

            if audio_path:
                os.remove(audio_path)
            if thumbnail_path:
                os.remove(thumbnail_path)
            return True

        except Exception:
            return False

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
        download_counter = playlist_length - len(urls)
        save_path = self._download_directory
        if playlist_name:
            save_path = os.path.join(save_path, playlist_name)

        try:
            _bot_block_cnt = 0
            while urls:
                print()  # Отступ для читаемости лога
                start = time.time()

                url = next(iter(urls))
                download_counter += 1
                self._logger.info(f"Loading... [{download_counter}/{playlist_length}]")

                download_result = self._download_attempt(url, save_path)
                if not download_result:
                    _bot_block_cnt += 1
                    download_counter -= 1
                else:
                    _bot_block_cnt = 0
                    urls.remove(url)

                if _bot_block_cnt == 3:
                    print()
                    self._logger.error(
                        "Your IP is in the bot block, try later or use a "
                        "cleaner VPN or proxy")
                    break  # Прерывание загрузки после блокировки бота

                rand = round(random.uniform(0, 3), 1)
                delay = self._delay_between_downloads + rand - (time.time() - start)
                if urls and delay > 0:
                    countdown_timer(delay)

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
