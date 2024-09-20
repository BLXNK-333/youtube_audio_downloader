import os
import subprocess
import logging
from typing import Tuple

from ..entities import AudioExt
from ..config.app_config import get_config


class AudioConverter:
    _codec_map = {
        # scheme, (audio_codec, is_need_bitrate)
        "opus": ("copy", False),
        "m4a": ("copy", False),
        "opus_convert": ("libopus", True),
        "m4a_convert": ("aac", True),
        "mp3": ("libmp3lame", True),
    }

    def __init__(self):
        self._config = get_config()
        self._yt_dlp_logger = logging.getLogger('yt-dlp')
        self._audio_ext = self._config.download.audio_ext

    def _get_output_params(self, audio_path: str) -> Tuple[str, str, bool]:
        filename, ext = os.path.splitext(os.path.basename(audio_path))
        parent_dir = os.path.dirname(os.path.dirname(audio_path))
        output_filepath = os.path.join(parent_dir, filename)

        strip_ext = ext.lstrip(".")
        scheme = strip_ext

        if strip_ext == AudioExt.WEBM:
            scheme = AudioExt.OPUS
            output_filepath += f".{AudioExt.OPUS}"
        elif self._audio_ext == AudioExt.OPUS and strip_ext == AudioExt.M4A:
            scheme = "opus_convert"
            output_filepath += f".{AudioExt.OPUS}"
        elif self._audio_ext == AudioExt.M4A and strip_ext == AudioExt.WEBM:
            scheme = "m4a_convert"
            output_filepath += f".{AudioExt.M4A}"
        elif self._audio_ext == AudioExt.MP3:
            scheme = AudioExt.MP3
            output_filepath += f".{AudioExt.MP3}"
        else:
            output_filepath += ext  # Default to the original extension

        acodec, is_need_bitrate = AudioConverter._codec_map[scheme]
        return output_filepath, acodec, is_need_bitrate

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
                f"[*convertor] Calculated bitrate for audio: {bitrate} kbps")
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

    def _execute_ffmpeg(self, cmd: list):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = process.communicate()

        if process.returncode != 0:
            error_message = stderr.decode()
            self._yt_dlp_logger.error(
                f"[*convertor] FFmpeg command failed with return code "
                f"{process.returncode}: {error_message}")
            return None, error_message  # Или другой способ обработки ошибки
        else:
            self._yt_dlp_logger.info(f"[*convertor] Audio has been saved: {cmd[-1]}")
        return stdout, stderr

    def convert_audio(self, audio_path: str) -> str:
        output_filepath, acodec, is_need_bitrate = self._get_output_params(audio_path)

        cmd = [
            "ffmpeg", "-y",
            "-i", audio_path,
            "-c:a", acodec
        ]
        if is_need_bitrate:
            cur_br = self._get_bitrate(audio_path)
            cmd.extend(["-b:a", f"{cur_br}k"])
        cmd.append(output_filepath)

        self._execute_ffmpeg(cmd)
        return output_filepath
