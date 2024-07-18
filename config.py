from sqligther import SQLither
import telebot
import time
import traceback

TOKEN = '6036561616:AAEvEZyRfhS9ubze1iKx8acB8Z3iRxXazgg'  # bot token

db = SQLither('newdb.db')  # соединение с бд
bot = telebot.TeleBot(TOKEN)  # токен бота
pas = 'pas'  # пароль для получения статуса администратора
last_click_time = {}
delay_time = 1.5


def delete_message(call):
    try:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    except Exception as e:
        if str(e).startswith("A request to the Telegram API was unsuccessful. Error code: 400. Description: Bad Request: message can't be deleted for everyone"):
            print("Сообщение слишком старое для удаления")
            bot.send_message(chat_id=call.message.chat.id, text="Приносим извинения, бот не может удалить данное сообщение. "
            "Вы можете удалить его самостоятельно, либо вызвать новое сообщение с помощью системных кнопок телеграмма")
        else:
            print("Exception in delete_message")
            print(e)
            traceback.print_exc()


def delay_handler(func):
    def wrapper(call):
        user_id = call.from_user.id
        # Проверяем, прошло ли достаточно времени с момента последнего нажатия
        if user_id in last_click_time and time.time() - last_click_time[user_id] < delay_time:
            bot.delete_message(call.chat.id, call.message_id)
        else:
            # Вызываем оригинальную функцию
            func(call)
            # Запоминаем время последнего нажатия
            last_click_time[user_id] = time.time()
    return wrapper
