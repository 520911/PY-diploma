import time

import requests
import json
from tqdm import tqdm

with open('token.txt') as f:
    ya_token1 = f.readline().strip()
    vk_token1 = f.readline()


class VkPhotos:
    url = 'https://api.vk.com/method/'

    def __init__(self, vk_token, version='5.130'):
        self.vk_token = vk_token
        self.version = version
        self.params = {
            'access_token': self.vk_token,
            'v': self.version
        }
        self.vk_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']

    def get_vk_photos(self, vk_id=None):
        if vk_id is None:
            vk_id = self.vk_id
        headers = {'Content-Type': 'application/json',
                   'Authorization': '{}'.format(self.vk_token)
                   }
        params = {
            'owner_id': vk_id,  # 552934290
            'album_id': 'profile',
            'count': '5',
            'extended': '1',
            'photo_sizes': '1',
            **self.params
        }
        responce = requests.get(self.url + 'photos.get?', headers=headers, params=params).json()
        result_dict = {}
        log_dict = {}
        for photo_info in tqdm(responce['response']['items'], desc='Loading...', total=5, unit='S'):
            time.sleep(1)
            type_size = photo_info['sizes'][-1]['type']
            file_name = str(photo_info['likes']['count']) + '__' + str(photo_info['date']) + '.jpg'
            file_url = photo_info['sizes'][-1]['url']
            result_dict[file_name] = file_url
            log_dict[file_name] = type_size
        with open('photos_info_oop.json', 'w') as file:
            json.dump(log_dict, file, indent=2)
        return result_dict


class YaUploder:
    ya_url = 'https://cloud-api.yandex.net/v1/disk/resources/'

    def __init__(self, ya_token, version='5.130'):
        self.ya_token = ya_token
        self.version = version
        self.params = {'path': 'vkphotos'}
        self.ya_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.ya_token)
        }

    def create_ya_folder(self):  # Создание папки на яндекс диске
        response = requests.put(self.ya_url, headers=self.ya_headers, params=self.params)
        result_url = self.ya_url + self.params['path']
        if response.status_code == 201:
            print('Папка успешно создана')
        elif response.status_code == 409:
            print('Такая папка уже существует')
        return result_url

    def upload_vk_photo_to_yadisk(self, dict_of_photos):
        result_url = self.ya_url + 'upload?'
        YaUploder.create_ya_folder(self)
        for key, value in tqdm(dict_of_photos.items(), desc='Downloads photo...', total=5, colour='green'):
            time.sleep(0.5)
            params = {  # Использование словаря с информацией о фотографиях для формирования параметров загрузки на диск
                'path': 'vkphotos/' + key,
                'url': value,
            }
            response = requests.post(result_url + params['path'], headers=self.ya_headers, params=params)
            response.raise_for_status()
            if response.status_code == 202:
                print('Загрузка прошла успешно!')
            elif response.status_code == 400:
                print('Некорректные данные!')
            elif response.status_code == 409:
                print('Указанной папки нет на яндекс диске!')
            elif response.status_code == 507:
                print('Недостаточно свободного места на яндекс диске!')
            else:
                break


vk_photos = VkPhotos(vk_token1)
get_photos_names_urls = vk_photos.get_vk_photos(552934290)
ya_uploader = YaUploder(ya_token1)
ya_uploader.upload_vk_photo_to_yadisk(get_photos_names_urls)
