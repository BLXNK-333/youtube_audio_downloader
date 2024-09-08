import subprocess
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

    def convert_with_thumbnail(self, audio_path: str, cover_path: str, output_file: str):
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

    def convert_without_thumbnail(self, audio_path: str, output_file: str):
        audio_codec, image_codec = Convertor._codec_map[self._audio_ext]

        cmd = [
            "ffmpeg",
            "-i", audio_path,
            "-c:a", audio_codec,
            output_file
        ]

        self._execute_ffmpeg(cmd)
