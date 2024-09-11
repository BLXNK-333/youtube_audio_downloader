import time
from typing import Dict, Any, List, Tuple, Optional
import os
import shutil
import logging

from yt_dlp import YoutubeDL

from .config.app_config import get_config
from .convertor import Convertor
from .utils import remove_empty_files
from .entities import AudioExt


def read_user_agents(filepath="user_agents.txt"):
    try:
        with open(filepath, encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"File '{filepath}' not found.")
        return []


class Downloader:
    def __init__(self, convertor: Convertor):
        self._config = get_config()
        self._convertor = convertor
        self._logger = logging.getLogger()
        self._yt_dlp_logger = logging.getLogger('yt-dlp')

        self._write_thumbnail = self._config.download.write_thumbnail
        self._write_metadata = self._config.download.write_metadata
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
            'format': AudioExt.BEST_,
            'outtmpl': os.path.join(save_path, 'tmp', self._filename_format),
            'writethumbnail': self._write_thumbnail,  # Загружаем миниатюры
            'writemetadata': self._write_metadata,  # Загружаем метаданные
            'progress_hooks': [self._download_complete_hook],  # Хук для обработки
            'headers': {'User-Agent': self._useragent}
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
                _bot_block_cnt = 0
                for url in urls:
                    print()  # Отступ для читаемости лога
                    _bot_block_cnt = 0
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
                                    f"[downloader] Attempt {attempt + 1}/3 failed for {url}")
                                if "Sign in to confirm you’re not a bot" in str(e):
                                    _bot_block_cnt += 1
                                time.sleep(1)
                                if attempt == 2:
                                    raise e
                            finally:
                                time.sleep(1)

                    except Exception as e:
                        counter -= 1
                        self._logger.error(f"Error loading {url}: \n{e}")
                        if _bot_block_cnt == 3:
                            self._logger.error(
                                "Your IP is in the bot block, use a cleaner VPN or proxy")
                            break
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
    #  При скачивании, через некоторое время попадает в бот блок, понять в чем причина,
    #  и попытаться, обойти, Возможно причина в юзерагенте. Да хз в чем.