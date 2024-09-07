import subprocess
from PIL import Image
from PIL.Image import Resampling
from io import BytesIO
import os

from src.config.app_config import get_config


class Convertor:
    _codec_map = {
        "ogg": ("copy", "libtheora"),
        "m4a": ("copy", "mjpeg"),
        "mp3": ("libmp3lame", "mjpeg"),
    }

    def __init__(self):
        self._config = get_config()
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
            raise subprocess.CalledProcessError(process.returncode, cmd, output=stderr.decode())

        return stdout, stderr

    def _get_codec_settings(self):
        if self._audio_ext not in Convertor._codec_map:
            raise Exception(
                f"Not supported format: {self._audio_ext}\n"
                f"Use AUDIO_EXT=[{'|'.join(Convertor._codec_map.keys())}] in settings")
        return Convertor._codec_map.get(self._audio_ext)

    def convert_with_thumbnail(self, audio_path: str, cover_path: str, output_file: str):
        audio_codec, image_codec = self._get_codec_settings()

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

    def convert_without_thumbnail(self, audio_path: str, output_file: str):
        audio_codec, image_codec = self._get_codec_settings()

        cmd = [
            "ffmpeg",
            "-i", audio_path,
            "-c:a", audio_codec,
            output_file
        ]

        self._execute_ffmpeg(cmd)


# Пример использования
if __name__ == "__main__":
    save_directory = "/home/blxnk/Downloads/yt_downloader"
    audio_path = os.path.join(save_directory, "ПОШЛАЯ МОЛЛИ – АДСКАЯ КОЛЫБЕЛЬНАЯ.webm")
    cover_path = os.path.join(save_directory, "ПОШЛАЯ МОЛЛИ – АДСКАЯ КОЛЫБЕЛЬНАЯ.webp")
    output_with_thumbnail = os.path.join(save_directory, "output_with_thumbnail.ogg")
    output_without_thumbnail = os.path.join(save_directory, "output_without_thumbnail.ogg")

    conv = Convertor()
    # conv.convert_with_thumbnail(audio_path, cover_path, output_with_thumbnail)
    conv.convert_without_thumbnail(audio_path, output_without_thumbnail)
