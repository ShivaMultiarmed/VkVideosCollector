import json
from time import sleep
import pymongo
import requests
import datetime

from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.by import By

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
        'id': item['id'],
        'title': item['title'],
        'page_url': f'{video_base_url}{item['owner_id']}_{item['id']}',
        'date': datetime.datetime.utcfromtimestamp(float(item['date']))
    } for item in json.loads(video_list_response.text)['response']['items']
][0:7]

browser = webdriver.Chrome()
for video in videos:
    try:
        browser.get(video['page_url'])
        sleep(7)
        # WebDriverWait(browser, 10).until(expected_conditions.presence_of_element_located((By.CSS_SELECTOR,'[class*="vkitTwoColumnLayoutMain__root"] [class*="VideoPage__player"] + .vkuiDiv.vkuiRootComponent')))
        video_details_wrapper = browser.find_element(By.CSS_SELECTOR, '[class*="vkitTwoColumnLayoutMain__root"] [class*="VideoPage__player"] + .vkuiDiv.vkuiRootComponent')
        try:
            link = video_details_wrapper.find_element(By.CSS_SELECTOR, '.vkuiSimpleCell__middle .vkuiSimpleCell__content span a')
            video['channel_title'] = link.text
            video['channel_link'] = link.get_attribute('href')
        except StaleElementReferenceException as e:
            pass
        except NoSuchElementException as e:
            pass
        try:
            description_wrapper = video_details_wrapper.find_element(By.CSS_SELECTOR, '.vkuiCard.vkuiRootComponent')
            try:
                show_more_button = description_wrapper.find_element(By.TAG_NAME, 'button')
                show_more_button.click()
            except NoSuchElementException:
                pass
            video['description'] = description_wrapper.find_element(By.CSS_SELECTOR, '[class*="Description__textWrapper"]').text
        except StaleElementReferenceException as e:
            pass
        except NoSuchElementException as e:
            pass

        sleep(3)
    except TimeoutException as e:
        pass

mongo_client = pymongo.MongoClient('mongodb://127.0.0.1:27017')
db = mongo_client.get_database('vk_videos')
is_collection_new = query not in db.list_collection_names()
collection = db.get_collection(query)
if is_collection_new:
    collection.create_index('id', unique=True)
for video in videos:
    try:
        collection.insert_one(video)
    except DuplicateKeyError as e:
        pass