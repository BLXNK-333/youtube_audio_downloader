import os
import re
import subprocess
from io import BytesIO
from enum import StrEnum

from yt_dlp import YoutubeDL
from PIL import Image
from PIL.Image import Resampling


# Путь к папке для сохранения окончательных файлов
# output_base_folder = os.path.expanduser('~/Downloads')


class Entity(StrEnum):
    VIDEO = "VIDEO"
    PLAYLIST = "PLAYLIST"
    BAD_LINK = "BAD_LINK"


class UrlPrefix(StrEnum):
    VIDEO = "https://www.youtube.com/watch?v="
    PLAYLIST = "https://www.youtube.com/playlist?list="
    SHARE = "https://youtu.be/"


def what_entity(url: str) -> str:
    if url.startswith(UrlPrefix.PLAYLIST):
        return Entity.PLAYLIST
    if url.startswith(UrlPrefix.VIDEO) or url.startswith(UrlPrefix.SHARE):
        return Entity.VIDEO

    return Entity.BAD_LINK


def extract_id_from_url(url: str):
    pass


def resize_image(image_data, max_width=300):
    """Изменение размера изображения до max_width, сохраняя пропорции."""
    with Image.open(image_data) as img:
        img.thumbnail((img.width, max_width), Resampling.LANCZOS)
        output_data = BytesIO()
        img.save(output_data, format='WEBP')
        output_data.seek(0)
        return output_data


def add_cover_to_audio(audio_data, cover_data, output_file):
    """Добавление обложки к аудиофайлу."""
    # Сохраняем данные во временные файлы для использования в ffmpeg
    with open('temp_audio.opus', 'wb') as temp_audio, open('temp_cover.webp',
                                                           'wb') as temp_cover:
        temp_audio.write(audio_data.getbuffer())
        temp_cover.write(cover_data.getbuffer())

    cmd = [
        "ffmpeg", "-i", "temp_audio.opus",
        "-i", "temp_cover.webp",
        "-map", "0", "-map", "1",
        "-c:a", "copy", "-c:v", "libtheora",
        "-disposition:v", "attached_pic",
        output_file
    ]
    subprocess.run(cmd, check=True)

    # Удаляем временные файлы
    os.remove('temp_audio.opus')
    os.remove('temp_cover.webp')


def download_audio(url, save_path):
    # Убедитесь, что директория существует
    os.makedirs(save_path, exist_ok=True)

    ydl_options = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'writethumbnail': True,  # Загружаем миниатюры
        'writemetadata': True,  # Сохранение метаданных
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'opus',
            'preferredquality': '0',  # Максимальное качество
        }],
        'merge_output_format': 'opus',  # Указываем Opus как конечный контейнер
        'noplaylist': True,  # Скачиваем файлы по одному
        'dateafter': 'now-7y',  # Только видео, опубликованные не более 7 лет назад
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
    }

    with YoutubeDL(ydl_options) as ydl:
        ydl.download([url])


if __name__ == '__main__':
    # Ссылка на плейлист
    # playlist_url = 'https://www.youtube.com/playlist?list=PL-adxGZ1y-OXzOAXG5gB0pF5g5Pw7jBEG'

    # Запуск скачивания и обработки плейлиста
    # url = "https://www.youtube.com/watch?v=ALpS4Fq3lmw&list=PLDyvV36pndZFWfEQpNixIHVvp191Hb3Gg&index=1"
    url = "https://www.youtube.com/watch?v=U-xw6e-62fw"
    save_dir = "/home/blxnk/Downloads/yt_downloader"
    try:
        download_audio(url, save_dir)
    except Exception as e:
        print(e)