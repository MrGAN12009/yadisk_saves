import requests
import json


# Ваш OAuth-токен, полученный через Yandex OAuth
TOKEN = 'y0__wgBEPnemqsHGPSPNCD3s9HvEdqo44Fydx9WW0KNSk1vOv3PCmhJ'

# Базовый URL для API Яндекс.Диска
BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
UPLOAD_URL = f'{BASE_URL}/upload'

headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}

def create_folder(folder_path):
    """Создаёт папку на Яндекс.Диске"""
    response = requests.put(BASE_URL, headers=headers, params={'path': folder_path})
    if response.status_code in (201, 409):  # Папка создана или уже существует
        print(f'Папка {folder_path} готова.')
    else:
        print(f'Ошибка создания папки {folder_path}: {response.status_code} {response.text}')

def upload_file_from_url(file_url, remote_path):
    """Загружает файл на Яндекс.Диск напрямую с URL"""
    # Получаем URL для загрузки на Яндекс.Диск
    params = {'path': remote_path, 'overwrite': 'true'}
    response = requests.get(UPLOAD_URL, headers=headers, params=params)

    if response.status_code == 200:
        upload_url = response.json().get('href')
        if not upload_url:
            print('Не удалось получить ссылку для загрузки файла.')
            return False

        # Скачиваем файл и сразу передаём его в запрос на загрузку
        with requests.get(file_url, stream=True) as file_response:
            if file_response.status_code == 200:
                upload_response = requests.put(upload_url, data=file_response.raw)
                if upload_response.status_code == 201:
                    print('Файл успешно загружен на Яндекс.Диск.')
                    return True
                else:
                    print(f'Ошибка загрузки файла: {upload_response.status_code} {upload_response.text}')
                    return False
            else:
                print(f'Ошибка скачивания файла: {file_response.status_code} {file_response.text}')
                return False
    elif response.status_code == 409:
        print(f'Путь {remote_path} не существует.')
        folder_path = remote_path.rsplit('/', 1)[0]  # Извлекаем путь к папке
        create_folder(folder_path)
        return upload_file_from_url(file_url, remote_path)  # Повторная загрузка
    else:
        print(f'Ошибка получения URL для загрузки: {response.status_code} {response.text}')
        return False

def handle(params):
    """Обрабатывает параметры и загружает файл на Яндекс.Диск"""
    data = json.loads(params)
    file_url = data['dir']  # URL изображения
    remote_file_path = data['file_path']
    r = upload_file_from_url(data['file_path'], f"disk:{data['dir']}{data['file_path'].split('.')[-2][:10]}.{data['file_path'].split('.')[-1]}")
    return json.dumps({'res': r})


# params = {
#     'dir':"testDir",
#     'file_path':"test.txt",
#     'username':"user"
# }

