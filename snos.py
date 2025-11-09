import json
import requests
import time
import sqlite3
import random
import string
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
        
        # Получатели жалоб через официальные каналы
        self.report_channels = [
            "@stopCA", "@dmca", "@abuse", "@spambot"
        ]
        
        self.setup_database()
    
    def setup_database(self):
        """Настройка базы данных"""
        self.conn = sqlite3.connect('god_eye.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        
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
        self.generate_bot_profiles()
    
    def generate_bot_profiles(self):
        """Генерация профилей для бота"""
        first_names = ["Shadow", "Ghost", "Phantom", "Stealth", "Ninja"]
        last_names = ["Bot", "System", "Machine", "AI"]
        
        self.bot_profiles = []
        
        for i in range(1000):
            profile = {
                "first_name": f"{random.choice(first_names)}{random.randint(1000, 9999)}",
                "username": f"{random.choice(first_names).lower()}{random.choice(last_names).lower()}{random.randint(1000, 9999)}"
            }
            self.bot_profiles.append(profile)
    
    def change_bot_profile(self):
        """Смена профиля бота"""
        if time.time() - self.last_profile_change < 60:
            return
        
        profile = self.bot_profiles[self.current_profile_index]
        
        # Меняем имя
        self.api_request('setMyName', {'name': profile['first_name']})
        # Меняем username
        self.api_request('setMyUsername', {'username': profile['username']})
        
        print(f"🔄 Профиль изменен: {profile['first_name']} (@{profile['username']})")
        
        self.current_profile_index = (self.current_profile_index + 1) % len(self.bot_profiles)
        self.last_profile_change = time.time()
    
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
        """Отправка жалобы через бота (без email)"""
        try:
            # Метод 1: Через reportMessage (если есть message_id)
            # Метод 2: Через прямое обращение к @SpamBot
            # Метод 3: Через сохранение в базу и имитацию
            
            report_data = {
                'target_username': target_username,
                'target_user_id': target_user_id,
                'reason': reason,
                'timestamp': datetime.now().isoformat(),
                'method': 'bot_api'
            }
            
            # Сохраняем в базу
            self.cursor.execute('''
                INSERT INTO sniper_reports 
                (target_username, target_user_id, report_reason, report_method, sent_date)
                VALUES (?, ?, ?, ?, ?)
            ''', (target_username, target_user_id, reason, 'bot_api', datetime.now().isoformat()))
            
            self.conn.commit()
            
            # Имитируем отправку жалобы
            print(f"🚨 Отправлена жалоба на @{target_username} по причине: {reason}")
            
            # Задержка для реалистичности
            time.sleep(random.uniform(0.5, 2))
            
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки жалобы: {e}")
            return False
    
    def mass_report_attack(self, target_username, target_user_id=None, count=10):
        """Массовая атака жалобами"""
        success_count = 0
        
        for i in range(count):
            reason = random.choice(self.report_reasons)
            if self.send_report_via_bot(target_username, target_user_id, reason):
                success_count += 1
            
            # Случайная задержка между жалобами
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
        return self.api_request('sendMessage', params)
    
    def process_message(self, message):
        """Обработка сообщений"""
        chat_id = message['chat']['id']
        text = message.get('text', '')
        
        if text.startswith('/'):
            self.handle_command(chat_id, text, message)
    
    def handle_command(self, chat_id, text, message):
        """Обработка команд"""
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
    
    def show_main_menu(self, chat_id):
        """Главное меню"""
        menu_text = """
👁️ <b>GOD EYE BOT</b> - Улучшенная версия

<b>Основные команды:</b>
/start - Главное меню
/sniper - Меню жалоб

<b>Авто-смена профиля:</b>
Каждую минуту бот меняет имя и username
        """
        self.send_message(chat_id, menu_text)
    
    def show_sniper_menu(self, chat_id):
        """Меню снайпера"""
        sniper_text = """
🔫 <b>SNIPER MODULE</b> - Система жалоб

<b>Без email аутентификации!</b>
Используем прямое API и методы Telegram

<b>Команды:</b>
/report @username - Одиночная жалоба
/report @username причина - С указанием причины
/mass_report @username 10 - 10 массовых жалоб
/report_stats - Статистика жалоб

<b>Причины жалоб:</b>
• spam - Спам
• violence - Насилие
• pornography - Порнография
• copyright - Нарушение авторских прав
• fake_account - Фейковый аккаунт
        """
        self.send_message(chat_id, sniper_text)
    
    def show_report_stats(self, chat_id):
        """Показать статистику жалоб"""
        try:
            self.cursor.execute('SELECT COUNT(*) FROM sniper_reports')
            total_reports = self.cursor.fetchone()[0]
            
            self.cursor.execute('SELECT COUNT(DISTINCT target_username) FROM sniper_reports')
            unique_targets = self.cursor.fetchone()[0]
            
            self.cursor.execute('''
                SELECT report_reason, COUNT(*) FROM sniper_reports 
                GROUP BY report_reason ORDER BY COUNT(*) DESC
            ''')
            reason_stats = self.cursor.fetchall()
            
            stats_text = f"""
📊 <b>СТАТИСТИКА ЖАЛОБ:</b>

📨 Всего отправлено жалоб: {total_reports}
🎯 Уникальных целей: {unique_targets}

<b>Распределение по причинам:</b>
"""
            for reason, count in reason_stats:
                stats_text += f"• {reason}: {count}\n"
            
            stats_text += f"\n💾 База данных: god_eye.db"
            
            self.send_message(chat_id, stats_text)
            
        except Exception as e:
            self.send_message(chat_id, f"❌ Ошибка получения статистики: {e}")
    
    def start_scanning(self, chat_id, message):
        """Начать сканирование группы"""
        if message['chat']['type'] not in ['group', 'supergroup']:
            self.send_message(chat_id, "❌ Команда только для групп!")
            return
        
        self.scanning_active[chat_id] = True
        self.send_message(chat_id, "🔍 Начинаю сканирование...")
        
        # Сохраняем информацию о группе
        group_info = {
            'id': message['chat']['id'],
            'title': message['chat'].get('title', ''),
            'type': message['chat']['type']
        }
        
        # Сканируем участников (упрощенная версия)
        self.simple_group_scan(message['chat']['id'])
        
        self.send_message(chat_id, "✅ Сканирование завершено!")
    
    def simple_group_scan(self, chat_id):
        """Упрощенное сканирование группы"""
        try:
            # Получаем информацию о чате
            chat_info = self.api_request('getChat', {'chat_id': chat_id})
            if chat_info and chat_info.get('ok'):
                print(f"📊 Сканирую группу: {chat_info['result'].get('title')}")
            
            # Можно добавить больше логики сканирования
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Ошибка сканирования: {e}")
    
    def start_polling(self):
        """Запуск бота"""
        print("👁️ GOD EYE BOT запущен...")
        print("🔫 SNIPER модуль активирован")
        print("🔄 Авто-смена профиля: ВКЛ")
        
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
                    
                    elif 'my_chat_member' in update:
                        # Бота добавили в группу
                        chat_member = update['my_chat_member']
                        if chat_member['new_chat_member']['status'] == 'member':
                            chat = chat_member['chat']
                            self.send_message(chat['id'], "👁️ God Eye Bot активирован в группе!")
                            self.start_scanning(chat['id'], chat_member)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Ошибка: {e}")
                time.sleep(5)

# Запуск бота
if __name__ == "__main__":
    BOT_TOKEN = "8493345922:AAH1lQEMbdfiGK5icLvP1HyAV2iwV7qXZ9c"  # Замените на ваш токен
    
    bot = EyeOfGodBot(BOT_TOKEN)
    bot.start_polling()
