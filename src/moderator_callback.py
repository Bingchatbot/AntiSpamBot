import json
import requests
from replit import db
from utils import url_edit

# функция изменения сообщений у всех модераторов
def edit_admin_message(users_group, 
                       date_message, 
                       text_message, 
                       one_callback, 
                       two_callback = None):
    dict_moderator = db[users_group]["edit_message"][date_message]["moderators"]
    if two_callback is None:
        reply_markup = {"inline_keyboard": 
                        [[{"text": one_callback[0], 
                           "callback_data": one_callback[1]}]]}
    else:
        reply_markup = {"inline_keyboard": 
                        [[{"text": one_callback[0], 
                           "callback_data": one_callback[1]}], 
                         [{"text": two_callback[0], 
                           "callback_data": two_callback[1]}]
                        ]}
    for moderator in dict_moderator:
        response = requests.post(
            url_edit, data = {"chat_id": moderator,
                              "message_id": dict_moderator[moderator][0],
                              "text": text_message,
                              "reply_markup": json.dumps(reply_markup)})
        if response.status_code != 200: 
            print(f'''File "main.py", edit_admin_message, status_code 
            {response.status_code}, response.text = {response.text}''')
    return
