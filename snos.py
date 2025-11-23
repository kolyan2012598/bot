import requests
import json
import time
import os
from datetime import datetime

# --- КОНФИГУРАЦИЯ ---
# 1. Токен бота
BOT_TOKEN = "8302491219:AAEGaJkcdwFSSuwn3X0y2NWjfHJJMqec5yA"
API_BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"

# 2. GROUP_CHAT_ID удален. Бот будет работать с chat_id из каждого обновления.

# Имя файла для сохранения лога (ОДИН ФАЙЛ для всех чатов)
LOG_FILE = "group_chat_log.txt"

# Переменная для Long Polling
last_update_id = 0

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ API (Без изменений) ---

def api_call(method, params=None, files=None):
    """Выполняет POST-запрос к Telegram Bot API."""
    url = API_BASE_URL + method
    try:
        if files:
            response = requests.post(url, params=params, files=files)
        else:
            response = requests.post(url, json=params)
            
        response.raise_for_status() 
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Ошибка API при вызове {method}: {e}")
        return None

def send_message(chat_id, text):
    """Отправляет текстовое сообщение в чат."""
    params = {'chat_id': chat_id, 'text': text}
    api_call("sendMessage", params)

def send_document(chat_id, file_path):
    """Отправляет сохраненный файл чата как документ."""
    try:
        with open(file_path, 'rb') as f:
            files = {'document': f}
            params = {'chat_id': chat_id}
            result = api_call("sendDocument", params=params, files=files)
            return result
    except FileNotFoundError:
        send_message(chat_id, "Ошибка: Файл истории чата не найден.")
    except Exception as e:
        print(f"Ошибка при отправке документа: {e}")
        send_message(chat_id, "Произошла ошибка при отправке файла.")

def get_updates(offset=None):
    """Получает новые обновления с помощью Long Polling."""
    params = {'timeout': 30, 'offset': offset}
    return api_call("getUpdates", params)

# --- ЛОГИКА БОТА ---

def log_message_to_file(message):
    """Сохраняет сообщение в локальный текстовый файл."""
    if 'text' not in message:
        return 

    user = message.get('from', {})
    
    username = user.get('username')
    if username:
        user_mention = f"@{username}"
    else:
        first_name = user.get('first_name', 'Неизвестный')
        last_name = user.get('last_name', '')
        user_mention = f"@{first_name} {last_name}".strip()

    timestamp = datetime.fromtimestamp(message['date']).strftime('%Y-%m-%d %H:%M:%S')
    text = message['text'].replace('\n', ' ') 
    
    # Добавляем ID чата в лог, чтобы хоть как-то различать, откуда пришло сообщение
    chat_id = message['chat']['id']
    log_entry = f"{timestamp};(Chat ID: {chat_id});{user_mention}; {text}\n"

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(log_entry)

def handle_updates(updates):
    """Обрабатывает полученные обновления."""
    global last_update_id
    
    if not updates or not updates.get('result'):
        return

    for update in updates['result']:
        last_update_id = update['update_id'] + 1
        
        message = update.get('message')
        if not message:
            continue

        # Определяем chat_id из текущего сообщения
        chat_id = message['chat']['id']

        text = message.get('text', '')
        
        # 1. Обработка команд
        if text.startswith('/chat_load'):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Вызвана /chat_load в чате {chat_id}. Отправка файла...")
            # Отправляем лог в чат, из которого пришла команда
            send_document(chat_id, LOG_FILE)
            send_message(chat_id, "Файл с историей чата отправлен.")
        
        elif text.startswith('/clear_file'):
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Вызвана /clear_file в чате {chat_id}. Удаление файла...")
            try:
                if os.path.exists(LOG_FILE):
                    os.remove(LOG_FILE)
                    send_message(chat_id, "Файл истории чата удален с компьютера создателя.")
                else:
                    send_message(chat_id, "Файл истории чата уже отсутствует.")
            except OSError as e:
                send_message(chat_id, f"Ошибка при удалении файла: {e}")
        
        # 2. Непрерывное логирование
        elif text: 
            log_message_to_file(message)

# --- ОСНОВНОЙ ЦИКЛ БОТА (Без изменений) ---

def run_bot():
    """Главный цикл бота (Long Polling)."""
    global last_update_id
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Бот запущен. Ожидание обновлений из ЛЮБЫХ чатов...")
    
    updates = get_updates()
    if updates and updates.get('result'):
        last_update_id = updates['result'][-1]['update_id'] + 1

    while True:
        try:
            updates = get_updates(last_update_id)
            if updates and updates.get('result'):
                handle_updates(updates)
            
        except requests.exceptions.ReadTimeout:
            pass
        except Exception as e:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Общая ошибка в цикле: {e}")
            time.sleep(5) 

if __name__ == '__main__':
    # Убедитесь, что модуль requests установлен: pip install requests
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\nБот остановлен пользователем.")
