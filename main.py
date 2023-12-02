import json
import requests
import os
from flask import Flask, request
from replit import db

# создаем сервер
app = Flask(__name__)

TOKEN = os.environ["TOKEN"]
WORDS = os.environ["WORDS"]
COUNTS = os.environ["COUNTS"]

url_send = "https://api.telegram.org/bot{}/sendMessage".format(TOKEN)
url_edit = "https://api.telegram.org/bot{}/editMessageText".format(TOKEN)
url_delete = "https://api.telegram.org/bot{}/deleteMessage".format(TOKEN)

@app.route("/")
def home():
    return "Telegram bot @anti_spam_01_bot\nhttps://t.me/antispam_01"

@app.route("/", methods=["POST"])
def webhook():
    # получаем и разбираем сообщение в группе
    data = json.loads(request.data)
    if "message" in data:
        message_id = data["message"]["message_id"]
        from_id = data["message"]["from"]["id"]
        first_name = data["message"]["from"]["first_name"]
        chat_id = data["message"]["chat"]["id"]
        date_message = data["message"]["date"]
        user_id = "user" + str(from_id)
        users_group = "users" + str(chat_id)
        # создаем запись для группы в базе данных
        if not db.get(users_group):
            db[users_group] = {} #
            db[users_group]["new_user"] = {}
            db[users_group]["left_user"] = {}
            db[users_group]["spam_or_no"] = {}
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
            # проверяем пользователя базе данных и если его сообщений больше чем COUNTS, то отключаем бота
            if user_id in db[users_group]:
                db[users_group][user_id] += 1
                if db[users_group][user_id] > int(COUNTS):
                    return ""
            else:
                db[users_group][user_id] = 1
            # делаем список из слов в секрете для проверки их в тексте
            words = WORDS.split(', ')
            # ищем слова в тексте, если есть удаляем сообщение и отправляем копию
            for i in range(len(words)):
                if words[i] in text:
                    db[users_group]["spam_or_no"][date_message] = data["message"]
                    delete_message(chat_id, message_id)
                    text_message = f'''
                    Сообщение пользователя {first_name} ({from_id}) 
                    от {date_message} :\n{text}\n\nВ виде данных:\n{data["message"]}'''
                    try:
                        send_message(from_id, text_message)
                    except Exception as e:
                        print(f'ERROR {users_group} = {e}')
                    return ""
                  
    return ""
# функция отправки сообщения
def send_message(chat_id, text_message):
    response = requests.post(
      url_send, data = {"chat_id": chat_id, "text": text_message}
    )
    if response.status_code != 200: 
        print(f'''File "main.py", edit_message, status_code 
        {response.status_code}, response.text = {response.text}''')
    return
# функция удаления сообщения
def delete_message(chat_id, message_id):
    response = requests.post(
      url_delete, data = {"chat_id": chat_id, "message_id": message_id}
    )
    if response.status_code != 200: 
        print(f'File "main.py", delete_message, status_code {response.status_code}')
    return

if __name__ == "__main__":
    home()
    app.run(host="0.0.0.0", port=80)
