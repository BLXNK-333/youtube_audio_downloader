import os
import subprocess
import logging
from typing import Optional

from PIL import Image
from PIL.Image import Resampling
from io import BytesIO

from .config.app_config import get_config


class Convertor:
    _codec_map = {
        "ogg": ("copy", "libtheora"),
        "m4a": ("copy", "mjpeg"),
        "mp3": ("libmp3lame", "mjpeg"),
    }

    def __init__(self):
        self._config = get_config()
        self._logger = logging.getLogger()
        self._audio_ext = self._config.settings.audio_ext
        self._resize = self._config.settings.thumbnail_resize
        self._max_width = self._config.settings.thumbnail_max_width

    def _convert_image(self, image_path: str) -> BytesIO:
        with Image.open(image_path) as img:
            if self._resize:
                img.thumbnail((self._max_width, self._max_width), Resampling.LANCZOS)

            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='WEBP')
            img_byte_arr.seek(0)
            return img_byte_arr

    def _execute_ffmpeg(self, cmd: list, input_data: bytes = None):
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE if input_data else None,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = process.communicate(input=input_data)

        if process.returncode != 0:
            error_message = stderr.decode()
            self._logger.error(
                f"FFmpeg command failed with return code {process.returncode}: {error_message}")
            return None, error_message  # Или другой способ обработки ошибки

        return stdout, stderr

    def _convert_with_thumbnail(self, audio_path: str, cover_path: str, output_file: str):
        audio_codec, image_codec = Convertor._codec_map[self._audio_ext]

        cover_data = self._convert_image(cover_path)
        cmd = [
            "ffmpeg",
            "-i", audio_path,
            "-i", "pipe:0",
            "-map", "0:a",
            "-map", "1:v",
            "-c:a", audio_codec,
            "-c:v", image_codec,
            "-disposition:v", "attached_pic",
            output_file
        ]

        self._execute_ffmpeg(cmd, cover_data.read())

    def _convert_without_thumbnail(self, audio_path: str, output_file: str):
        audio_codec, image_codec = Convertor._codec_map[self._audio_ext]

        cmd = [
            "ffmpeg",
            "-i", audio_path,
            "-c:a", audio_codec,
            output_file
        ]

        self._execute_ffmpeg(cmd)

    def convert(self, audio_path: str, cover_path: Optional[str]) -> None:
        """
        Сохраняет конвертированный файл на 1 каталог выше, предполагается
        что исходные файлы находятся в ./tmp

        :param audio_path: (str) Путь к аудио файлу.
        :param cover_path: (Optional[str]) Путь к миниатюре или None.
        :return: (None)
        """

        out_filename, ext = os.path.splitext(os.path.basename(audio_path))
        parent_dir = os.path.dirname(os.path.dirname(audio_path))
        out_filepath = os.path.join(parent_dir, f"{out_filename}.{self._audio_ext}")

        if cover_path:
            self._convert_with_thumbnail(audio_path, cover_path, out_filepath)
        else:
            self._convert_without_thumbnail(audio_path, out_filepath)

