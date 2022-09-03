
def token_vk():  # Токен для Вконтакте из файла token_vk.txt
    with open('token_vk.txt', 'r', encoding='utf-8') as file:
        return file.readline()


def token_ya_disk():  # Токен для Яндекс диска из файла token_ya_disk.txt
    with open('token_ya_disk.txt', 'r', encoding='utf-8') as file:
        return file.readline()


def id_vk():  # Получаем от пользователя id профиля и количество фотографий
    print('Введите id пользователя:')
    user_id_vk = input()
    print('Введите количество фотографий:')
    user_photo_vk = int(input())
    return user_id_vk, user_photo_vk
    # return '1'


def max_size_photo():  # Получаем список словарей со всеми фотографиями пользователя
    import requests
    url = 'https://api.vk.com/method/photos.get'
    params = {
        'access_token': token_vk(),
        'v': '5.131',
        'owner_id': user_id,
        'album_id': 'profile',
        'extended': '1',
        'photo_sizes': '1'
    }
    res_requests = requests.get(url, params=params)
    working_dict = res_requests.json()
    res = []
    for item in working_dict['response']['items']:
        dict_tmp = {
            'url': item['sizes'][-1]['url'],
            'size': item['sizes'][-1]['type'],
            'likes': item['likes']['count'],
            'date': item['date'],
        }
        res.append(dict_tmp)
    return res


def create_folder():  # Создаем папку avatars куда будут загружаться фото
    import requests
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    path = 'avatars'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'OAuth {token_ya_disk()}'
    }
    requests.put(f'{url}?path={path}', headers=headers)


# Сохраняем фото на диск, имя - количество лайков, если такое название уже есть
# данные о незагруженных фото сохраняем в отдельный список словарей.
def download_photo(count_photos=5):
    import requests
    from tqdm import tqdm
    error_uploading_photo_list = []
    data = max_size_photo()
    count = 0
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Authorization': f'OAuth {token_ya_disk()}'
    }
    url = 'https://cloud-api.yandex.net/v1/disk/resources'
    print('Загрузка фотографий:')
    for item in tqdm(data[:count_photos]):
        if count < count_photos:
            loadfile = requests.get(item['url']).content
            name_file = str(item['likes'])
            count += 1
            savefile = f'avatars/{name_file}.jpg'
            replace = False
            res = requests.get(
                f'{url}/upload?path={savefile}&overwrite={replace}',
                headers=headers).json()
            with open(f'{name_file}.jpg', 'wb') as f:
                f.write(loadfile)
                with open(f'{name_file}.jpg', 'rb') as file:
                    list_files.append(f'{name_file}.jpg')
                    try:
                        requests.put(res['href'], files={'file': file})
                        log_json.append(
                            {
                                'file_name': f'{name_file}.jpg',
                                'size': item['size']
                            }
                        )
                    except KeyError:
                        if res['error'] == 'DiskResourceAlreadyExistsError':
                            error_uploading_photo_list.append(
                                {
                                    'loadfile': item['url'],
                                    'name_file': f"{str(item['likes'])}_{str(item['date'])}",
                                    'size': item['size']
                                }
                            )
    return error_uploading_photo_list


# Сохраняем незагруженные ранее фото с названием - лайки_дата
def error_uploading_photo(uploading_photo_list):
    if uploading_photo_list:
        import requests
        from tqdm import tqdm
        data = uploading_photo_list
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': f'OAuth {token_ya_disk()}'
        }
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        print('Повторная загрузка с измененным именем файла:')
        for item in tqdm(data):
            loadfile = requests.get(item['loadfile']).content
            name_file = item['name_file']
            savefile = f'avatars/{name_file}.jpg'
            replace = False
            res = requests.get(
                f'{url}/upload?path={savefile}&overwrite={replace}',
                headers=headers).json()
            with open(f'{name_file}.jpg', 'wb') as f:
                f.write(loadfile)
                with open(f'{name_file}.jpg', 'rb') as file:
                    list_files.append(f'{name_file}.jpg')
                    requests.put(res['href'], files={'file': file})
                    log_json.append(
                        {
                            'file_name': f'{name_file}.jpg',
                            'size': item['size']
                        }
                    )
        print('Все фотографии успешно загружены')
    else:
        print('Все фотографии успешно загружены!')


def loger():  # Записываем в log.json данные о загруженных фото
    import json
    with open('log.json', "w") as f:
        json.dump(log_json, f, ensure_ascii=False, indent=2)


def delete_files_system():  # Удаляем фото сохраненные на локальной машине
    import os
    for file_name in list_files:
        os.remove(file_name)


log_json = []  # Задействован в функции loger()
list_files = []  # Задействован в функции delete_files_system()
user_id, user_photo = id_vk()
create_folder()
error_uploading_photo(download_photo(user_photo))
loger()
delete_files_system()
