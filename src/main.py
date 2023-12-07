import json
import os
from datetime import datetime
from flask import Flask, request
from replit import db
from utils import send_message, edit_message, delete_message, get_admin, restrict_member, get_chat, send_admin_message, unrestrict_member, ban_member

# создаем сервер
app = Flask(__name__)

WORDS = os.getenv("WORDS", "реклама, работа, crypt, drop")
COUNTS = os.getenv("COUNTS", "10")

@app.route("/")
def home():
    return "Telegram bot @anti_spam_01_bot\nhttps://t.me/antispam_01"

@app.route("/", methods=["POST"])
def webhook():
    # получаем и разбираем сообщение
    data = json.loads(request.data)
    if "message" in data:
        message_id = data["message"]["message_id"]
        from_id = data["message"]["from"]["id"]
        first_name = data["message"]["from"]["first_name"]
        chat_id = data["message"]["chat"]["id"]
        date_message = data["message"]["date"]
        user_id = "user" + str(from_id)
        users_group = "users" + str(chat_id)
        # проверяем, если сообщение не из группы, то останавливаем выполнение кода
        if chat_id == from_id:
            return ""
        # создаем запись для группы в базе данных
        if not db.get(users_group):
            db[users_group] = {}
            db[users_group]["new_user"] = {}
            db[users_group]["left_user"] = {}
            db[users_group]["spam_or_no"] = {}
            db[users_group]["errors"] = {}
        # запись в базу данных и удаление сервисных сообщений
        if data["message"].get("new_chat_participant") is not None:
            db[users_group]["new_user"][date_message] = data["message"]["new_chat_participant"]
            delete_message(chat_id, message_id)
            return ""
        elif data["message"].get("left_chat_participant") is not None:
            db[users_group]["left_user"][date_message] = data["message"]["left_chat_participant"]
            delete_message(chat_id, message_id)
            return ""
        # находим текст в сообщение
        if data["message"].get("text"):
            text = data["message"]["text"]
            # проверяем пользователя на наличие прав админа, а также в базе данных 
            # и если его сообщений больше чем COUNTS, то отключаем бота
            dict_admins = get_admin(chat_id)
            if from_id in dict_admins:
                return ""
            elif user_id in db[users_group]:
                db[users_group][user_id] += 1
                if db[users_group][user_id] > int(COUNTS):
                    return ""
            else:
                db[users_group][user_id] = 1
              
            admin_use_bot = []
            admin_message = ""
            for admin in dict_admins:
                if get_chat(admin):
                    admin_use_bot.append(admin)
                else:
                    admin_message += f'''\n--- Сообщение не отправлено
администратору группы {dict_admins[admin]} ({admin}), так как у него нет чата с ботом'''
            # делаем список из слов в секрете для проверки их в тексте
            words = WORDS.split(', ')
            # ищем слова в тексте, если есть удаляем сообщение и отправляем копию
            for i in range(len(words)):
                if words[i] in text.lower():
                    db[users_group]["spam_or_no"][date_message] = data["message"]
                    delete_message(chat_id, message_id)
                    restrict_member(chat_id, from_id)
                    text_message = f'''Удалено сообщение и ограничены права до проверки модератором пользователя {first_name} ({from_id}) от {datetime.fromtimestamp(date_message).strftime("%d.%m.%Y %H:%M:%S")}\n"{text}"\n'''
                    try:
                        if get_chat(from_id):
                            send_message(from_id, text_message)
                        else:
                            text_message += f'''\n--- Сообщение не отправлено 
пользователю {first_name} ({from_id}), нет чата с ботом'''
                        
                        for i in range(len(admin_use_bot)):
                            send_admin_message(admin_use_bot[i], 
                                               text_message + admin_message,
                                               chat_id,
                                               from_id)
                    except Exception as e:
                        print(f'ERROR {users_group} = {e}')
                    return ""
    # Если сообщение с клавиатуры
    elif "callback_query" in data:
        chat_id_edit = data["callback_query"]["from"]["id"]
        message_id = data["callback_query"]["message"]["message_id"]
        text_edit = data["callback_query"]["message"]["text"] + f'''
        \n{(datetime.now()).strftime("%d.%m.%Y %H:%M:%S")}'''
        try:
            callback_list = data["callback_query"]["data"].split(',')
            if callback_list[0] == "unrestrict_member":
                unrestrict_member(callback_list[1], callback_list[2])
                text_edit += f'''\nСняты ограничения администратором
{data["callback_query"]["from"]["first_name"]} ({chat_id_edit})'''
                edit_message(chat_id_edit, message_id, text_edit)
            elif callback_list[0] == "ban_member":
                ban_member(callback_list[1], callback_list[2])
                text_edit += f'''\nПользователь забанен администратором
{data["callback_query"]["from"]["first_name"]} ({chat_id_edit})'''
                edit_message(chat_id_edit, message_id, text_edit)
        except Exception as e:
            print(f"ERROR callback {chat_id_edit} = {e}")
    return ""
  
if __name__ == "__main__":
    home()
    app.run(host="0.0.0.0", port=80)
