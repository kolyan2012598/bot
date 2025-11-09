import json
import requests
import time
import sqlite3
import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
        
        # Базы данных для снайпера
        self.senders = {
            'sanya.dragonov@mail.ru': 'RakuzanSnos',
            'avyavya.vyaavy@mail.ru': 'zmARvx1MRvXppZV6xkXj',
            'gdfds98@mail.ru': '1CtFuHTaQxNda8X06CaQ',
            'dfsdfdsfdf51@mail.ru': 'SXxrCndCR59s5G9sGc6L',
            'aria.therese.svensson@mail.com': 'Zorro1ab',
            'taterbug@verizon.net': 'Holly1!',
            'ejbrickner@comcast.net': 'Pass1178',
            'teressapeart@cox.net': 'Quinton2329!',
            'liznees@verizon.net': 'Dancer008',
            'olajakubovich@mail.com': 'OlaKub2106OlaKub2106',
            'kcdg@charter.net': 'Jennifer3*',
            'bean_118@hotmail.com': 'Liverpool118!',
            'dsdhjas@mail.com': 'LONGHACH123',
            'robitwins@comcast.net': 'May241996',
            'wasina@live.com': 'Marlas21',
            'aruzhan.01@mail.com': '1234567!',
            'rob.tackett@live.com': 'metallic',
            'lindahallenbeck@verizon.net': 'Anakin@2014',
            'hlaw82@mail.com': 'Snoopy37$$',
            'paintmadman@comcast.net': 'mycat2200*',
            'prideandjoy@verizon.net': 'Ihatejen12',
            'sdgdfg56@mail.com': 'kenwood4201',
            'garrett.danelz@comcast.net': 'N11golfer!',
            'gillian_1211@hotmail.com': 'Gilloveu1211',
            'sunpit16@hotmail.com': 'Putter34!',
            'fdshelor@verizon.net': 'Masco123*',
            'yeags1@cox.net': 'Zoomom1965!',
            'amine002@usa.com': 'iScrRoXAei123',
            'bbarcelo16@cox.net': 'Bsb161089$$',
            'laliebert@hotmail.com': 'pirates2',
            'vallen285@comcast.net': 'Delft285!1!',
            'sierra12@email.com': 'tegen1111',
            'luanne.zapevalova@mail.com': 'FqWtJdZ5iN@',
            'kmay@windstream.net': 'Nascar98',
            'redbrick1@mail.com': 'Redbrick11',
            'ivv9ah7f@mail.com': 'K226nw8duwg',
            'erkobir@live.com': 'floydLAWTON019',
            'Misscarter@mail.com': 'ashtray19',
            'carlieruby10@cox.net': 'Lollypop789$',
            'blackops2013@mail.com': 'amason123566',
            'caroline_cullum@comcast.net': 'carter14',
            'dpb13@live.com': 'Ic&ynum13',
            'heirhunter@usa.com': 'Noguys@714',
            'sherri.edwards@verizon.net': 'Dreaming123#',
            'rami.rami1980@hotmail.com': 'ramirami1980',
            'jmsingleton2@comcast.net': '151728Jn$$',
            'aberancho@aol.com': '10diegguuss10',
            'dgidel@iowatelecom.net': 'Buster48',
            'gpopandopul@mail.com': 'GEORG62A',
            'bolgodonsk@mail.com': '012345678!',
            'colbycolb@cox.net': 'Signals@1'
        }
        
        self.receivers = ['stopCA@telegram.org', 'dmca@telegram.org', 'abuse@telegram.org',
                         'sticker@telegram.org', 'support@telegram.org']
        
        self.setup_database()
    
    def setup_database(self):
        """Настройка базы данных"""
        self.conn = sqlite3.connect('eye_of_god.db', check_same_thread=False)
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
            CREATE TABLE IF NOT EXISTS groups (
                group_id INTEGER PRIMARY KEY,
                group_title TEXT,
                member_count INTEGER,
                created_date TEXT
            )
        ''')
        
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sniper_targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_username TEXT,
                target_user_id INTEGER,
                reports_sent INTEGER DEFAULT 0,
                last_report_date TEXT,
                status TEXT DEFAULT 'active'
            )
        ''')
        
        self.conn.commit()
        self.generate_bot_profiles()
    
    def generate_bot_profiles(self):
        """Генерация профилей для бота"""
        first_names = ["Shadow", "Ghost", "Phantom", "Stealth", "Ninja"]
        last_names = ["Bot", "System", "Machine", "AI"]
        domains = ["bot", "ai", "system", "net"]
        
        self.bot_profiles = []
        
        for i in range(1000):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            number = random.randint(1000, 9999)
            domain = random.choice(domains)
            
            profile = {
                "first_name": f"{first_name}{number}",
                "username": f"{first_name.lower()}{last_name.lower()}{number}.{domain}"
            }
            self.bot_profiles.append(profile)
    
    def change_bot_profile(self):
        """Смена профиля бота"""
        if time.time() - self.last_profile_change < 60:
            return
        
        if self.current_profile_index >= len(self.bot_profiles):
            self.current_profile_index = 0
        
        profile = self.bot_profiles[self.current_profile_index]
        
        name_params = {'name': profile['first_name']}
        username_params = {'username': profile['username']}
        
        self.api_request('setMyName', name_params)
        self.api_request('setMyUsername', username_params)
        
        print(f"🔄 Профиль изменен: {profile['first_name']} (@{profile['username']})")
        self.current_profile_index += 1
        self.last_profile_change = time.time()
    
    def send_email_report(self, target_username, target_user_id=None, reason="violence"):
        """Отправка жалобы по email"""
        try:
            # Выбираем случайного отправителя
            sender_email = random.choice(list(self.senders.keys()))
            sender_password = self.senders[sender_email]
            
            # Выбираем случайного получателя
            receiver_email = random.choice(self.receivers)
            
            # Создаем сообщение
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = receiver_email
            msg['Subject'] = f"Жалоба на пользователя Telegram @{target_username}"
            
            # Текст жалобы
            body = f"""
            Уважаемая администрация Telegram,
            
            Я хочу сообщить о нарушении пользователем @{target_username} (ID: {target_user_id}) правил платформы.
            
            Причина жалобы: {reason}
            
            Данный пользователь нарушает правила Telegram путем:
            - Распространения запрещенного контента
            - Нарушения правил сообщества
            - Неадекватного поведения
            
            Прошу принять соответствующие меры.
            
            С уважением,
            Пользователь Telegram
            """
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Отправка через SMTP
            if 'mail.ru' in sender_email:
                server = smtplib.SMTP('smtp.mail.ru', 587)
            elif 'gmail.com' in sender_email:
                server = smtplib.SMTP('smtp.gmail.com', 587)
            else:
                server = smtplib.SMTP('smtp.mail.com', 587)
            
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, receiver_email, text)
            server.quit()
            
            # Сохраняем в базу
            self.cursor.execute('''
                INSERT INTO sniper_targets 
                (target_username, target_user_id, reports_sent, last_report_date)
                VALUES (?, ?, 1, ?)
            ''', (target_username, target_user_id, datetime.now().isoformat()))
            
            self.conn.commit()
            
            print(f"📧 Отправлена жалоба от {sender_email} на @{target_username}")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка отправки email: {e}")
            return False
    
    def mass_email_report(self, target_username, target_user_id=None, count=5):
        """Массовая отправка жалоб по email"""
        success_count = 0
        
        for i in range(count):
            if self.send_email_report(target_username, target_user_id, f"violation_{i+1}"):
                success_count += 1
                time.sleep(2)  # Задержка между отправками
        
        # Обновляем счетчик в базе
        self.cursor.execute('''
            UPDATE sniper_targets 
            SET reports_sent = reports_sent + ?, last_report_date = ?
            WHERE target_username = ?
        ''', (success_count, datetime.now().isoformat(), target_username))
        
        self.conn.commit()
        
        return success_count
    
    def api_request(self, method, params=None):
        """API запрос к Telegram"""
        url = self.base_url + method
        try:
            response = requests.post(url, json=params, timeout=10)
            return response.json()
        except Exception as e:
            print(f"Ошибка API: {e}")
            return None
    
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
        
        elif text.startswith('/sniper_report '):
            args = text.split(' ')
            if len(args) >= 2:
                username = args[1].replace('@', '')
                count = int(args[2]) if len(args) >= 3 else 1
                self.send_message(chat_id, f"🔫 Начинаю снайперскую атаку на @{username}...")
                success = self.mass_email_report(username, count=count)
                self.send_message(chat_id, f"✅ Отправлено {success} жалоб на @{username}")
        
        elif text.startswith('/mass_sniper '):
            args = text.split(' ')
            if len(args) >= 2:
                username = args[1].replace('@', '')
                self.send_message(chat_id, f"💥 Запускаю МАССОВУЮ атаку на @{username}...")
                success = 0
                for i in range(5):  # 5 волн по 3 жалобы
                    wave_success = self.mass_email_report(username, count=3)
                    success += wave_success
                    time.sleep(5)
                self.send_message(chat_id, f"🎯 Массовая атака завершена! Всего отправлено {success} жалоб на @{username}")

        elif text == '/startscan':
            self.start_scanning(chat_id, message)

        elif text == '/stopscan':
            self.stop_scanning(chat_id)

        elif text.startswith('/exit '):
            self.kick_user(chat_id, text, message)

        elif text == '/stats':
            self.show_stats(chat_id)

    def show_main_menu(self, chat_id):
        """Главное меню"""
        menu_text = """
👁️ <b>ГЛАЗ БОГА</b> - Полная система контроля

<b>Основные команды:</b>
/startscan - Сканировать участников группы
/stopscan - Остановить сканирование
/exit @username - Исключить пользователя
/stats - Статистика

<b>SNIPER MODULE:</b>
/sniper - Меню снайпера
/sniper_report @username 5 - 5 жалоб по email
/mass_sniper @username - Массовая атака (15+ жалоб)

<b>Авто-смена:</b>
Профиль меняется каждую минуту
        """
        self.send_message(chat_id, menu_text)

    def show_sniper_menu(self, chat_id):
        """Меню снайпера"""
        sniper_text = """
🔫 <b>SNIPER MODULE</b> - Email жалобы в Telegram

<b>Базы данных:</b>
• 50+ email аккаунтов для отправки
• 5 получателей в Telegram
• Авто-ротация отправителей

<b>Команды:</b>
/sniper_report @username - 1 жалоба
/sniper_report @username 5 - 5 жалоб
/mass_sniper @username - Массовая атака (15+)

<b>Получатели:</b>
@stopCA, @dmca, @abuse, @sticker, @support
        """
        self.send_message(chat_id, sniper_text)

    def start_scanning(self, chat_id, message):
        """Начать сканирование группы"""
        if message['chat']['type'] not in ['group', 'supergroup']:
            self.send_message(chat_id, "❌ Эта команда работает только в группах!")
            return

        self.scanning_active[chat_id] = True
        self.send_message(chat_id, "🔍 Начинаю сканирование участников группы...")

        # Сканируем администраторов
        admins = self.get_chat_administrators(chat_id)
        if admins and 'result' in admins:
            for admin in admins['result']:
                self.save_user_info(admin['user'], chat_id)

        # Сканируем участников
        self.scan_group_members(chat_id)
        self.send_message(chat_id, "✅ Сканирование завершено!")

    def stop_scanning(self, chat_id):
        """Остановить сканирование"""
        if chat_id in self.scanning_active:
            self.scanning_active[chat_id] = False
            self.send_message(chat_id, "⏹️ Сканирование остановлено")

    def kick_user(self, chat_id, text, message):
        """Исключить пользователя из группы"""
        if 'reply_to_message' in message:
            user_id = message['reply_to_message']['from']['id']
            result = self.ban_chat_member(chat_id, user_id)
            if result and result.get('ok'):
                self.send_message(chat_id, f"✅ Пользователь исключен!")
            else:
                self.send_message(chat_id, f"❌ Не удалось исключить пользователя")
        else:
            args = text.split(' ')
            if len(args) >= 2:
                username = args[1].replace('@', '')
                self.send_message(chat_id, f"🔄 Ищу пользователя @{username}...")

    def show_stats(self, chat_id):
        """Показать статистику"""
        self.cursor.execute('SELECT COUNT(*) FROM users')
        user_count = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM groups')
        group_count = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT COUNT(*) FROM sniper_targets')
        targets_count = self.cursor.fetchone()[0]

        self.cursor.execute('SELECT SUM(reports_sent) FROM sniper_targets')
        reports_count = self.cursor.fetchone()[0] or 0

        stats_text = f"""
📊 <b>СТАТИСТИКА СИСТЕМЫ:</b>

👥 <b>Пользователей в базе:</b> {user_count}
💬 <b>Групп под наблюдением:</b> {group_count}
🎯 <b>Целей для снайпера:</b> {targets_count}
📧 <b>Отправлено жалоб:</b> {reports_count}

⚡ <b>SNIPER база:</b>
• Аккаунтов: {len(self.senders)}
• Получателей: {len(self.receivers)}
• Профилей бота: {len(self.bot_profiles)}
        """
        self.send_message(chat_id, stats_text)

    def get_chat_administrators(self, chat_id):
        """Получить администраторов чата"""
        params = {'chat_id': chat_id}
        return self.api_request('getChatAdministrators', params)

    def ban_chat_member(self, chat_id, user_id):
        """Забанить пользователя"""
        params = {'chat_id': chat_id, 'user_id': user_id}
        return self.api_request('banChatMember', params)

    def save_user_info(self, user_data, group_id=None):
        """Сохранить информацию о пользователе"""
        user_id = user_data['id']
        username = user_data.get('username', '')
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')

        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        self.cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, username, first_name, last_name, registration_date, last_activity, group_id)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, last_name, now, now, group_id))

        self.conn.commit()

    def scan_group_members(self, chat_id):
        """Сканировать участников группы"""
        try:
            print(f"🔍 Сканирую группу {chat_id}...")
            # Здесь можно добавить логику сканирования участников
            time.sleep(2)
        except Exception as e:
            print(f"❌ Ошибка сканирования: {e}")

    def start_polling(self):
        """Запуск бота"""
        print("👁️ Глаз Бога запущен...")
        print(f"🔫 SNIPER модуль: {len(self.senders)} аккаунтов")
        print(f"🔄 Авто-смена: {len(self.bot_profiles)} профилей")

        while True:
            try:
                # Меняем профиль каждую минуту
                self.change_bot_profile()

                # Получаем обновления
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
                            self.send_message(chat['id'], "👁️ Глаз Бога активирован!")
                            self.start_scanning(chat['id'], chat_member)

                time.sleep(1)

            except Exception as e:
                print(f"❌ Ошибка: {e}")
                time.sleep(5)

# Запуск бота
if __name__ == "__main__":
    BOT_TOKEN = "8493345922:AAH1lQEMbdfiGK5icLvP1HyAV2iwV7qXZ9c"
    
    bot = EyeOfGodBot(BOT_TOKEN)
    bot.start_polling()
