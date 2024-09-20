import logging
from typing import Dict, List, Optional
from urllib.parse import urlparse

import requests
from .config.app_config import get_config


class ApiQuery:
    def __init__(self):
        self._config = get_config()
        self._logger = logging.getLogger()
        self._api_key_yt = self._config.api.yt_token
        self._endpoint = self._config.api.endpoint
        self._proxy = self._parse_proxy(self._config.extended.proxy)

    def _parse_proxy(self, proxy_url: str) -> Optional[Dict[str, str]]:
        """Парсит прокси URL и возвращает словарь для requests."""
        if proxy_url == "":
            return None
        parsed = urlparse(proxy_url)
        proxy_scheme = parsed.scheme

        if proxy_scheme not in {"http", "https", "socks4", "socks5"}:
            raise ValueError(f"Unsupported proxy scheme: {proxy_scheme}")
        return {proxy_scheme: proxy_url}

    def _make_request(self, url: str, params: Dict) -> Optional[Dict]:
        """Выполняет запрос к API и обрабатывает результат."""
        try:
            response = requests.get(url, params=params, proxies=self._proxy)
            if response.status_code != 200:
                self._logger.error(
                    f"API request failed. Status code: {response.status_code}, "
                    f"URL: {url}, Params: {params}"
                )
                return None  # Возвращаем None при неудачном статусе

            return response.json()  # Возвращаем результат при успешном запросе

        except requests.ConnectionError:
            self._logger.error("Connection error: There may be problems with the Internet.")
            return None

        except requests.Timeout:
            self._logger.error("Request timed out: The server did not respond on time.")
            return None

        except requests.RequestException as e:
            self._logger.error(f"API request error: {e}")
            return None

    def _process_pagination(
        self, url: str, params: Dict, process_func
    ) -> List[Dict[str, str]]:
        """Обрабатывает пагинацию и возвращает обработанные данные."""
        results = []

        while True:
            data = self._make_request(url, params)
            if not data:
                break

            # Обработка данных на странице
            processed_items = process_func(data)
            results.extend(processed_items)

            # Проверяем наличие токена для следующей страницы
            next_page_token = data.get('nextPageToken')
            if next_page_token:
                params['pageToken'] = next_page_token
            else:
                break

        return results

    def get_playlist_info(self, playlist_id: str) -> Optional[Dict[str, str]]:
        params = {
            'part': 'snippet',
            'id': playlist_id,
            'key': self._api_key_yt
        }

        url = f"{self._endpoint}/playlists"
        data = self._make_request(url, params)

        if not data or 'items' not in data or not data['items']:
            self._logger.error(f"Playlist with ID {playlist_id} not found.")
            return None

        info = {
            'title': data['items'][0]['snippet']['title'],
            'publishedAt': data['items'][0]['snippet']['publishedAt'],
            'channelId': data['items'][0]['snippet']['channelId']
        }

        self._logger.info(f"Playlist name received: {info['title']}")
        return info

    def get_channel_info(self, handle: str) -> Optional[Dict[str, str]]:
        """
        Возвращает словарь с информацией о канале, включая количество видео и плейлист загрузок.
        :param handle: (str) Хэндл канала, начиная с '@'.
            Пример: handle: "@808nation"
        """
        search_params = {
            'part': 'snippet',
            'q': handle,
            'type': 'channel',
            'key': self._api_key_yt
        }
        search_url = f"{self._endpoint}/search"
        data = self._make_request(search_url, search_params)

        if not data or 'items' not in data or not data['items']:
            self._logger.error(f"No channel found for handle: {handle}")
            return None

        channel_id = data['items'][0]['snippet']['channelId']
        uploads_playlist_id = 'UU' + channel_id[2:]
        channel_info = data['items'][0]['snippet']

        info = {
            'title': channel_info['title'],
            'publishedAt': channel_info['publishedAt'],
            'channelId': channel_id,
            'uploads': uploads_playlist_id
        }

        self._logger.info(f"Channel info retrieved: {info['title']}")
        return info

    def get_video_snippet(self, video_id: str) -> List[Dict[str, str]]:
        url = f"{self._endpoint}/videos"
        params = {
            'part': 'snippet',
            'id': video_id,
            'key': self._api_key_yt
        }

        data = self._make_request(url, params)
        if not data or 'items' not in data or not data['items']:
            self._logger.error(f"No video with the specified ID was found. ID: {video_id}")
            return []

        snippet = data['items'][0]['snippet']
        return [{
            'title': snippet['title'],
            'url': f"https://www.youtube.com/watch?v={video_id}",
            'published': snippet['publishedAt'],
        }]

    def get_playlist_snippets(
        self,
        playlist_id: str,
    ) -> List[Dict[str, str]]:

        url = f"{self._endpoint}/playlistItems"
        params = {
            'part': 'snippet',
            'playlistId': playlist_id,
            'maxResults': 50,
            'key': self._api_key_yt
        }

        def process_func(data: Dict) -> List[Dict[str, str]]:
            items = []
            for item in data['items']:
                snippet = item['snippet']
                videoId = snippet['resourceId']['videoId']
                items.append({
                    'title': snippet['title'],
                    'url': f"https://www.youtube.com/watch?v={videoId}",
                    'published': snippet['publishedAt'],
                })
            return items

        return self._process_pagination(url, params, process_func)
