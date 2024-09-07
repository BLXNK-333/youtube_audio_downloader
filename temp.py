import subprocess
from PIL import Image
from PIL.Image import Resampling
from io import BytesIO
import os


class Convertor:
    def __init__(self, max_width=500):
        self._max_width = max_width

    def _resize_image(self, image_path: str) -> BytesIO:
        """Изменяет размер изображения до заданной максимальной ширины, сохраняя пропорции.

        :param image_path: (str) Путь к исходному изображению.
        :return: Объект BytesIO, содержащий изменённое изображение в заданном формате.
        """
        with Image.open(image_path) as img:
            # Изменяем размер изображения, сохраняя пропорции
            img.thumbnail((self._max_width, self._max_width), Resampling.LANCZOS)

            # Сохраняем изображение в объект BytesIO
            img_byte_arr = BytesIO()
            img.save(img_byte_arr,
                     format='WEBP')  # Можно использовать формат, который поддерживает обложки
            img_byte_arr.seek(0)  # Сбросить указатель в начало потока
            return img_byte_arr

    def add_cover_to_audio(self, audio_data: str, cover_data: BytesIO, output_file: str):
        """Добавление обложки к аудиофайлу."""

        # Создаём команду для вызова ffmpeg
        cmd = [
            "ffmpeg",
            "-i", audio_data,  # Входной аудиофайл
            "-i", "pipe:0",  # Обложка из stdin (pipe)
            "-map", "0:a",  # Выбираем аудиопоток из первого файла
            "-map", "1:v",  # Выбираем видеопоток (обложку) из второго файла
            "-c:a", "libmp3lame",  # Копируем аудио без перекодирования
            "-c:v", "mjpeg",  # Используем кодек mjpeg для обложки
            "-disposition:v:0", "attached_pic",  # Указываем, что это обложка
            output_file
        ]

        # Запускаем subprocess и передаём cover_data в stdin
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        stdout, stderr = process.communicate(input=cover_data.read())

        # Проверяем на наличие ошибок
        if process.returncode != 0:
            print(f"ffmpeg error: {stderr.decode()}")
            raise subprocess.CalledProcessError(process.returncode, cmd)


# Пример использования
if __name__ == "__main__":
    _save_directory = "/home/blxnk/Downloads/yt_downloader"
    audio_path = _save_directory + "/tmp/ПОШЛАЯ МОЛЛИ – АДСКАЯ КОЛЫБЕЛЬНАЯ.webm"
    cover_path = _save_directory + "/tmp/ПОШЛАЯ МОЛЛИ – АДСКАЯ КОЛЫБЕЛЬНАЯ.webp"
    output_path = _save_directory + "/output.mp3"

    # Создаём объект Convertor и изменяем размер изображения
    conv = Convertor(max_width=500)
    cover_data = conv._resize_image(cover_path)

    # Добавляем обложку к аудиофайлу
    conv.add_cover_to_audio(audio_path, cover_data, output_path)
