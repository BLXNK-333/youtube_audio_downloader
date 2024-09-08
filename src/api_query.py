import pprint

import requests
from src.config.app_config import get_config


class ApiQuery:
    def __init__(self):
        self._config = get_config()
        self._api_key_yt = self._config.api.yt_token
        self._base_url = "https://www.googleapis.com/youtube/v3"

    def get_playlist_title(self, playlist_id: str):
        url = f"{self._base_url}/playlists?part=snippet&id={playlist_id}&key={self._api_key_yt}"
        response = requests.get(url)
        data = response.json()
        return data['items'][0]['snippet']['title']

    def get_video_details(self, video_id: str):
        url = f"{self._base_url}/videos"
        params = {
            'part': 'snippet',
            'id': video_id,
            'key': self._api_key_yt
        }

        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if 'items' in data and len(data['items']) > 0:
                snippet = data['items'][0]['snippet']
                return {
                    'title': snippet['title'],
                    'published': snippet['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={video_id}"
                }
            else:
                raise ValueError("Видео с указанным ID не найдено.")
        else:
            response.raise_for_status()

    def get_playlist_videos_details(self, playlist_id):
        videos = {}
        url = f"{self._base_url}/playlistItems"
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
                videos[videoId] = {
                    'title': snippet['title'],
                    'published': snippet['publishedAt'],
                    'url': f"https://www.youtube.com/watch?v={videoId}"
                }

            next_page_token = data.get('nextPageToken')
            if next_page_token:
                params['pageToken'] = next_page_token
            else:
                break

        return videos

#
# if __name__ == '__main__':
#     AQ = ApiQuery()
#     pprint.pprint(AQ.get_video_details("YYwmlS8wkW0"))
