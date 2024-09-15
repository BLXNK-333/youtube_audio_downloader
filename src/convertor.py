import os
import subprocess
import logging
from typing import Tuple
from io import BytesIO

from PIL import Image
from PIL.Image import Resampling
from mutagen.oggopus import OggOpus
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TIT2, TPE1, TDRC, COMM

from .config.app_config import get_config
from .entities import AudioExt, Metadata


class Convertor:
    _codec_map = {
        # scheme, (audio_codec, image_codec, is_need_bitrate)
        "opus": ("copy", "libtheora", False),
        "m4a": ("copy", "mjpeg", False),
        "opus_convert": ("libopus", "libtheora", True),
        "m4a_convert": ("aac", "mjpeg", True),
        "mp3": ("libmp3lame", "mjpeg", True),
    }

    def __init__(self):
        self._config = get_config()
        self._logger = logging.getLogger()
        self._yt_dlp_logger = logging.getLogger('yt-dlp')

        self._write_thumbnail = self._config.download.write_thumbnail
        self._write_metadata = self._config.download.write_metadata
        self._audio_ext = self._config.download.audio_ext

        self._resize = self._config.download.thumbnail_resize
        self._max_width = self._config.download.thumbnail_max_width

    def _get_output_filepath_and_codec_scheme(self, audio_path: str) -> Tuple[str, str]:
        filename, ext = os.path.splitext(os.path.basename(audio_path))
        parent_dir = os.path.dirname(os.path.dirname(audio_path))
        output_filepath = os.path.join(parent_dir, filename)

        strip_ext = ext.lstrip(".")
        scheme = strip_ext

        if self._audio_ext == AudioExt.OPUS and strip_ext == AudioExt.M4A:
            scheme = "opus_convert"
            output_filepath += f".{AudioExt.OPUS}"
        elif self._audio_ext == AudioExt.M4A and strip_ext == AudioExt.OPUS:
            scheme = "m4a_convert"
            output_filepath += f".{AudioExt.M4A}"
        elif self._audio_ext == AudioExt.MP3:
            scheme = AudioExt.MP3
            output_filepath += f".{AudioExt.MP3}"
        else:
            output_filepath += ext  # Default to the original extension
        return output_filepath, scheme

    def _convert_image(self, image_path: str) -> BytesIO:
        with Image.open(image_path) as img:
            if self._resize:
                img.thumbnail((self._max_width, self._max_width), Resampling.LANCZOS)
                self._yt_dlp_logger.debug(
                    f"[*convertor] Resized image {image_path} to {self._max_width}px")

            img_byte_arr = BytesIO()
            img.save(img_byte_arr, format='WEBP')
            img_byte_arr.seek(0)
            return img_byte_arr

    def _get_bitrate(self, file_path: str) -> int:
        """
        Определяет битрейт аудиофайла с помощью ffprobe.

        :param file_path: Путь к аудиофайлу.
        :return: Битрейт файла в кбит/с.
        """
        try:
            # Получаем информацию о продолжительности с помощью ffprobe
            result = subprocess.run(
                ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                 '-of', 'csv=p=0', file_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=True
            )

            # Парсим продолжительность
            duration = float(result.stdout.strip())
            # Получаем размер файла в байтах
            file_size = os.path.getsize(file_path)
            # Битрейт рассчитывается как (размер файла в байтах * 8) /
            # (длительность в секундах * 1000). Переводим в кбит/с
            bitrate = int((file_size * 8) / (duration * 1000)) + 1
            self._yt_dlp_logger.info(
                f"[*convertor] Calculated bitrate for {file_path}: {bitrate} kbps")
            return bitrate

        except subprocess.CalledProcessError as e:
            self._yt_dlp_logger.error(f"[*convertor] Error executing ffprobe: {e.stderr}")
            raise

        except ValueError:
            self._yt_dlp_logger.error(
                f"[*convertor] The bitrate could not be determined.")
            raise

        except FileNotFoundError:
            self._yt_dlp_logger.error(f"[*convertor] File {file_path} not found.")
            raise

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
            self._yt_dlp_logger.error(
                f"[*convertor] FFmpeg command failed with return code "
                f"{process.returncode}: {error_message}")
            return None, error_message  # Или другой способ обработки ошибки
        else:
            self._yt_dlp_logger.info(f"[*convertor] Audio has been saved: {cmd[-1]}")
        return stdout, stderr

    def _process_add_metadata(self, filepath: str, metadata: Metadata):
        ext_hmap = {'.opus': OggOpus, '.m4a': MP4, '.mp3': ID3}
        _, ext = os.path.splitext(filepath)
        audio = ext_hmap[ext](filepath)

        # Пример добавления метаданных для каждого формата
        if isinstance(audio, OggOpus):
            audio['title'] = metadata.title
            audio['artist'] = metadata.artist
            audio['date'] = metadata.date
            audio['comment'] = metadata.comment
        elif isinstance(audio, MP4):
            audio['\xa9nam'] = metadata.title  # title
            audio['\xa9ART'] = metadata.artist  # artist
            audio['\xa9day'] = metadata.date  # date
            audio['\xa9cmt'] = metadata.comment  # comment
        elif isinstance(audio, ID3):
            audio.add(TIT2(encoding=3, text=metadata.title))
            audio.add(TPE1(encoding=3, text=metadata.artist))
            audio.add(TDRC(encoding=3, text=metadata.date))
            audio.add(COMM(encoding=3, text=metadata.comment))

        audio.save()
        self._yt_dlp_logger.info("[*convertor] Metadata added")

    def _process_convert_audio(
        self,
        audio_path: str,
        cover_path: str,
        output_file: str,
        scheme: str
    ) -> None:
        def create_cmd(add_thumbnail: bool):
            audio_codec, image_codec, is_need_bitrate = Convertor._codec_map[scheme]
            cmd = [
                "ffmpeg",
                "-i", audio_path
            ]

            if add_thumbnail:
                cmd.extend([
                    "-i", "pipe:0",
                    "-map", "0:a",
                    "-map", "1:v",
                ])
            cmd.extend(["-c:a", audio_codec])

            if is_need_bitrate:
                cur_br = self._get_bitrate(audio_path)
                cmd.extend(["-b:a", f"{cur_br}k"])

            if add_thumbnail:
                cmd.extend([
                    "-c:v", image_codec,
                    "-disposition:v:0", "attached_pic"
                ])
            cmd.extend([output_file])
            return cmd

        # Тут очередная палка в жопу. Не удалось вхуячить по-нормальному
        # миниатюру в файлы opus, по этому для них отключил миниатюры.
        _, ext = os.path.splitext(output_file)
        command = create_cmd(
            add_thumbnail=(not ext.lstrip(".") == AudioExt.OPUS and bool(cover_path))
        )

        if cover_path:
            cover_data = self._convert_image(cover_path)
            self._execute_ffmpeg(command, cover_data.read())
        else:
            self._execute_ffmpeg(command)

    def convert(
        self,
        audio_path: str,
        cover_path: str,
        metadata: Metadata
    ) -> None:
        """
        Сохраняет конвертированный файл на 1 каталог выше, предполагается
        что исходные файлы находятся в ./tmp

        :param audio_path: (str) Путь к аудио файлу или "".
        :param cover_path: (str) Путь к миниатюре или "".
        :param metadata: (Metadata) Dataclass с метаданными.
        :return: (None).
        """

        output_filepath, codec_scheme = self._get_output_filepath_and_codec_scheme(
            audio_path
        )
        self._process_convert_audio(audio_path, cover_path, output_filepath, codec_scheme)
        if self._write_metadata:
            self._process_add_metadata(output_filepath, metadata)
