# AntiSpamBot
Telegram bot @anti_spam_01_bot для удаления спама в группе

Как установить своего бота на replit.com:

1. Регистрируетесь на replit.com

2. Нажимаете кнопку "Create Repl"

3. В новом окне выбираете "Import from GitHub" около "х" справа вверху.

4. Нажимаете "From URL" и вставляете "https://github.com/Bingchatbot/AntiSpamBot":

![alt text](https://github.com/Bingchatbot/AntiSpamBot/blob/main/screenshots/01.png?raw=true)

5. Внизу справа жмете кнопку "Import from GitHub"

6. В окне около "Configure the Run Command" указываете "python src/main.py"

7. После появления вкладки "Console" с текстом "Results of your code will appear here when you Run the project." открываете рядом вкладку "Shell"

8. Запускаете команду "pip install -r requirements.txt" и ждете когда закончатся все установки(внизу должно появится цветное "~/AntiSpamBot$"):

![alt text](https://github.com/Bingchatbot/AntiSpamBot/blob/main/screenshots/02.png?raw=true)

9. Слева на панели "Tools" находите пункт "Secrets"

10. Жмете "New Secret" и в окне "Key" указываете "TOKEN", а в окне "Value" ключ от "@BotFather" из Telegram вида "1234567890:aAbBcCdD=eEfFgGhH+01234"

11. Кнопка "Add Secret" создает необходимый для запуска бота секрет. "WORDS" и "COUNTS" можно исправить в коде под свои требования.

12. Но также можно создать секрет "WORDS" для набора символов (каждый набор символов должен быть разделен запятой и пробелом ", ") по которым бот будет удалять сообщение, сообщать администраторам группы и предлагать дальнейшие действия

13. Секрет "COUNTS" задает количество сообщений пользователя в группе после которого бот не проверяет его текст. Все секреты не видны при выполнении кода!

14. Запускаете код "Run" и в новом окне "Webview" выбираете "DevTools"

15. Затем внизу этого окна нужно найти вкладку "Resources" и прокрутить до "Script", а после скопировать весь https адрес:

![alt text](https://github.com/Bingchatbot/AntiSpamBot/blob/main/screenshots/03.png?raw=true)

16. В любом браузере вводите "https://api.telegram.org/bot1234567890:aAbBcCdD=eEfFgGhH+01234/setWebHook?url=https://antispambot.yourlogin.repl.co/", где 1234567890:aAbBcCdD=eEfFgGhH+01234 заменяете на свой ключ от "@BotFather" из Telegram и после "url=" добавляете данные из 15. вида https://antispambot.yourlogin.repl.co/

17. Переходите по данный ссылке в браузере и после ответа "ok : true" в окне подключаете бота в группу с правами администратора (обязательны "Удаление сообщений" и "Блокировка участников") и затем бот будет обрабатывать все новые сообщения группы (для получения уведомлений о действиях бота, хотя бы у одного администратора должен быть личный чат с ботом)

![alt text](https://github.com/Bingchatbot/AntiSpamBot/blob/main/screenshots/04.png?raw=true)
