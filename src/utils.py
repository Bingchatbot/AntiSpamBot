import json
import requests
import os


TOKEN = os.environ["TOKEN"]
ID_USER = os.getenv("ID_USER", None)

url_send = "https://api.telegram.org/bot{}/sendMessage".format(TOKEN)
url_edit = "https://api.telegram.org/bot{}/editMessageText".format(TOKEN)
url_delete = "https://api.telegram.org/bot{}/deleteMessage".format(TOKEN)
url_get_admin = "https://api.telegram.org/bot{}/getChatAdministrators".format(TOKEN)
url_user_use_bot = "https://api.telegram.org/bot{}/sendChatAction".format(TOKEN)
url_restrict = "https://api.telegram.org/bot{}/restrictChatMember".format(TOKEN)
url_ban_member = "https://api.telegram.org/bot{}/banChatMember".format(TOKEN)
url_get_moderator = "https://api.telegram.org/bot{}/getChat".format(TOKEN)

# функция отправки сообщения
def send_message(chat_id, text_message):
    response = requests.post(
      url_send, data = {"chat_id": chat_id, "text": text_message}
    )
    if response.status_code != 200: 
        print(f'''File "main.py", send_message, status_code 
        {response.status_code}, response.text = {response.text}''')
    return
# функция изменения сообщения
def edit_message(chat_id, message_id, text_edit):
    response = requests.post(
      url_edit, data = {"chat_id": chat_id, "message_id": message_id, "text": text_edit}
    )
    if response.status_code != 200: 
        print(f'''File "main.py", send_message, status_code 
        {response.status_code}, response.text = {response.text}''')
    return
# функция удаления сообщения
def delete_message(chat_id, message_id):
    response = requests.post(
      url_delete, data = {"chat_id": chat_id, "message_id": message_id}
    )
    if response.status_code != 200: 
        print(f'''File "main.py", delete_message, status_code 
        {response.status_code}, response.text = {response.text}''')
    return
# функция получения словаря из ID_USER
def get_id_moderator():
    dict_id_moderator = {}
    if ID_USER:
        list_admin = ID_USER.split(', ')
        for i in range(len(list_admin)):
            result = get_moderator(list_admin[i])
            if result:
                dict_id_moderator[result['id']] = result['first_name']
    return dict_id_moderator
# функция получения словаря администраторов группы
def get_group_admin(chat_id):
    group_admins = {}
    response = requests.post(
      url_get_admin, data = {"chat_id": chat_id})
    if response.status_code != 200: 
        print(f'''File "main.py", get_group_admin, status_code 
        {response.status_code}, response.text = {response.text}''')
    else:
        data = response.json()
        for admin in data['result']:
            if admin['user']['is_bot']:
                continue
            else:
                group_admins[admin['user']['id']] = admin['user']['first_name']
    return group_admins
# функция ограничения прав пользователя
def restrict_member(chat_id, from_id):
    response = requests.post(
      url_restrict, data = {"chat_id": chat_id, 
                            "user_id": from_id,
                            "permissions": {}
                           }
    )
    if response.status_code != 200: 
        print(f'''File "main.py", restrict_member, status_code 
        {response.status_code}, response.text = {response.text}''')
    return
# функция проверки есть ли чат пользователя с ботом через sendChatAction
def get_user_use_bot(from_id):
    response = requests.post(
      url_user_use_bot, data = {"chat_id": from_id, "action": "typing"}
    )
    if response.status_code != 200: 
        print(f'''File "main.py", user_use_bot, status_code 
        {response.status_code}, response.text = {response.text}''')
        return False
    return True
# функция получения имени модератора из Secrets через getChat
def get_moderator(chat_id):
    response = requests.post(
      url_get_moderator, data = {"chat_id": chat_id}
    )
    if response.status_code != 200: 
        print(f'''File "main.py", get_moderator, status_code 
        {response.status_code}, response.text = {response.text}''')
        return False
    return response.json()['result']
# функция отправки сообщения администратору
def send_admin_message(chat_id, text_message, group_id, user_id):
    unrestrict_member = f"unrestrict_member,{group_id},{user_id}"
    ban_member = f"ban_member,{group_id},{user_id}"
    reply_markup = {"inline_keyboard": 
                    [[{"text": "Отменить ограничение доступа", 
                       "callback_data": unrestrict_member}], 
                     [{"text": "Забанить за спам", 
                       "callback_data": ban_member}]
                    ]}
    response = requests.post(
      url_send, data = {"chat_id": chat_id, 
                        "text": text_message,
                        "reply_markup": json.dumps(reply_markup)
                       }
    )
    if response.status_code != 200: 
        print(f'''File "main.py", send_admin_message, status_code 
        {response.status_code}, response.text = {response.text}''')
    return
# функция отмены ограничения прав пользователя
def unrestrict_member(chat_id, from_id):
    permissions = {"can_send_polls": True,
                   "can_send_other_messages": True,
                   "can_add_web_page_previews": True,
                   "can_change_info": True,
                   "can_invite_users": True,
                   "can_pin_messages": True,
                   "can_manage_topics": True}
    permissions_json = json.dumps(permissions)
    response = requests.post(
      url_restrict, data = {"chat_id": chat_id, 
                            "user_id": from_id,
                            "permissions": permissions_json})
    if response.status_code != 200: 
        print(f'''File "main.py", unrestrict_member, status_code 
        {response.status_code}, response.text = {response.text}''')
    return
# функция полного бана пользователя в группе
def ban_member(chat_id, from_id):
    response = requests.post(
      url_ban_member, data = {"chat_id": chat_id, "user_id": from_id}
    )
    if response.status_code != 200: 
        print(f'''File "main.py", ban_member, status_code 
        {response.status_code}, response.text = {response.text}''')
    return
