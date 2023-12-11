import json
import os
from datetime import datetime
from flask import Flask, request
from replit import db
from utils import send_message, edit_message, delete_message, get_group_admin, restrict_member, get_user_use_bot, send_admin_message, unrestrict_member, ban_member, get_id_moderator, unban_member
from moderator_callback import edit_admin_message


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
            db[users_group]["edit_message"] = {}
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
            group_admins = get_group_admin(chat_id)
            if from_id in group_admins:
                if db[users_group].get(from_id) is not None:
                    db[users_group][user_id] += 1
                else:
                    db[users_group][user_id] = 1
                return ""
            elif user_id in db[users_group]:
                db[users_group][user_id] += 1
                if db[users_group][user_id] > int(COUNTS):
                    return ""
            else:
                db[users_group][user_id] = 1

            moderators = get_id_moderator()
            if not moderators:
                if group_admins:
                    moderators = group_admins
                else:
                    print("ERROR: Словари администраторов и модераторов пусты, бот не проверяет сообщение")
                    return ""
            elif from_id in moderators:
                return ""
              
            admin_use_bot = []
            admin_message = ""
            for admin in moderators:
                if get_chat(admin):
                    admin_use_bot.append(admin)
                else:
                    admin_message += f'''\n--- Сообщение не отправлено
модератору группы {moderators[admin]} ({admin}), так как у него нет чата с ботом'''

            if not admin_use_bot:
                print('ERROR : Нет ни одного чата модератора с ботом, бот не проверяет сообщение')
                return ""
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
                            if result:
                                db[users_group]["edit_message"][date_message] = {"user_restrict": [from_id, result["message_id"]]}
                        else:
                            text_message += f'''\n--- Сообщение не отправлено 
пользователю {first_name} ({from_id}), нет чата с ботом'''
                        
                        for i in range(len(admin_use_bot)):
                            send_admin_message(admin_use_bot[i], 
                                               text_message + admin_message,
                                               users_group,
                                               date_message,
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
            users_group = callback_list[1]
            date_message = callback_list[2]
            group_chat_id = users_group.replace('users', '')
            user_from_id = db[users_group]["edit_message"][date_message]["moderators"][str(chat_id_edit)][1]
            restrict_callback = ["Вернуть ограничение доступа",
                                 f"restrict_member,{users_group},{date_message}"]
            unrestrict_callback = ["Отменить ограничение доступа",
                                   f"unrestrict_member,{users_group},{date_message}"]
            ban_callback = ["Забанить за спам", 
                            f"ban_member,{users_group},{date_message}"]
            unban_callback = ["Отменить бан участника",
                              f"unban_member,{users_group},{date_message}"]
            if callback_list[0] == "unrestrict_member":
                unrestrict_member(group_chat_id, user_from_id)
                text_edit += f'''\nСняты ограничения модератором
{data["callback_query"]["from"]["first_name"]} ({chat_id_edit})'''
                edit_admin_message(users_group, date_message, text_edit,
                                   restrict_callback, ban_callback)
            elif callback_list[0] == "restrict_member":
                restrict_member(group_chat_id, user_from_id)
                text_edit += f'''\nВозвращены ограничения модератором
{data["callback_query"]["from"]["first_name"]} ({chat_id_edit})'''
                edit_admin_message(users_group, date_message, text_edit,
                                   unrestrict_callback, ban_callback)
            elif callback_list[0] == "ban_member":
                ban_member(group_chat_id, user_from_id)
                text_edit += f'''\nПользователь забанен администратором
{data["callback_query"]["from"]["first_name"]} ({chat_id_edit})'''
                edit_admin_message(users_group, date_message, text_edit, unban_callback)
            elif callback_list[0] == "unban_member":
                unban_member(group_chat_id, user_from_id)
                text_edit += f'''\nПользователь разбанен администратором
{data["callback_query"]["from"]["first_name"]} ({chat_id_edit})'''
                edit_admin_message(users_group, date_message, text_edit, ban_callback)
        except Exception as e:
            print(f"ERROR callback {chat_id_edit} = {e}")
    return ""
  
if __name__ == "__main__":
    home()
    app.run(host="0.0.0.0", port=80)
