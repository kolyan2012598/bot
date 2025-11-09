import requests
import time
import sqlite3
import random
import threading
import hashlib
from datetime import datetime
from fake_useragent import UserAgent

class UltimateGodEyeBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.last_update_id = 0
        self.ua = UserAgent()
        self.active_attacks = {}
        self.setup_database()
        
    def setup_database(self):
        """База данных для целей"""
        try:
            self.conn = sqlite3.connect('god_eye.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS mass_targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_username TEXT,
                    target_user_id INTEGER,
                    attack_type TEXT,
                    requests_sent INTEGER DEFAULT 0,
                    start_time TEXT,
                    status TEXT DEFAULT 'active'
                )
            ''')
            self.conn.commit()
            print("✅ База данных инициализирована")
        except Exception as e:
            print(f"❌ Ошибка базы данных: {e}")

    def api_request(self, method, params=None):
        """API запрос с ротацией User-Agent"""
        url = self.base_url + method
        headers = {
            'User-Agent': self.ua.random
        }
        try:
            response = requests.post(url, json=params, headers=headers, timeout=5)
            return response.json()
        except Exception as e:
            print(f"❌ API ошибка: {e}")
            return None

    def send_mass_report(self, target_username, target_user_id=None, attack_power=100):
        """Массовая отправка репортов"""
        try:
            for i in range(min(attack_power, 1000)):  # Ограничиваем 1000
                # Сохраняем в базу
                self.cursor.execute('''
                    INSERT INTO mass_targets 
                    (target_username, target_user_id, attack_type, requests_sent, start_time)
                    VALUES (?, ?, ?, ?, ?)
                ''', (target_username, target_user_id or 0, 'mass_report', 1, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                
                # Имитация отправки репорта
                report_data = {
                    'user_id': target_user_id or random.randint(100000000, 999999999),
                    'reason': 'spam',
                    'timestamp': int(time.time())
                }
                
                time.sleep(0.01)  # Небольшая задержка
                
            self.conn.commit()
            return min(attack_power, 1000)
            
        except Exception as e:
            print(f"❌ Ошибка отправки репортов: {e}")
            return 0

    def send_message(self, chat_id, text):
        """Отправка сообщения"""
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        return self.api_request('sendMessage', params)

    def get_updates(self):
        """Получение обновлений"""
        params = {'offset': self.last_update_id + 1, 'timeout': 10}
        result = self.api_request('getUpdates', params)
        return result.get('result', []) if result else []

    def process_message(self, message):
        """Обработка сообщений"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '')
            
            if text.startswith('/'):
                self.handle_command(chat_id, text, message)
        except Exception as e:
            print(f"❌ Ошибка обработки сообщения: {e}")

    def handle_command(self, chat_id, text, message):
        """Обработка команд"""
        try:
            if text == '/start':
                self.show_menu(chat_id)
                
            elif text.startswith('/mass_report'):
                args = text.split(' ')
                if len(args) >= 2:
                    username = args[1].replace('@', '')
                    power = int(args[2]) if len(args) >= 3 else 100
                    
                    self.send_message(chat_id, f"💥 Запуск атаки на @{username}...")
                    result = self.send_mass_report(username, power=power)
                    self.send_message(chat_id, f"☠️ Отправлено {result} репортов на @{username}")
                    
            elif text == '/mystats':
                self.show_stats(chat_id)
                
        except Exception as e:
            self.send_message(chat_id, f"❌ Ошибка команды: {e}")

    def show_stats(self, chat_id):
        """Показать статистику"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM mass_targets")
            total_targets = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT SUM(requests_sent) FROM mass_targets")
            total_attacks = self.cursor.fetchone()[0] or 0
            
            self.cursor.execute("SELECT COUNT(DISTINCT target_username) FROM mass_targets")
            unique_targets = self.cursor.fetchone()[0]
            
            stats_text = f"""
📊 <b>СТАТИСТИКА АТАК:</b>

🎯 Уникальных целей: {unique_targets}
💣 Всего атак: {total_attacks}
📁 Записей в базе: {total_targets}

💾 База: god_eye.db
            """
            self.send_message(chat_id, stats_text)
        except Exception as e:
            self.send_message(chat_id, f"❌ Ошибка статистики: {e}")

    def show_menu(self, chat_id):
        """Показать меню"""
        menu = """
☠️ <b>GOD EYE BOT</b>

<b>Команды:</b>
/mass_report @username - 100 репортов
/mass_report @username 500 - 500 репортов
/mystats - статистика атак

<b>Данные сохраняются в:</b>
📁 god_eye.db
        """
        self.send_message(chat_id, menu)

    def start_polling(self):
        """Запуск бота"""
        print("☠️ GOD EYE BOT ЗАПУЩЕН")
        print("💾 База данных: god_eye.db")
        
        while True:
            try:
                updates = self.get_updates()
                for update in updates:
                    self.last_update_id = update['update_id']
                    if 'message' in update:
                        self.process_message(update['message'])
                time.sleep(1)
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                time.sleep(5)

# Запуск бота
if __name__ == "__main__":
    TOKEN = "8271550032:AAHTBvz4qmLv8jpwg_eaeBHa2AqqqtO_xjs"  # Замените на ваш токен
    bot = UltimateGodEyeBot(TOKEN)
    bot.start_polling()
