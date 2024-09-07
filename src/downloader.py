import os
from yt_dlp import YoutubeDL


def download_audio(url, save_path):
    # Убедитесь, что директория существует
    os.makedirs(save_path, exist_ok=True)

    ydl_options = {
        'format': '140',
        'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
        'writethumbnail': True,  # Загружаем миниатюры
        'writemetadata': True,  # Сохранение метаданных
        'headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        },
    }

    with YoutubeDL(ydl_options) as ydl:
        ydl.download([url])


def list_formats(video_url):
    ydl_opts = {
        'listformats': True
        # Эта опция выводит список всех доступных форматов, но не скачивает видео
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(video_url, download=False)


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

    # url = "https://www.youtube.com/watch?v=U-xw6e-62fw"
    # list_formats(url)

