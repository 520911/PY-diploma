import time

import requests
import json
from tqdm import tqdm

with open('token.txt') as f:
    ya_token1 = f.readline().strip()
    vk_token1 = f.readline()


class VkYaPhotos:
    url = 'https://api.vk.com/method/'
    ya_url = 'https://cloud-api.yandex.net/v1/disk/resources/'

    def __init__(self, ya_token, vk_token, version='5.130'):
        self.vk_token = vk_token
        self.ya_token = ya_token
        self.version = version
        self.params = {
            'access_token': self.vk_token,
            'v': self.version
        }
        self.ya_headers = {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.ya_token)
        }
        self.vk_id = requests.get(self.url + 'users.get', self.params).json()['response'][0]['id']
        self.list_of_photos_info = []
        self.list_of_photos_urls = []
        self.list_of_file_name = []

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
            'access_token': self.vk_token,
            'v': '5.130'
        }
        responce = requests.get(self.url + 'photos.get?', headers=headers, params=params).json()
        for photo_info in tqdm(responce['response']['items'], desc='Loading...', total=5,
                               unit='S'):  # Извлечение данных в цикле в формате json
            time.sleep(1)
            type_size = photo_info['sizes'][-1]['type']  # Получение типа самой большой по размеру фотографии
            file_name = str(photo_info['likes']['count']) + str(
                photo_info[
                    'date']) + '.jpg'  # Формирование имени фотографии, которое состоит из количества лайков
            # под фотографией и даты добавления
            file_url = photo_info['sizes'][-1]['url']  # Поиск ссылки на самую большую фотографию для выгрузки
            self.list_of_photos_info.append(
                {'file_name': file_name, 'size': type_size})  # Формирование временного листа
            # для выгрузки в json
            self.list_of_photos_urls.append(file_url)  # Сохранение урлов фотографий в список
            self.list_of_file_name.append(file_name)  # Сохранение имен фотографий в список
        result_dict = dict(
            zip(self.list_of_file_name, self.list_of_photos_urls))  # Формирование словаря для последующего
        # использования значений урлов и имени фотографий
        with open('photos_info_oop.json', 'w') as file:
            json.dump(self.list_of_photos_info, file, indent=2)  # Сохранения json информацции на диске о фотографиях
        return result_dict  # Получение словаря с названием и урлом фотографий

    def create_ya_folder(self):  # Создание папки на яндекс диске
        params = {'path': 'vkphotos'}
        response = requests.put(self.ya_url, headers=self.ya_headers, params=params)
        result_url = self.ya_url + params['path']
        if response.status_code == 201:
            print('Папка успешно создана')
        elif response.status_code == 409:
            print('Такая папка уже существует')
        return result_url  # Функция возвращает путь до новой папки на яндекс диске

    def upload_vk_photo_to_yadisk(self):
        ya_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload?'
        VkYaPhotos.create_ya_folder(self)  # Вызов функции для оздания папки
        dict_of_photos = VkYaPhotos.get_vk_photos(self, vk_id=None)  # Вызов функции для получения словаря с информацией
        # об имени и ссылке на фотографию
        for key, value in tqdm(dict_of_photos.items(), desc='Downloads photo...', total=5, colour='green'):
            time.sleep(0.5)
            params = {  # Использование словаря с информацией о фотографиях для формирования параметров загрузки на диск
                'path': 'vkphotos/' + key,
                'url': value,
            }
            response = requests.post(ya_url + params['path'], headers=self.ya_headers, params=params)
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


service = VkYaPhotos(ya_token1, vk_token1)
service.upload_vk_photo_to_yadisk()
