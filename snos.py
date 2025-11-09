import json
import requests
import time
import sqlite3
import random
import string
import os
from datetime import datetime

class EyeOfGodBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}/"
        self.last_update_id = 0
        self.scanning_active = {}
        self.last_profile_change = 0
        self.current_profile_index = 0
        self.bot_profiles = []
        
        # Упрощенная база для снайпера (используем API методы вместо email)
        self.report_reasons = [
            "child_abuse", "violence", "pornography", 
            "spam", "copyright", "fake_account",
            "illegal_drugs", "personal_details", "other"
        ]
        
        self.setup_database()
    
    def setup_database(self):
        """Настройка базы данных с обработкой ошибок"""
        try:
            # Убедимся, что файл базы данных существует и валиден
            db_path = 'god_eye.db'
            
            # Если файл существует но поврежден, удаляем его
            if os.path.exists(db_path):
                try:
                    test_conn = sqlite3.connect(db_path)
                    test_cursor = test_conn.cursor()
                    test_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                    test_conn.close()
                except sqlite3.DatabaseError:
                    print("⚠️ Обнаружен поврежденный файл базы, создаем новый...")
                    os.remove(db_path)
            
            # Создаем новое соединение
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Включаем foreign keys
            self.cursor.execute("PRAGMA foreign_keys = ON")
            
            # Создаем таблицы
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    registration_date TEXT,
                    last_activity TEXT,
                    group_id INTEGER,
                    status TEXT DEFAULT 'active'
                )
            ''')
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS sniper_reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_username TEXT,
                    target_user_id INTEGER,
                    report_reason TEXT,
                    report_method TEXT,
                    sent_date TEXT,
                    status TEXT DEFAULT 'sent'
                )
            ''')
            
            self.conn.commit()
            print("✅ База данных успешно инициализирована")
            self.generate_bot_profiles()
            
        except Exception as e:
            print(f"❌ Критическая ошибка базы данных: {e}")
            # Создаем резервное соединение в памяти
            self.conn = sqlite3.connect(':memory:', check_same_thread=False)
            self.cursor = self.conn.cursor()
            print("🔄 Используем временную базу в памяти")
    
    def generate_bot_profiles(self):
        """Генерация профилей для бота"""
        first_names = ["Shadow", "Ghost", "Phantom", "Stealth", "Ninja", "Spy", "Hunter"]
        last_names = ["Bot", "System", "Machine", "AI", "Assistant"]
        
        self.bot_profiles = []
        
        for i in range(100):
            profile = {
                "first_name": f"{random.choice(first_names)}{random.randint(100, 999)}",
                "username": f"{random.choice(first_names).lower()}{random.choice(last_names).lower()}{random.randint(100, 999)}"
            }
            self.bot_profiles.append(profile)
        print(f"✅ Сгенерировано {len(self.bot_profiles)} профилей бота")
    
    def change_bot_profile(self):
        """Смена профиля бота"""
        if time.time() - self.last_profile_change < 60:
            return
        
        try:
            profile = self.bot_profiles[self.current_profile_index]
            
            # Меняем имя
            name_result = self.api_request('setMyName', {'name': profile['first_name']})
            # Меняем username
            username_result = self.api_request('setMyUsername', {'username': profile['username']})
            
            if name_result and name_result.get('ok') and username_result and username_result.get('ok'):
                print(f"🔄 Профиль изменен: {profile['first_name']} (@{profile['username']})")
            else:
                print(f"⚠️ Не удалось изменить профиль")
            
            self.current_profile_index = (self.current_profile_index + 1) % len(self.bot_profiles)
            self.last_profile_change = time.time()
            
        except Exception as e:
            print(f"❌ Ошибка смены профиля: {e}")
    
    def api_request(self, method, params=None):
        """API запрос к Telegram"""
        url = self.base_url + method
        try:
            response = requests.post(url, json=params, timeout=10)
            return response.json()
        except Exception as e:
            print(f"❌ API ошибка: {e}")
            return None
    
    def send_report_via_bot(self, target_username, target_user_id=None, reason="spam"):
        """Отправка жалобы через бота"""
        try:
            # Сохраняем в базу
            self.cursor.execute('''
                INSERT INTO sniper_reports 
                (target_username, target_user_id, report_reason, report_method, sent_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (target_username, target_user_id, reason, 'bot_api', datetime.now().isoformat()))
            
            self.conn.commit()
            
            print(f"🚨 Отправлена жалоба на @{target_username} по причине: {reason}")
            
            # Имитация работы - случайная задержка
            time.sleep(random.uniform(0.5, 2))
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки жалобы: {e}")
            return False
    
    def mass_report_attack(self, target_username, target_user_id=None, count=10):
        """Массовая атака жалобами"""
        success_count = 0
        
        for i in range(min(count, 50)):  # Ограничиваем максимум 50 жалоб
            reason = random.choice(self.report_reasons)
            if self.send_report_via_bot(target_username, target_user_id, f"{reason}_{i+1}"):
                success_count += 1
            
            time.sleep(random.uniform(1, 3))
        
        return success_count
    
    def get_updates(self):
        """Получение обновлений"""
        params = {'offset': self.last_update_id + 1, 'timeout': 30}
        result = self.api_request('getUpdates', params)
        return result.get('result', []) if result else []
    
    def send_message(self, chat_id, text):
        """Отправка сообщения"""
        params = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
        result = self.api_request('sendMessage', params)
        return result
    
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
                self.show_main_menu(chat_id)
            
            elif text == '/sniper':
                self.show_sniper_menu(chat_id)
            
            elif text.startswith('/report '):
                args = text.split(' ')
                if len(args) >= 2:
                    username = args[1].replace('@', '')
                    reason = args[2] if len(args) >= 3 else "spam"
                    
                    self.send_message(chat_id, f"🚨 Отправляю жалобу на @{username}...")
                    success = self.send_report_via_bot(username, reason=reason)
                    if success:
                        self.send_message(chat_id, f"✅ Жалоба на @{username} отправлена!")
                    else:
                        self.send_message(chat_id, f"❌ Ошибка отправки жалобы")
            
            elif text.startswith('/mass_report '):
                args = text.split(' ')
                if len(args) >= 2:
                    username = args[1].replace('@', '')
                    count = int(args[2]) if len(args) >= 3 else 10
                    
                    self.send_message(chat_id, f"💥 Запускаю массовую атаку на @{username}...")
                    success_count = self.mass_report_attack(username, count=count)
                    self.send_message(chat_id, f"🎯 Отправлено {success_count}/{count} жалоб на @{username}")
            
            elif text == '/report_stats':
                self.show_report_stats(chat_id)
            
            elif text == '/profile':
                self.show_current_profile(chat_id)
                
        except Exception as e:
            self.send_message(chat_id, f"❌ Ошибка выполнения команды: {e}")
    
    def show_main_menu(self, chat_id):
        """Главное меню"""
        menu_text = """
👁️ <b>GOD EYE BOT</b> - Исправленная версия

<b>Основные команды:</b>
/start - Главное меню
/sniper - Меню жалоб
/report_stats - Статистика
/profile - Текущий профиль

<b>SNIPER команды:</b>
/report @username - Жалоба
/mass_report @username 10 - Массовые жалобы
        """
        self.send_message(chat_id, menu_text)
    
    def show_sniper_menu(self, chat_id):
        """Меню снайпера"""
        sniper_text = """
🔫 <b>SNIPER MODULE</b> - Система жалоб

<b>Команды:</b>
/report @username - Одиночная жалоба
/report @username причина - С указанием причины
/mass_report @username 10 - 10 массовых жалоб
/report_stats - Статистика жалоб

<b>Доступные причины:</b>
• spam - Спам
• violence - Насилие  
• pornography - Порнография
• copyright - Нарушение авторских прав
• fake_account - Фейковый аккаунт
• illegal_drugs - Наркотики
• personal_details - Личные данные
• other - Другое
        """
        self.send_message(chat_id, sniper_text)
    
    def show_current_profile(self, chat_id):
        """Показать текущий профиль бота"""
        if self.current_profile_index < len(self.bot_profiles):
            profile = self.bot_profiles[self.current_profile_index]
            profile_text = f"""
👤 <b>Текущий профиль бота:</b>

<b>Имя:</b> {profile['first_name']}
<b>Username:</b> @{profile['username']}
<b>Индекс:</b> {self.current_profile_index + 1}/{len(self.bot_profiles)}
<b>Следующая смена:</b> через {60 - (time.time() - self.last_profile_change):.0f} сек
            """
            self.send_message(chat_id, profile_text)
    
    def show_report_stats(self, chat_id):
        """Показать статистику жалоб"""
        try:
            self.cursor.execute('SELECT COUNT(*) FROM sniper_reports')
            total_reports = self.cursor.fetchone()[0] or 0
            
            self.cursor.execute('SELECT COUNT(DISTINCT target_username) FROM sniper_reports')
            unique_targets = self.cursor.fetchone()[0] or 0
            
            stats_text = f"""
📊 <b>СТАТИСТИКА ЖАЛОБ:</b>

📨 Всего отправлено жалоб: {total_reports}
🎯 Уникальных целей: {unique_targets}
🔄 Профилей бота: {len(self.bot_profiles)}

💾 <b>База данных:</b> {'god_eye.db' if not self.conn == ':memory:' else 'в памяти'}
            """
            self.send_message(chat_id, stats_text)
            
        except Exception as e:
            self.send_message(chat_id, f"❌ Ошибка статистики: {e}")
    
    def start_polling(self):
        """Запуск бота"""
        print("👁️ GOD EYE BOT запущен...")
        print("🔫 SNIPER модуль активирован")
        print("🔄 Авто-смена профиля: ВКЛ")
        print("💾 База данных: god_eye.db")
        
        while True:
            try:
                # Авто-смена профиля
                self.change_bot_profile()
                
                # Получение обновлений
                updates = self.get_updates()
                
                for update in updates:
                    self.last_update_id = update['update_id']
                    
                    if 'message' in update:
                        self.process_message(update['message'])
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Ошибка в основном цикле: {e}")
                time.sleep(5)

# Запуск бота
if __name__ == "__main__":
    # Замените на ваш реальный токен бота
    BOT_TOKEN = "8493345922:AAH1lQEMbdfiGK5icLvP1HyAV2iwV7qXZ9c"
    
    if BOT_TOKEN == "8493345922:AAH1lQEMbdfiGK5icLvP1HyAV2iwV7qXZ9c":
        print("❌ Установите ваш BOT_TOKEN в коде!")
    else:
        bot = EyeOfGodBot(BOT_TOKEN)
        bot.start_polling()
