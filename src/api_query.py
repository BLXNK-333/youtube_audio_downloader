import logging
from typing import List, Dict

import requests
from .config.app_config import get_config


class ApiQuery:
    def __init__(self):
        self._config = get_config()
        self._logger = logging.getLogger()
        self._api_key_yt = self._config.api.yt_token
        self._endpoint = self._config.api.endpoint

    def get_playlist_title(self, playlist_id: str) -> str:
        url = f"{self._endpoint}/playlists?part=snippet&id={playlist_id}&key={self._api_key_yt}"
        response = requests.get(url)
        data = response.json()
        title = data['items'][0]['snippet']['title']
        self._logger.info(f"Playlist name received: {title}")
        return title

    def get_video_details(self, video_id: str) -> List[Dict[str, str]]:
        url = f"{self._endpoint}/videos"
        params = {
            'part': 'snippet',
            'id': video_id,
            'key': self._api_key_yt
        }

        response = requests.get(url, params=params)
        snippet_videos = []

        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                snippet = data['items'][0]['snippet']
                snippet_videos.append({
                    'title': snippet['title'],
                    'url': f"https://www.youtube.com/watch?v={video_id}",
                    'published': snippet['publishedAt'],
                })
                self._logger.info(f"Video details received, quantity: {len(snippet_videos)}")
            else:
                self._logger.error(f"No video with the specified ID was found. ID: {video_id}")
        else:
            response.raise_for_status()

        return snippet_videos

    def get_playlist_videos_details(self, playlist_id: str) -> List[Dict[str, str]]:
        snippet_videos = []
        url = f"{self._endpoint}/playlistItems"
        params = {
            'part': 'snippet',
            'playlistId': playlist_id,
            'maxResults': 50,  # Максимальное количество результатов на страницу
            'key': self._api_key_yt
        }

        while True:
            response = requests.get(url, params=params)

            if response.status_code != 200:
                break

            data = response.json()

            for item in data['items']:
                snippet = item['snippet']
                videoId = snippet['resourceId']['videoId']
                snippet_videos.append({
                    'title': snippet['title'],
                    'url': f"https://www.youtube.com/watch?v={videoId}",
                    'published': snippet['publishedAt'],
                })

            next_page_token = data.get('nextPageToken')
            if next_page_token:
                params['pageToken'] = next_page_token
            else:
                break
        self._logger.info(f"Video details received, quantity: {len(snippet_videos)}")
        return snippet_videos
