import time
import requests
import json
from tqdm import tqdm


def get_vk_photos(user_vk_id, vk_token):
    user_url = 'https://api.vk.com/method/photos.get?'
    headers = {'Content-Type': 'application/json',
               'Authorization': '{}'.format(vk_token)
               }
    params = {
        'owner_id': user_vk_id,  # 552934290
        'album_id': 'profile',
        'count': '5',
        'extended': '1',
        'photo_sizes': '1',
        'access_token': token_vk,
        'v': '5.130'
    }
    responce = requests.get(user_url, headers=headers, params=params)
    data = responce.json()
    list_of_photos_info = []
    list_of_photos_urls = []
    list_of_file_name = []
    for photo_info in tqdm(data['response']['items'], desc='Loading...', total=5,
                           unit='S'):  # Извлечение данных в цикле в формате json
        time.sleep(1)
        type_size = photo_info['sizes'][-1]['type']  # Получение типа самой большой по размеру фотографии
        file_name = str(photo_info['likes']['count']) + str(
            photo_info[
                'date']) + '.jpg'  # Формирование имени фотографии, которое состоит из количества лайков
        # под фотографией и даты добавления
        file_url = photo_info['sizes'][-1]['url']  # Поиск ссылки на самую большую фотографию для выгрузки
        list_of_photos_info.append({'file_name': file_name, 'size': type_size})  # Формирование временного листа
        # для выгрузки в json
        list_of_photos_urls.append(file_url)  # Сохранение урлов фотографий в список
        list_of_file_name.append(file_name)  # Сохранение имен фотографий в список
    result_dict = dict(zip(list_of_file_name, list_of_photos_urls))  # Формирование словаря для последующего
    # использования значений урлов и имени фотографий
    with open('photos_info.json', 'w') as file:
        json.dump(list_of_photos_info, file, indent=2)  # Сохранения json информацции на диске о фотографиях
    return result_dict  # Получение словаря с названием и урлом фотографий


def ya_headers(token_yandex):
    return {
        'Content-Type': 'application/json',
        'Authorization': 'OAuth {}'.format(token_yandex)
    }


def create_ya_folder(token_yandex):  # Создание папки на яндекс диске
    ya_url = 'https://cloud-api.yandex.net/v1/disk/resources/'
    headers = ya_headers(token_yandex)
    params = {'path': 'vkphotos'}
    response = requests.put(ya_url, headers=headers, params=params)
    result_url = ya_url + params['path']
    if response.status_code == 201:
        print('Папка успешно создана')
    elif response.status_code == 409:
        print('Такая папка уже существует')
    return result_url  # Функция возвращает путь до новой папки на яндекс диске


def upload_vk_photo_to_yadisk(token_yandex, user_vk_id, vk_token):
    ya_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload?'
    create_ya_folder(token_yandex)  # Вызов функции для оздания папки
    headers = ya_headers(token_yandex)
    dict_of_photos = get_vk_photos(user_vk_id, vk_token)  # Вызов функции для получения словаря с информацией
    # об имени и ссылке на фотографию
    for key, value in tqdm(dict_of_photos.items(), desc='Downloads photo...', total=5, colour='green'):
        time.sleep(0.5)
        params = {  # Использование словаря с информацией о фотографиях для формирования параметров загрузки на диск
            'path': 'vkphotos/' + key,
            'url': value,
        }
        response = requests.post(ya_url + params['path'], headers=headers, params=params)
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


token_ya = 'AQAHcDqwA'
token_vk = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
user_id = int(input('Введите свой id во вконтакте: '))
upload_vk_photo_to_yadisk(token_ya, user_id, token_vk)
