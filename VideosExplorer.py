import json
import requests
from bs4 import BeautifulSoup
import datetime

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
client_id = 52812873 # application id
access_token = 'vk1.a.nEuqcn74TbC4OCdKC_n0pmoh3usHjeilx4cDdQNbGubbSng365ASpCWZkeOABUkpYEEA2Iv3amev8y9HQqu7lmfh0WGDNqd7XoycwRa4-3RYcGdKw1cyvo1z_NWkB5dueQLZchaDN85PKZJZZrPSMWKpyfvpO8Uc4FIacfuarnBBULURGainPUx_jAPBDynx'

video_search_url = 'https://api.vk.com/method/video.search'
video_search_headers = {
    'User-Agent': user_agent
}
#query = input("Введите поисковый запрос:\n")
query = 'Экономика'
video_search_params = {
    'q': query,
    'adult': 1, # безопасный поиск
    'sort': 2, # по релевантности
    'access_token': access_token,
    'v': 5.131
}
video_list_response = requests.get(
    url = video_search_url,
    params=video_search_params,
    headers=video_search_headers
)
video_base_url = 'https://vkvideo.ru/video'
videos = [
    {
        'title': item['title'],
        'page_url': f'{video_base_url}{item['owner_id']}_{item['id']}',
        'date': datetime.datetime.utcfromtimestamp(float(item['date']))
    } for item in json.loads(video_list_response.text)['response']['items']
]
print(videos)