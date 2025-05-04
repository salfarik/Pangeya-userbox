from colorama import Fore, Style, init
import asyncio
import os
import random
from collections import defaultdict
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError
from telethon.tl.types import User
from datetime import datetime

init()




banner = '''
    ██▓███   ▄▄▄       ███▄    █   ▄████ ▓█████▓██   ██▓ ▄▄▄                     
   ▓██░  ██▒▒████▄     ██ ▀█   █  ██▒ ▀█▒▓█   ▀ ▒██  ██▒▒████▄                   
   ▓██░ ██▓▒▒██  ▀█▄  ▓██  ▀█ ██▒▒██░▄▄▄░▒███    ▒██ ██░▒██  ▀█▄                 
   ▒██▄█▓▒ ▒░██▄▄▄▄██ ▓██▒  ▐▌██▒░▓█  ██▓▒▓█  ▄  ░ ▐██▓░░██▄▄▄▄██                
   ▒██▒ ░  ░ ▓█   ▓██▒▒██░   ▓██░░▒▓███▀▒░▒████▒ ░ ██▒▓░ ▓█   ▓██▒               
   ▒▓▒░ ░  ░ ▒▒   ▓▒█░░ ▒░   ▒ ▒  ░▒   ▒ ░░ ▒░ ░  ██▒▒▒  ▒▒   ▓▒█░               
   ░▒ ░       ▒   ▒▒ ░░ ░░   ░ ▒░  ░   ░  ░ ░  ░▓██ ░▒░   ▒   ▒▒ ░               
   ░░         ░   ▒      ░   ░ ░ ░ ░   ░    ░   ▒ ▒ ░░    ░   ▒                  
                  ░  ░         ░       ░    ░  ░░ ░           ░  ░               
                                                ░ ░                  
                                                                  
                                             
 ┌───────────────────────┐          █    ██   ██████ ▓█████  ██▀███   ▄▄▄▄    ▒█████  ▒██   ██▒
 │ Version - 1           │          ██  ▓██▒▒██    ▒ ▓█   ▀ ▓██ ▒ ██▒▓█████▄ ▒██▒  ██▒▒▒ █ █ ▒░
 │ Creater - morti       │         ▓██  ▒██░░ ▓██▄   ▒███   ▓██ ░▄█ ▒▒██▒ ▄██▒██░  ██▒░░  █   ░ 
 │ price - 0$            │         ▓▓█  ░██░  ▒   ██▒▒▓█  ▄ ▒██▀▀█▄  ▒██░█▀  ▒██   ██░ ░ █ █ ▒     
 │ Channel - @vk2o17a    │         ▒▒█████▓ ▒██████▒▒░▒████▒░██▓ ▒██▒░▓█  ▀█▓░ ████▓▒░▒██▒ ▒██▒
 │ Level - Easy          │         ░▒▓▒ ▒ ▒ ▒ ▒▓▒ ▒ ░░░ ▒░ ░░ ▒▓ ░▒▓░░▒▓███▀▒░ ▒░▒░▒░ ▒▒ ░ ░▓ ░ 
 └───────────────────────┘         ░░▒░ ░ ░ ░ ░▒  ░ ░ ░ ░  ░  ░▒ ░ ▒░▒░▒   ░   ░ ▒ ▒░ ░░   ░▒ ░
                                   ░░░ ░ ░ ░  ░  ░     ░     ░░   ░  ░    ░ ░ ░ ░ ▒   ░    ░   
                                   ░           ░     ░  ░   ░      ░          ░ ░   ░    ░  
                                                                           ░                    
'''

