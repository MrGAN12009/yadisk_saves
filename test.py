import requests
import json

# Ваш OAuth-токен, полученный через Yandex OAuth
TOKEN = ''

# Базовый URL для API Яндекс.Диска
BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'
UPLOAD_URL = f'{BASE_URL}/upload'

headers = {
    'Authorization': f'OAuth {TOKEN}'
}


def create_folder(folder_path):
    """Создаёт папку на Яндекс.Диске"""
    response = requests.put(BASE_URL, headers=headers, params={'path': folder_path})
    if response.status_code in (201, 409):  # Папка создана или уже существует
        print(f'Папка {folder_path} готова.')
    else:
        print(f'Ошибка создания папки {folder_path}: {response.status_code} {response.text}')


def upload_file_from_url(file_url, remote_path):
    """Загружает файл из URL напрямую на Яндекс.Диск"""
    # Получаем URL для загрузки на Яндекс.Диск
    params = {'path': remote_path, 'overwrite': 'true'}
    response = requests.get(UPLOAD_URL, headers=headers, params=params)

    if response.status_code == 200:
        upload_url = response.json().get('href')
        if not upload_url:
            print('Не удалось получить ссылку для загрузки файла.')
            return False

        # Потоковая загрузка файла из URL на Яндекс.Диск
        file_stream = requests.get(file_url, stream=True)
        if file_stream.status_code == 200:
            upload_response = requests.put(
                upload_url,
                data=file_stream.iter_content(chunk_size=1024),
                headers={'Content-Type': 'application/octet-stream'}  # Указываем тип контента
            )
            if upload_response.status_code == 201:
                print('Файл успешно загружен на Яндекс.Диск.')
                return True
            else:
                print(f'Ошибка загрузки файла: {upload_response.status_code} {upload_response.text}')
                return False
        else:
            print(f'Ошибка загрузки файла из URL: {file_stream.status_code} {file_stream.text}')
            return False
    elif response.status_code == 409:
        print(f'Путь {remote_path} не существует.')
        folder_path = remote_path.rsplit('/', 1)[0]  # Извлекаем путь к папке
        create_folder(folder_path)
        return upload_file_from_url(file_url, remote_path)  # Повторная загрузка
    else:
        print(f'Ошибка получения URL для загрузки: {response.status_code} {response.text}')
        return False


# Основной вызов
# params = {"file_path" : "https://files.salebot.pro/uploads/message_files/2643cf62625f3555284d45e955753e2758ed1f01872862d1d4365e6dd59d0dd2.jpg",
# 'dir' : '/'}
def handle(params):
    """Обрабатывает параметры и загружает файл на Яндекс.Диск"""
    data = json.loads(params)
    local_file_path = data['file_path']

    result = upload_file_from_url(local_file_path, f"disk:{data['dir']}{local_file_path.split('.')[-2][-5:]}{local_file_path.split('.')[-1]}")
    return json.dumps({'res': result})
