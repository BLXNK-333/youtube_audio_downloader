import os
from yt_dlp import YoutubeDL

from src.config.app_config import get_config


class Downloader:
    _quality_codes = {
        "ogg": "251",
        "m4a": "140",
        "mp3": "251"
    }

    def __init__(self):
        self._config = get_config()
        self._write_thumbnail = self._config.settings.write_thumbnail
        self._write_metadata = self._config.settings.write_metadata
        self._download_directory = self._config.settings.download_directory
        self._audio_ext = self._config.settings.audio_ext
        self._useragent = self._config.settings.useragent
        self._filename_format = self._config.settings.filename_format

    def _download_audio(self, url: str, save_path):
        # Убедитесь, что директория существует
        os.makedirs(save_path, exist_ok=True)
        ydl_options = {
            'format': Downloader._quality_codes[self._audio_ext],
            'outtmpl': os.path.join(save_path, self._filename_format),
            'writethumbnail': self._write_thumbnail,  # Загружаем миниатюры
            'writemetadata': self._write_metadata,  # Загружаем метаданные
            'headers': {'User-Agent': self._filename_format},
        }

        with YoutubeDL(ydl_options) as ydl:
            ydl.download([url])

    def _download_playlist(self):
        pass

    def list_formats(self, video_url):
        ydl_opts = {
            'listformats': True
            # Эта опция выводит список всех доступных форматов, но не скачивает видео
        }

        with YoutubeDL(ydl_opts) as ydl:
            ydl.extract_info(video_url, download=False)


if __name__ == '__main__':
    # Ссылка на плейлист
    # playlist_url = 'https://www.youtube.com/playlist?list=PL-adxGZ1y-OXzOAXG5gB0pF5g5Pw7jBEG'

    # Ссылка на плейлист
    # url = "https://www.youtube.com/watch?v=U-xw6e-62fw"
    url = "https://www.youtube.com/watch?v=YYwmlS8wkW0"
    save_dir = "/home/blxnk/Downloads/yt_downloader"
    dl = Downloader()
    try:
        dl._download_audio(url, save_dir)
    except Exception as e:
        print(e)

    # url = "https://www.youtube.com/watch?v=U-xw6e-62fw"
    # list_formats(url)