class TrollBot:
    def __init__(self):
        self.active_trolls = defaultdict(set)
        self.active_ftrolls = set()
        self.client = None
        self.owner_id = None
        self.session_template = "unknown_session"
        self.templates = self.load_templates()
        self.used_phrases = []
        self.available_phrases = []
        self.reset_phrases()

    def reset_phrases(self):
        self.available_phrases = self.templates['phrases'].copy()
        random.shuffle(self.available_phrases)
        self.used_phrases = []

    def load_templates(self):
        templates = {
            'phrases': [],
            'dox_steps': [],
            'dox_report': '',
            'snos_steps': [],
            'messages': {}
        }
        
        try:
            with open("templates.txt", "r", encoding="utf-8") as f:
                current_section = None
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue
                    
                    if line.startswith('[') and line.endswith(']'):
                        current_section = line[1:-1]
                        continue
                    
                    if current_section == 'phrases':
                        templates['phrases'].append(line)
                    elif current_section == 'dox_steps':
                        templates['dox_steps'].append(line)
                    elif current_section == 'dox_report':
                        templates['dox_report'] += line + '\n'
                    elif current_section == 'snos_steps':
                        templates['snos_steps'].append(line)
                    elif current_section == 'messages':
                        if '=' in line:
                            key, value = line.split('=', 1)
                            templates['messages'][key.strip()] = value.strip()
        
        except FileNotFoundError:
            with open("templates.txt", "w", encoding="utf-8") as f:
                f.write("""[phrases]
[dox_steps]
[dox_report]
[snos_steps]
[messages]""")
        
        return templates

    def get_random_phrase(self, text):
        if not self.available_phrases:
            self.reset_phrases()
        
        phrase = self.available_phrases.pop()
        self.used_phrases.append(phrase)
        return phrase.format(text=text)

    def save_api_config(self, api_id, api_hash):
        with open("api_config.txt", "w") as f:
            f.write(f"{api_id}\n{api_hash}")

    def load_api_config(self):
        try:
            with open("api_config.txt", "r") as f:
                return int(f.readline().strip()), f.readline().strip()
        except FileNotFoundError:
            return None, None

    async def init_client(self):
        print("---- Настройка сессии ----")
        if self.find_existing_sessions():
            return await self.connect_existing_session()
        return await self.create_new_session()

    def find_existing_sessions(self):
        return any(fname.endswith(".session") for fname in os.listdir())

    async def connect_existing_session(self):
        session_files = [fname for fname in os.listdir() if fname.endswith(".session")]
        print("Доступные сессии:")
        for i, fname in enumerate(session_files, 1):
            print(f"{i}. {fname}")
        
        choice = int(input("Выберите номер сессии: ")) - 1
        self.session_template = session_files[choice].split(".")[0]
        
        api_id, api_hash = self.load_api_config()
        if not api_id or not api_hash:
            api_id = int(input("Введите API ID для этой сессии: "))
            api_hash = input("Введите API Hash: ")
            self.save_api_config(api_id, api_hash)
        
        self.client = TelegramClient(self.session_template, api_id, api_hash)
        
        try:
            await self.client.connect()
            if await self.client.is_user_authorized():
                me = await self.client.get_me()
                self.owner_id = me.id
                return True
                
            print("❌ Требуется повторная авторизация!")
            return await self.auth_user()
            
        except Exception as e:
            print(f"Ошибка подключения: {str(e)}")
            return False

    async def create_new_session(self):
        api_id = int(input("Введите API ID: "))
        api_hash = input("Введите API Hash: ")
        self.save_api_config(api_id, api_hash)
        
        phone = input("Введите номер телефона: ").strip().replace("+", "")
        
        version = 1
        self.session_template = f"{phone}_{version}"
        while os.path.exists(f"{self.session_template}.session"):
            version += 1
            self.session_template = f"{phone}_{version}"
        
        self.client = TelegramClient(self.session_template, api_id, api_hash)

        try:
            await self.client.connect()
            if not await self.client.is_user_authorized():
                await self.auth_user()
                
            me = await self.client.get_me()
            self.owner_id = me.id
            return True
            
        except Exception as e:
            print(f"Ошибка создания сессии: {str(e)}")
            return False

    async def auth_user(self):
        phone = input("Номер телефона: ")
        await self.client.send_code_request(phone)
        code = input("Код подтверждения: ")
        
        try:
            await self.client.sign_in(phone, code=code)
        except SessionPasswordNeededError:
            password = input("2FA пароль: ")
            await self.client.sign_in(password=password)
        return True

    async def get_target_user(self, event):
        try:
            if len(event.message.message.split()) > 1:
                username = event.message.message.split()[1].lstrip('@')
                return await self.client.get_entity(username)
            
            if event.is_reply:
                reply_msg = await event.get_reply_message()
                return await reply_msg.get_sender()
                
        except Exception as e:
            print(f"Ошибка получения пользователя: {str(e)}")
            return None

    async def process_command(self, event):
        user = await self.get_target_user(event)
        if not user:
            await event.reply(self.templates['messages'].get('reply_error', '❌ Ошибка'))
            return None
        return user

    def format_last_online(self, last_online):
        if last_online is None:
            return '❌ Неизвестно'
        
        now = datetime.now()
        if isinstance(last_online, datetime):
            time_difference = now - last_online
            if time_difference.days < 1:
                if time_difference.seconds < 60:
                    return "Только что"
                elif time_difference.seconds < 3600:
                    minutes = time_difference.seconds // 60
                    return f"{minutes} минут назад"
                else:
                    hours = time_difference.seconds // 3600
                    return f"{hours} часов назад"
            else:
                return last_online.strftime("%d.%m.%Y %H:%M")  
        else:
            return str(last_online)

    async def process_dox(self, event):
        user = await self.process_command(event)
        if not user:
            return

        try:
            msg = await event.reply(self.templates['dox_steps'][0])
            await asyncio.sleep(2)
            
            if len(self.templates['dox_steps']) > 1:
                await msg.edit(self.templates['dox_steps'][1])
                await asyncio.sleep(2)
            
            username = f"@{user.username}" if user.username else "❌ Нет"
            full_name = getattr(user, 'first_name', '')
            if getattr(user, 'last_name', ''):
                full_name += f" {user.last_name}"

            registration_date = "❌ Неизвестно"
            last_online = self.format_last_online(getattr(user, 'status', None))

            report = self.templates['dox_report'].format(
                full_name=full_name.strip() or '❌ Скрыто',
                user_id=user.id,
                username=username,
                registration_date=registration_date,
                last_online=last_online
            ).strip()

            await msg.edit(report)
            
        except Exception as e:
            await event.reply(f"⚠️ Ошибка: {str(e)}")

    async def process_snos(self, event):
        user = await self.process_command(event)
        if not user:
            return

        try:
            msg = await event.reply(self.templates['snos_steps'][0])
            await asyncio.sleep(3)
            for step in self.templates['snos_steps'][1:]:
                await msg.edit(step)
                await asyncio.sleep(3)
                
        except Exception as e:
            await event.reply(f"⚠️ Ошибка: {str(e)}")

    async def process_love(self, event):

        love_lines = [
            "🤍🤍🤍🤍🤍🤍🤍🤍🤍",
            "🤍🤍❤️❤️🤍❤️❤️🤍🤍",
            "🤍❤️❤️❤️❤️❤️❤️❤️🤍",
            "🤍❤️❤️❤️❤️❤️❤️❤️🤍",
            "🤍❤️❤️❤️❤️❤️❤️❤️🤍",
            "🤍🤍❤️❤️❤️❤️❤️🤍🤍",
            "🤍🤍🤍❤️❤️❤️🤍🤍🤍",
            "🤍🤍🤍🤍❤️🤍🤍🤍🤍",
            "🤍🤍🤍🤍🤍🤍🤍🤍🤍"
        ]
        

        reply_to = event.reply_to_msg_id if event.is_reply else None
        
        message = await event.respond(love_lines[0], reply_to=reply_to)
        current_text = love_lines[0]
        for line in love_lines[1:]:
            await asyncio.sleep(0.5)
            current_text += "\n" + line
            await message.edit(current_text)
    async def process_b(self, event):
        if not event.message.text.startswith('.b '):
            return
        

        text = event.message.text[3:]  
        bold_text = f"**{text}**"
        await event.edit(bold_text, parse_mode='markdown')
        
        
    async def process_help(self, event):
        help_msg = (
            "Pangeya userbot"
            "✨ **Доступные команды** ✨\n\n"
            
            "🔍 **Информация**\n"
            "▫️ `.help` - Показать это меню\n"
            "▫️ `.dox [@юзер]` - Полная информация о пользователе\n"
            "▫️ `.пробив [@юзер]` - Пробив по всем базам\n\n"
            
            "🎭 **Троллинг**\n"
            "▫️ `.trol [@юзер]` - Персональный троллинг\n"
            "▫️ `.ftrol` - Массовый троллинг в чате\n"
            "▫️ `.ntrol` - Остановить весь троллинг\n\n"
            
            "💞 **Романтика**\n"
            "▫️ `.love` - Анимация сердца (ответом на сообщение)\n\n"
            
            "🚀 **Анимации**\n"
            "▫️ `.roket` - Запуск ракеты (ответом на сообщение)\n\n"
            
            "📝 **Текст**\n"
            "▫️ `.b [текст]` - Жирный текст\n"
            "▫️ `.pp [текст]` - Эффект печатной машинки\n\n"
            
            "⚙️ **Другое**\n"
            "▫️ `.svat` - Система свата\n"
            "▫️ `.арбитраж` - Заработок криптовалюты\n"
            "▫️ `.snos [@юзер]` - Полный снос аккаунта\n\n"
            
            "👨💻 **Создатель:** @fuckmorti \n"
            "📢 **Канал:** @vk2o17a"
        )
        await event.reply(help_msg, parse_mode='markdown', link_preview=False)
        
    async def process_pp(self, event):
        if not event.message.text.startswith('.pp '):
            return
        
        text = event.message.text[4:]  
        current_text = ""
        

        await event.edit(".pp")  
        
        for char in text:
            current_text += char
            await event.edit(f".pp {current_text}")
            await asyncio.sleep(0.5)
        

        await event.edit(current_text)
    async def process_roket(self, event):
        steps = [
            "Подготовка к отправке ракеты",
            "5",
            "4",
            "3",
            "2",
            "1",
            "Начинаю запуск, приготовьтесь",
            "Ракета вылетела",
            "💥"
        ]
        

        message = await event.respond(steps[0])
        current_text = steps[0]
        
        for step in steps[1:]:
            await asyncio.sleep(1)
            current_text += "\n" + step
            await message.edit(current_text)

    async def run(self):
        @self.client.on(events.NewMessage())
        async def message_handler(event):
            try:
                msg = event.message
                chat_id = event.chat_id
                sender_id = event.sender_id

                if msg.text and msg.text.startswith((
                    '.trol', '.ntrol', '.ftrol', '.dox', '.snos', 
                    '.svat', '.арбитраж', '.пробив', '.help',
                    '.love', '.b', '.pp', '.roket'
                )):
                    if sender_id != self.owner_id:
                        await event.delete()
                        return

                    command = msg.text.split()[0]
                    
                    if command == '.trol':
                        user = await self.process_command(event)
                        if user:
                            self.active_trolls[chat_id].add(user.id)
                            await event.reply(self.templates['messages'].get('trol_activated', '✅ Троллинг активирован'))
                    
                    elif command == '.ntrol':
                        self.active_trolls[chat_id].clear()
                        self.active_ftrolls.discard(chat_id)
                        await event.reply(self.templates['messages'].get('all_modes_off', '✅ Все режимы деактивированы'))
                    
                    elif command == '.ftrol':
                        self.active_ftrolls.add(chat_id)
                        await event.reply(self.templates['messages'].get('ftrol_activated', '✅ Массовый троллинг активирован'))
                    
                    elif command == '.dox':
                        await self.process_dox(event)
                    
                    elif command == '.snos':
                        await self.process_snos(event)
                    
                    elif command == '.svat':
                        messages = [
                            "Тебе надо было следить за языком 😡",
                            "Ищем номер...🔍",
                            "Совершаем звонок📞",
                            "Всё готово! ✅"
                        ]
                        message = await event.reply(messages[0])
                        await asyncio.sleep(2)
                        await message.edit(messages[1])
                        await asyncio.sleep(2)
                        await message.edit(messages[2])
                        await asyncio.sleep(2)
                        await message.edit(messages[3])
                    
                    elif command == '.арбитраж':
                        n = random.randint(1, 15)
                        await event.reply(
                            f"АЙ ЛЕВ, ТЫ НАФАРМИЛ {n} БАКС(-ОВ) 💸\n"
                            "Так же получил 115 фз 😂"
                        )
                    
                    elif command == '.пробив':
                        user = await self.process_command(event)
                        if not user:
                            return

                        message = await event.reply("😈Начинаю сбор информации, сиди и бойся")
                        await asyncio.sleep(3)
                        
                        report = (
                            f"Пользователь с id {user.id} найден в этих базах данных:\n\n"
                            "База данных MTC 📱\n"
                            "База данных Яндекс 🌐\n"
                            "База данных ГБ 🏛️\n"
                            "База данных 1win 🎰\n"
                            "База данных Uber 🚕\n"
                            "База данных Gmail 📧\n"
                            "База данных МВД и ГУВД 👮♂️\n\n"
                            "🔒Найдены номер, IP и 2 почты 📨"
                        )
                        await message.edit(report)
                    
                    elif command == '.help':
                        await self.process_help(event)
                    
                    elif command == '.love':
                        await self.process_love(event)
                    
                    elif command == '.b':
                        await self.process_b(event)
                    
                    elif command == '.pp':
                        await self.process_pp(event)
                    
                    elif command == '.roket':
                        await self.process_roket(event)

                if sender_id == self.owner_id:
                    return
                if msg.sticker or msg.gif or msg.photo or msg.voice:
                    return

                send_response = False
                if chat_id in self.active_ftrolls:
                    send_response = True
                elif chat_id in self.active_trolls and sender_id in self.active_trolls[chat_id]:
                    send_response = True

                if send_response and msg.text:
                    response = self.get_random_phrase(msg.text)
                    await event.reply(response)

            except Exception as e:
                print(f"Ошибка обработки: {str(e)}")
                
        print(Fore.MAGENTA + banner + Style.RESET_ALL)
        print("\nБот запущен! Команды:")
        print(".trol [@username/реплай] - троллить пользователя")
        print(".ftrol - массовый троллинг")
        print(".ntrol - отключить троллинг")
        print(".dox [@username/реплай] - информация о пользователе")
        print(".snos [@username/реплай] - снос пользователя")
        print(".love - анимация сердечка")
        print(".b [текст] - жирный текст")
        print(".pp [текст] - постепенное появление текста(команда сломана)")
        print(".roket - запуск ракеты (в ответ на сообщение, тоже работает плохо)\n")
        
        await self.client.run_until_disconnected()

async def main():
    bot = TrollBot()
    if await bot.init_client():
        await bot.run()
    else:
        print("Не удалось инициализировать бота")

if __name__ == "__main__":
    asyncio.run(main())