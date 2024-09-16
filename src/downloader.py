import time
from typing import Dict, Any, List, Optional
import os
import shutil
import logging
import random

from yt_dlp import YoutubeDL

from .config.app_config import get_config
from .converter.converter import Converter
from .entities import DownloadCallback, Metadata
from .utils import (
    remove_empty_files,
    countdown_timer,
    read_user_agents
)


class Downloader:
    def __init__(self, convertor: Converter):
        self._config = get_config()
        self._converter = convertor
        self._logger = logging.getLogger()
        self._yt_dlp_logger = logging.getLogger('yt-dlp')

        self._write_thumbnail = self._config.download.write_thumbnail
        self._write_metadata = self._config.download.write_metadata
        self._download_directory = self._config.download.download_directory
        self._filename_format = self._config.download.filename_format

        self._delay_between_downloads = 13
        self._user_agents = read_user_agents()
        self._hook_callback: Optional[DownloadCallback] = None

    def _get_ydl_options(self, save_path: str, useragent: str) -> Dict[str, Any]:
        """
        Генерирует словарь с опциями для скачивания.

        :param save_path: Путь для сохранения скачанных файлов.
        :return: Словарь с опциями.
        """

        # Генерируем случайный лимит от 300 до 800 KB/s
        random_ratelimit = random.randint(300, 800) * 1024

        ydl_opts = {
            'format': "bestaudio/best",
            'outtmpl': os.path.join(save_path, 'tmp', self._filename_format),
            'progress_hooks': [self._download_complete_hook],  # Хук для обработки
            'headers': {'User-Agent': useragent},
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',  # Извлекаем аудио
            }],
            'writethumbnail': self._write_thumbnail,  # Загружаем миниатюры
            'whritemetadata': self._write_metadata,  # Загружаем метаданные
            'ratelimit': random_ratelimit
        }

        return ydl_opts

    def _download_complete_hook(self, d) -> None:
        """
        Хук, который выполняется с какой-то периодичностью во время
        скачивания файла.
        """
        if d['status'] == 'finished':
            callback = DownloadCallback(
                audio_path="",
                thumbnail_path="",
                metadata=Metadata(title="", artist="", date="", comment=""),
                bitrate_check=True
            )

            format_id = d['info_dict']['format_id']
            format_dict = {'251': 'opus', '140': 'm4a'}
            if format_id not in format_dict:
                callback.bitrate_check = False

            callback.audio_path = (os.path.splitext(d['filename'])[0] +
                                   "." + format_dict[format_id])

            # Получаем информацию о миниатюре
            if self._write_thumbnail:
                thumbnail_info = d['info_dict'].get('thumbnails', [])
                if thumbnail_info:
                    callback.thumbnail_path = d['info_dict']['thumbnails'][-1].get(
                        'filepath')

            if self._write_metadata and callback.metadata:
                info_dict = d['info_dict']

                # Формируем словарь с нужными метаданными
                callback.metadata.title = info_dict.get('title', '')
                callback.metadata.artist = info_dict.get('uploader', '')
                callback.metadata.date = info_dict.get('upload_date', '')
                callback.metadata.comment = info_dict.get('webpage_url', '')

            self._hook_callback = callback

    def _download_attempt(self, url: str, save_path: str) -> bool:
        user_agent = random.choice(self._user_agents)
        ydl_opts = self._get_ydl_options(save_path, user_agent)

        try:
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])

            callback = self._hook_callback
            if callback is None:
                self._yt_dlp_logger.warning(f"[*downloader] Callback did not return.")
                return False

            if callback.bitrate_check:
                assert isinstance(callback.metadata, Metadata)
                self._converter.convert(
                    callback.audio_path,
                    callback.thumbnail_path,
                    callback.metadata
                )
            else:
                self._yt_dlp_logger.warning(
                    f"[*downloader] Skipped because the audio bitrate is too low.")

            if callback.audio_path:
                os.remove(callback.audio_path)
            if callback.thumbnail_path:
                os.remove(callback.thumbnail_path)
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
